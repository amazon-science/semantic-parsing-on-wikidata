# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import pytest

from semantic_parsing.sparql.mrl_to_sparql import mrl_to_sparql


TESTS = (
    ('wd.predicate.wdt:P35(wd:Q127998)',
    'SELECT ?ans_0 WHERE { ?ans_0 wdt:P35 wd:Q127998 . }'),
    
    ('wd.predicate.*ps:P1411(wd.predicate.*p:P1411(wd:Q124057))',
     'SELECT ?ans_0 WHERE { wd:Q124057 p:P1411 ?x_0 . ?x_0 ps:P1411 ?ans_0 . }'),
    
    ('wd.predicate.wdt:P35(wd:Q127998) & wd.predicate.wdt:P31(wd:Q6256)',
     'SELECT ?ans_0 WHERE { ?ans_0 wdt:P35 wd:Q127998 . ?ans_0 wdt:P31 wd:Q6256 . }'),
    
    ('wd.predicate.*ps:P1082(wd.predicate.*p:P1082(wd:Q1045) ^ wd.predicate.pq:P585(wd.operator.year(2009)))',
     "SELECT ?ans_0 WHERE { wd:Q1045 p:P1082 ?x_0 . ?x_0 pq:P585 ?x_1 . ?x_0 ps:P1082 ?ans_0 . FILTER(CONTAINS(YEAR(?x_1), '2009')) . }"),
    
    ('wd.predicate.*ps:P1411(wd.predicate.*p:P1411(wd:Q124057) & wd.predicate.pq:P1686(wd:Q3915489))',
     "SELECT ?ans_0 WHERE { wd:Q124057 p:P1411 ?x_0 . ?x_0 pq:P1686 wd:Q3915489 . ?x_0 ps:P1411 ?ans_0 . }"),
    
    ('wd.operator.order_by(wd.predicate.wdt:P31(wd:Q11387), DESC, wd.predicate.wdt:P2120, 5)',
     'SELECT ?ans_0 WHERE { ?ans_0 wdt:P31 wd:Q11387 . ?ans_0 wdt:P2120 ?x_0 . } ORDER BY DESC(?x_0) LIMIT 5'),
    
    ('wd.predicate.*rdfs:label(wd.predicate.wdt:P31(wd:Q334166)) & wd.operator.label_contains_string("vehicle", "en")',
     'SELECT DISTINCT ?ans_0 WHERE { ?x_0 wdt:P31 wd:Q334166 . ?x_0 rdfs:label ?ans_0 . FILTER(CONTAINS(LCASE(?ans_0), "vehicle")) . FILTER(LANG(?ans_0) = "en") . } LIMIT 25'),
    
    ('wd.predicate.*pq:P515(wd.predicate.*p:P2054(wd:Q283) & wd.operator.contains_value(wd.predicate.ps:P2054, "0.9857"))',
     'SELECT ?ans_0 WHERE { wd:Q283 p:P2054 ?x_0 . ?x_0 ps:P2054 ?x_1 . ?x_0 pq:P515 ?ans_0 . FILTER(CONTAINS(?x_1, "0.9857")) . }'),
    
    ('wd.predicate.*ps:P39(wd.predicate.*p:P39(wd:Q11613) ^ wd.predicate.pq:P580(wd.operator.year(1935)))',
     "SELECT ?ans_0 WHERE { wd:Q11613 p:P39 ?x_0 . ?x_0 pq:P580 ?x_1 . ?x_0 ps:P39 ?ans_0 . FILTER(CONTAINS(YEAR(?x_1), '1935')) . }"),
    
    ('[wd.predicate.*wdt:P509(wd:Q105460), wd.predicate.*wdt:P20(wd:Q105460)]',
     "SELECT ?ans_0 ?ans_1 WHERE { wd:Q105460 wdt:P509 ?ans_0 . wd:Q105460 wdt:P20 ?ans_1 . }"),
    
    ('wd.operator.equal(wd.predicate.*wdt:P2404(wd:Q740), 0.1)',
     "ASK WHERE { wd:Q740 wdt:P2404 ?x_0 . FILTER(?x_0 = 0.1) . }"),
    
    ('wd.operator.count(wd.predicate.*wdt:P97(wd:Q71231))',
     "SELECT (COUNT(?ans_0) AS ?count) WHERE { wd:Q71231 wdt:P97 ?ans_0 . }"),
    
    ('wd.predicate.*rdfs:label(wd.predicate.wdt:P31(wd:Q11410)) & wd.operator.label_starts_with("z", "en")',
     'SELECT DISTINCT ?ans_0 WHERE { ?x_0 wdt:P31 wd:Q11410 . ?x_0 rdfs:label ?ans_0 . FILTER(STRSTARTS(LCASE(?ans_0), "z")) . FILTER(LANG(?ans_0) = "en") . } LIMIT 25'),
)


@pytest.mark.parametrize("mrl_str, expected_sparql", TESTS)
def test_compile(mrl_str, expected_sparql):
    sparql = mrl_to_sparql(mrl_str)
    assert str(sparql) == expected_sparql
