# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from os import path
from semantic_parsing import DATA_DIR


WIKIDATA_DUMP_URL = 'https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz'
WIKIDATA_PAGEVIEWS_URL = 'https://dumps.wikimedia.org/other/pageviews/%Y/%Y-%m/'

WIKIDATA_DIR = path.join(DATA_DIR, 'wikidata')
WIKIDATA_DUMP_PATH = path.join(WIKIDATA_DIR, 'latest-all.json.gz')
WIKIDATA_ENTITIES = path.join(WIKIDATA_DIR, 'entities.jsonl')
WIKIDATA_PAGEVIEWS_DIR = path.join(WIKIDATA_DIR, 'pageviews')
WIKIDATA_PAGEVIEWS = path.join(WIKIDATA_DIR, 'pageviews.counts')
WIKIDATA_ENTITIES_WITH_PAGEVIEWS = path.join(WIKIDATA_DIR, 'entities_pageviews.jsonl')

WIKIMEDIA_DISAMBIGUATION_PAGE = 'Q4167410'
WIKIMEDIA_HUMAN_NAME_DISAMBIGUATION_PAGE = 'Q22808320'
WIKIMEDIA_DISAMBIGUATION_PAGES = set([WIKIMEDIA_DISAMBIGUATION_PAGE, WIKIMEDIA_HUMAN_NAME_DISAMBIGUATION_PAGE])
