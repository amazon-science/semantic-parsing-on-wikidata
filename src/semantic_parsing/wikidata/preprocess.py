# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from semantic_parsing.utils import init_logging
from semantic_parsing.wikidata.dump_entities import extract_entities
from semantic_parsing.wikidata.pageviews import download_pageviews_data
from semantic_parsing.wikidata.merge_entities_pageviews import merge_entities_pageviews
from semantic_parsing.wikidata.gazetteer import build_gazetteer
from semantic_parsing.wikidata.entity_db import build_entity_db


def preprocess(lang='en'):
    # input: WIKIDATA_DUMP_URL
    # output: WIKIDATA_ENTITIES
    extract_entities([lang])
    
    # input: WIKIDATA_PAGEVIEWS_URL
    # output: WIKIDATA_PAGEVIEWS_DIR
    download_pageviews_data(lang)
    
    # input: WIKIDATA_ENTITIES, WIKIDATA_PAGEVIEWS_DIR
    # output: WIKIDATA_ENTITIES_WITH_PAGEVIEWS
    merge_entities_pageviews(lang)
    
    # input: WIKIDATA_ENTITIES_WITH_PAGEVIEWS
    # output: gazetteer.sqlite3
    build_gazetteer(lang)
    
    # input: WIKIDATA_ENTITIES_WITH_PAGEVIEWS
    # output: entities.sqlite3
    build_entity_db()


if __name__ == '__main__':
    init_logging()
    preprocess()
