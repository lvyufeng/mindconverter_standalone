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
from mindinsight.mindconverter.graph_based_converter.constant import ExchangeMessageKeywords, TemplateKeywords
from mindinsight.mindconverter.graph_based_converter.mapper.base import ONNXToMindSporeMapper


class CastMapper(ONNXToMindSporeMapper):
    """Cast mapper."""

    @staticmethod
    def _operation_name_in_ms(*args, **kwargs):
        return "P.Cast"

    @staticmethod
    def _convert_params(**kwargs):
        return dict()

    @staticmethod
    def _convert_trained_weights(**kwargs):
        return dict()

    @staticmethod
    def _generate_snippet_template(**kwargs):
        op = kwargs.get("operation")
        args = kwargs.get("converted_params", dict())
        params = kwargs['raw_params']
        weights = kwargs.get("weights")
        to = params["to"]
        type_dict = {1: 'mindspore.float32',
                     2: 'mindspore.uint8',
                     3: 'mindspore.int8',
                     4: 'mindspore.uint16',
                     5: 'mindspore.int16',
                     6: 'mindspore.int32',
                     7: 'mindspore.int64',
                     8: 'mindspore.string',
                     9: 'mindspore.bool_',
                     10: 'mindspore.float16',
                     11: 'mindspore.double',
                     12: 'mindspore.uint32',
                     13: 'mindspore.uint64',
                     14: 'UNSUPPORTED',
                     15: 'UNSUPPORTED',
                     16: 'UNSUPPORTED'}
        if not op:
            raise ValueError("Can not get MindSpore operation name.")

        args["to"] = type_dict[to]
        variable_slot = "var_0"
        init_template = f"self.{{{variable_slot}}} = {op}()"
        init_to = f"self.{{{variable_slot}}}_to = {{to}}"
        construct_template = f"opt_{{{variable_slot}}} = self.{{{variable_slot}}}" \
                             f"({{{ExchangeMessageKeywords.VariableScope.value.INPUTS.value}}}, " \
                             f"self.{{{variable_slot}}}_to)"
        template = {
            variable_slot: {
                TemplateKeywords.INIT.value: [init_template, init_to],
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
                ExchangeMessageKeywords.VariableScope.value.TRAINABLE_PARAMS.value: dict()
            }
        }
        outputs_list = [f"opt_{{{variable_slot}}}"]
        outputs_mapping = ((0, 0),)
        return template, exchange_msg, outputs_list, outputs_mapping
