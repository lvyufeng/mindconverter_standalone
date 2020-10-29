# Copyright 2020 Huawei Technologies Co., Ltd.All Rights Reserved.
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
"""Define pattern to search."""
scope_name_mapping = {}


class Pattern:
    """Define Pattern object."""

    def __init__(self, pattern, pattern_length, in_degree, out_degree, ptn_items: list = None):
        self.pattern = pattern
        self.count = 0
        self.start_index = []
        self.end_index = []
        self.module_name = None
        self.ptn_length = pattern_length
        self.ptn_items = pattern.split("->") if ptn_items is None else ptn_items
        self.in_degree = in_degree
        self.out_degree = out_degree

    def insert(self, idx, seq_len):
        """
        Insert a new position.

        Args:
            idx (int): Start index.
            seq_len (int): Pattern length.
        """
        if idx in self.start_index:
            return
        self.start_index.append(idx)
        self.end_index.append(idx + seq_len)
        self.count += 1

    def __str__(self):
        """Override `str()` method."""
        return self.__repr__()

    def __repr__(self):
        """Override `repr()` method."""
        return f"Ptn: {self.pattern}[" \
               f"{scope_name_mapping.get(self.pattern, 'Not init')}], " \
               f"count={self.count}"
