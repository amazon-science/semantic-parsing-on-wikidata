# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import pytest

from wd_semantic_parsing.mrl.data import MRL
from wd_semantic_parsing.mrl.parser import parse_mrl


TESTS = (
    ('a.b.pred_1(a.b.pred_2(a.b.pred_3(OBJ1)), a.b.pred_4(OBJ2))', MRL),
    ('[a.b.pred_1(OBJ1), a.b.pred_2(OBJ1)]', list),
)


@pytest.mark.parametrize("mrl_str, mrl_type", TESTS)
def test_parser(mrl_str, mrl_type):
    mrl = parse_mrl(mrl_str)
    assert type(mrl) == mrl_type
    assert str(mrl) == mrl_str
