# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import pytest

from wd_semantic_parsing.sparql.sparql_to_mrl import sparql_to_mrl


TESTS = (
    ### LC QuAD2 ###
    
    # uid 20258: What country is Mahmoud Abbas the head of state of?
    ('SELECT DISTINCT ?sbj WHERE { ?sbj wdt:P35 wd:Q127998 . ?sbj wdt:P31 wd:Q6256 . }',
     'wd.predicate.wdt:P35(wd:Q127998) & wd.predicate.wdt:P31(wd:Q6256)'),
    
    # uid 7141: As of 2009, how many people lived in Somalia?
    ("SELECT ?obj WHERE { wd:Q1045 p:P1082 ?s . ?s ps:P1082 ?obj . ?s pq:P585 ?x filter(contains(YEAR(?x),'2009')) }",
     'wd.predicate.*ps:P1082(wd.predicate.*p:P1082(wd:Q1045) ^ wd.predicate.pq:P585(wd.operator.year(2009)))'),
    
    # uid 4236,: What nomination did Dolores del Rio receive for their work with La Otra?
    ("SELECT ?obj WHERE { wd:Q124057 p:P1411 ?s . ?s ps:P1411 ?obj . ?s pq:P1686 wd:Q3915489 }",
     'wd.predicate.*ps:P1411(wd.predicate.*p:P1411(wd:Q124057) & wd.predicate.pq:P1686(wd:Q3915489))'),
    
    # uid 2623: In what open cluster is the radius bigger?
    ('select ?ent where { ?ent wdt:P31 wd:Q11387 . ?ent wdt:P2120 ?obj } ORDER BY DESC(?obj)LIMIT 5 ',
     'wd.operator.order_by(wd.predicate.wdt:P31(wd:Q11387), DESC, wd.predicate.wdt:P2120, 5)'),
    
    # uid 23954: Reveal to ME MODE OF TRANSPORT WHOSE NAME HAS THE WORD VEHICLE IN IT?
    ("SELECT DISTINCT ?sbj ?sbj_label WHERE { ?sbj wdt:P31 wd:Q334166 . ?sbj rdfs:label ?sbj_label . FILTER(CONTAINS(lcase(?sbj_label), 'vehicle')) . FILTER (lang(?sbj_label) = 'en') } LIMIT 25 ",
     'wd.predicate.*rdfs:label(wd.predicate.wdt:P31(wd:Q334166)) & wd.operator.label_contains_string("vehicle", "en")'),
    
    # uid 5078: When was the GDP of Rio Grande do Sul1.15e+11 ?
    ("SELECT ?value WHERE { wd:Q40030 p:P2131 ?s . ?s ps:P2131 ?x filter(contains(?x,'1.15e+11')) . ?s pq:P585 ?value}",
     'wd.predicate.*pq:P585(wd.predicate.*p:P2131(wd:Q40030) & wd.operator.contains_value(wd.predicate.ps:P2131, "1.15e+11"))'),
    
    # uid 9547: Where and how did John Denver die?
    ("SELECT ?ans_1 ?ans_2 WHERE { wd:Q105460 wdt:P509 ?ans_1 . wd:Q105460 wdt:P20 ?ans_2 }",
     '[wd.predicate.*wdt:P509(wd:Q105460), wd.predicate.*wdt:P20(wd:Q105460)]'),
    
    # uid 18379: Does cobalt have a time-weighted average exposure limit of .1?
    ("ASK WHERE { wd:Q740 wdt:P2404 ?obj filter(?obj = 0.1) } ",
     'wd.operator.equal(wd.predicate.*wdt:P2404(wd:Q740), 0.1)'),
    
    # uid 1261: How many noble titles does Charles the Bald hold?
    ('SELECT (COUNT(?obj) AS ?value ) { wd:Q71231 wdt:P97 ?obj }',
     'wd.operator.count(wd.predicate.*wdt:P97(wd:Q71231))'),
    
    # uid 5057: On 1/3/1935, what was the location held by Harry S. Truman?
    ("SELECT ?obj WHERE { wd:Q11613 p:P39 ?s . ?s ps:P39 ?obj . ?s pq:P580 ?x filter(contains(YEAR(?x),'1935')) }",
     'wd.predicate.*ps:P39(wd.predicate.*p:P39(wd:Q11613) ^ wd.predicate.pq:P580(wd.operator.year(1935)))'),
    
     # uid 621: Where did Pope Paul VI work, Rome and Munich?
    ("ASK WHERE { wd:Q16975 wdt:P937 wd:Q220 . wd:Q16975 wdt:P937 wd:Q1726 }",
     '[wd.operator.assert(wd:Q16975, wd.predicate.wdt:P937, wd:Q220), wd.operator.assert(wd:Q16975, wd.predicate.wdt:P937, wd:Q1726)]'),
    
    # uid 24144: what is the game name starts with z
    ("SELECT DISTINCT ?sbj ?sbj_label WHERE { ?sbj wdt:P31 wd:Q11410 . ?sbj rdfs:label ?sbj_label . FILTER(STRSTARTS(lcase(?sbj_label), 'z')) . FILTER (lang(?sbj_label) = 'en') } LIMIT 25 ",
     'wd.predicate.*rdfs:label(wd.predicate.wdt:P31(wd:Q11410)) & wd.operator.label_starts_with("z", "en")'),
    
    #### QALD 7 ###
    
    # Does the Isar flow into a lake?
    ("ASK WHERE { wd:Q106588 wdt:P403 ?x_0 . ?x_0 wdt:P31 wd:Q23397 . }",
     'wd.operator.assert(wd.predicate.*wdt:P403(wd:Q106588) & wd.predicate.wdt:P31(wd:Q23397))'),
    
    # How many goals did Pelé score?
    ("SELECT (SUM(?goals) as ?total) WHERE { wd:Q12897 p:P54 ?teamMembership .  ?teamMembership pq:P1351 ?goals . }",
     'wd.operator.sum(wd.predicate.*pq:P1351(wd.predicate.*p:P54(wd:Q12897)))'),
)


@pytest.mark.parametrize("sparql_str, expected_mrl", TESTS)
def test_compile(sparql_str, expected_mrl):
    mrl = sparql_to_mrl(sparql_str)
    assert str(mrl) == expected_mrl
