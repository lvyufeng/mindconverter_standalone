# Copyright 2021 Huawei Technologies Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Mapper module."""
import numpy as np

from mindinsight.mindconverter.graph_based_converter.constant import WeightType, ExchangeMessageKeywords, \
    TemplateKeywords
from mindinsight.mindconverter.graph_based_converter.mapper.base import ONNXToMindSporeMapper


class SubMapper(ONNXToMindSporeMapper):
    """Sub mapper."""

    @staticmethod
    def _operation_name_in_ms(*args, **kwargs):
        return "P.Sub"

    @staticmethod
    def _convert_params(**kwargs):
        return dict()

    @staticmethod
    def _convert_trained_weights(**kwargs):
        weights = kwargs.get('weights', list())
        tensor = SubMapper._find_val_by_index(0, weights)
        if isinstance(tensor, np.ndarray) and tensor.shape:
            return {'bias': {'data': tensor, 'type': WeightType.PARAMETER.value}}
        return dict()

    @staticmethod
    def _generate_snippet_template(**kwargs):
        template, exchange_msg, outputs_list, outputs_mapping = ONNXToMindSporeMapper._generate_snippet_template(
            **kwargs)
        op = kwargs.get("operation")
        args = kwargs.get("converted_params")
        weights = kwargs.get("weights")
        trainable_params = kwargs.get('trainable_params', dict())
        if not op:
            raise ValueError("Can not get MindSpore operation name.")
        if not weights:
            return template, exchange_msg, outputs_list, outputs_mapping

        tensor = SubMapper._find_val_by_index(0, weights)
        bias_shape = tensor.shape
        bias_dtype = tensor.dtype
        bias_location = SubMapper._find_location_by_index(0, weights)

        variable_slot = "var_0"
        init_template = f"self.{{{variable_slot}}} = {op}()"
        inputs_in_construct = [f"{{{ExchangeMessageKeywords.VariableScope.value.INPUTS.value}}}"]
        if bias_location != -1:
            inputs_in_construct.insert(bias_location, f"self.{{{variable_slot}}}_bias")

        if bias_shape:
            args["bias_shape"] = bias_shape
            args["bias_dtype"] = bias_dtype
            init_tensor = f"self.{{{variable_slot}}}_bias = " \
                          f"Parameter(Tensor(np.random.uniform(0, 1, {{bias_shape}}).astype(np.{{bias_dtype}})), " \
                          f"name=None)"
        else:
            args["bias_value"] = tensor.tolist()
            init_tensor = f"self.{{{variable_slot}}}_bias = {{bias_value}}"

        construct_template = f"opt_{{{variable_slot}}} = self.{{{variable_slot}}}" \
                             f"({', '.join(inputs_in_construct)})"
        template = {
            variable_slot: {
                TemplateKeywords.INIT.value: [init_template, init_tensor],
                TemplateKeywords.CONSTRUCT.value: [construct_template]
            }
        }
        exchange_msg = {
            variable_slot: {
                ExchangeMessageKeywords.VariableScope.value.OPERATION.value: op,
                ExchangeMessageKeywords.VariableScope.value.VARIABLE_NAME.value: None,
                ExchangeMessageKeywords.VariableScope.value.OUTPUT_TYPE.value:
                    ExchangeMessageKeywords.VariableScope.value.TSR_TYPE.value,
                ExchangeMessageKeywords.VariableScope.value.INPUTS.value: [],
                ExchangeMessageKeywords.VariableScope.value.ARGS.value: args,
                ExchangeMessageKeywords.VariableScope.value.WEIGHTS.value: weights,
                ExchangeMessageKeywords.VariableScope.value.TRAINABLE_PARAMS.value: trainable_params
            }
        }
        outputs_list = [f"opt_{{{variable_slot}}}"]
        outputs_mapping = ((0, 0),)
        return template, exchange_msg, outputs_list, outputs_mapping
