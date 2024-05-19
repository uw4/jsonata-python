﻿#
# jsonata-java is the JSONata Java reference port
# 
# Copyright Dashjoin GmbH. https://dashjoin.com
# 
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import math
from typing import Any, MutableMapping, MutableSequence

from jsonata import jexception


class Utils:
    class NullValue:
        def __repr__(self):
            return "null"

    NULL_VALUE = NullValue()

    @staticmethod
    def is_numeric(v: Any | None) -> bool:
        if isinstance(v, bool):
            return False
        if isinstance(v, int):
            return True
        is_num = False
        if isinstance(v, float):
            is_num = not math.isnan(v)
            if is_num and not math.isfinite(v):
                raise jexception.JException("D1001", 0, v)
        return is_num

    @staticmethod
    def is_array_of_strings(v: Any | None) -> bool:
        if isinstance(v, list):
            for o in v:
                if not isinstance(o, str):
                    return False
            return True
        return False

    @staticmethod
    def is_array_of_numbers(v: Any | None) -> bool:
        if isinstance(v, list):
            for o in v:
                if not Utils.is_numeric(o):
                    return False
            return True
        return False

    @staticmethod
    def is_function(o: Any | None) -> bool:
        from jsonata import jsonata
        return isinstance(o, (jsonata.Jsonata.JFunction, jsonata.Jsonata.JFunctionCallable))

    NONE = object()

    @staticmethod
    def create_sequence(el: Any | None = NONE) -> list:
        sequence = Utils.JList()
        sequence.sequence = True
        if el is not Utils.NONE:
            if isinstance(el, list) and len(el) == 1:
                sequence.append(el[0])
            else:
                # This case does NOT exist in Javascript! Why?
                sequence.append(el)
        return sequence

    class JList(list):
        sequence: bool
        outer_wrapper: bool
        tuple_stream: bool
        keep_singleton: bool
        cons: bool

        def __init__(self, c=()):
            super().__init__(c)
            self.sequence = False
            self.outer_wrapper = False
            self.tuple_stream = False
            self.keep_singleton = False
            self.cons = False

        # Jsonata specific flags

    @staticmethod
    def is_sequence(result: Any | None) -> bool:
        return isinstance(result, Utils.JList) and result.sequence

    @staticmethod
    def convert_number(n: float) -> float | None:
        # Use long if the number is not fractional
        if not Utils.is_numeric(n):
            return None
        if int(n) == float(n):
            v = int(n)
            if int(v) == v:
                return int(v)
            else:
                return v
        return float(n)

    @staticmethod
    def convert_value(val: Any | None) -> Any | None:
        return val if val is not Utils.NULL_VALUE else None

    @staticmethod
    def convert_dict_nulls(res: MutableMapping[str, Any]) -> None:
        for key, val in res.items():
            v = Utils.convert_value(val)
            if v is not val:
                res[key] = v
            Utils.recurse(val)

    @staticmethod
    def convert_list_nulls(res: MutableSequence[Any]) -> None:
        for i, val in enumerate(res):
            v = Utils.convert_value(val)
            if v is not val:
                res[i] = v
            Utils.recurse(val)

    @staticmethod
    def recurse(val: Any | None) -> None:
        if isinstance(val, dict):
            Utils.convert_dict_nulls(val)
        if isinstance(val, list):
            Utils.convert_list_nulls(val)

    @staticmethod
    def convert_nulls(res: Any | None) -> Any | None:
        Utils.recurse(res)
        return Utils.convert_value(res)