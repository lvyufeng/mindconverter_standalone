# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Common configurations for debugger unit testing."""
import json
import os

from google.protobuf import json_format

from mindinsight.datavisual.data_transform.graph import NodeTypeEnum
from mindinsight.debugger.common.utils import NodeBasicInfo
from mindinsight.debugger.proto import ms_graph_pb2
from mindinsight.debugger.stream_handler.graph_handler import GraphHandler
from mindinsight.debugger.stream_handler.watchpoint_handler import WatchpointHitHandler

GRAPH_PROTO_FILE = os.path.join(
    os.path.dirname(__file__), '../../utils/resource/graph_pb/lenet.pb'
)


def get_graph_proto():
    """Get graph proto."""
    with open(GRAPH_PROTO_FILE, 'rb') as f:
        content = f.read()

    graph = ms_graph_pb2.GraphProto()
    graph.ParseFromString(content)

    return graph


def init_graph_handler():
    """Init GraphHandler."""
    graph = get_graph_proto()
    graph_handler = GraphHandler()
    graph_handler.put(graph)

    return graph_handler


def init_watchpoint_hit_handler(value):
    """Init WatchpointHitHandler."""
    wph_handler = WatchpointHitHandler()
    wph_handler.put(value)

    return wph_handler


def get_node_basic_infos(node_names):
    """Get node info according to node names."""
    if not node_names:
        return []
    graph_stream = init_graph_handler()
    node_infos = []
    for node_name in node_names:
        node_type = graph_stream.get_node_type(node_name)
        if node_type == NodeTypeEnum.AGGREGATION_SCOPE.value:
            sub_nodes = graph_stream.get_nodes_by_scope(node_name)
            sub_infos = [NodeBasicInfo(name=node.name, full_name=node.full_name, type=node.type)
                         for node in sub_nodes]
            node_infos.extend(sub_infos)
        full_name = graph_stream.get_full_name(node_name)
        node_infos.append(NodeBasicInfo(name=node_name, full_name=full_name, type=node_type))
    return node_infos


def get_watch_nodes_by_search(watch_nodes):
    """Get watched leaf nodes by search name."""
    watched_leaf_nodes = []
    graph_stream = init_graph_handler()
    for search_name in watch_nodes:
        search_nodes = graph_stream.get_searched_node_list()
        search_node_names = [
            NodeBasicInfo(name=node.name, full_name=node.full_name, type=node.type)
            for node in search_nodes
            if node.name.startswith(search_name)]
        watched_leaf_nodes.extend(search_node_names)

    return watched_leaf_nodes


def mock_tensor_proto():
    """Mock tensor proto."""
    tensor_dict = {
        "node_name":
            "Default/network-WithLossCell/_backbone-LeNet5/relu-ReLU/gradReLU/ReluGradV2-op92",
        "slot": "0"
    }
    tensor_proto = json_format.Parse(json.dumps(tensor_dict), ms_graph_pb2.TensorProto())

    return tensor_proto


def mock_tensor_history():
    """Mock tensor history."""
    tensor_history = {
        "tensor_history": [
            {"name": "Default/TransData-op99:0",
             "full_name": "Default/TransData-op99:0",
             "node_type": "TransData",
             "type": "output",
             "step": 0,
             "dtype": "DT_FLOAT32",
             "shape": [2, 3],
             "has_prev_step": False,
             "value": "click to view"},
            {"name": "Default/args0:0",
             "full_name": "Default/args0:0",
             "node_type": "Parameter",
             "type": "input",
             "step": 0,
             "dtype": "DT_FLOAT32",
             "shape": [2, 3],
             "has_prev_step": False,
             "value": "click to view"}
        ],
        "metadata": {
            "state": "waiting",
            "step": 0,
            "device_name": "0",
            "pos": "0",
            "ip": "127.0.0.1:57492",
            "node_name": "",
            "backend": "Ascend"
        }
    }

    return tensor_history
