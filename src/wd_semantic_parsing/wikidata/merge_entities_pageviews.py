# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import logging

from wd_semantic_parsing.wikidata import WIKIDATA_ENTITIES, WIKIDATA_PAGEVIEWS, WIKIDATA_ENTITIES_WITH_PAGEVIEWS
from wd_semantic_parsing.utils import init_logging, get_json_lines, load_dict, JsonEntries


def find_pageviews(pageviews, entity, lang):
    if lang not in entity['wiki_title']:
        return None
    
    page_title = entity['wiki_title'][lang].replace(' ', '_')
    if page_title not in pageviews:
        return None
    
    return pageviews[page_title]


def merge_entities_pageviews(lang='en', skip_missing=True):
    pageviews = load_dict(WIKIDATA_PAGEVIEWS, is_counter=True)
    entities = JsonEntries(WIKIDATA_ENTITIES_WITH_PAGEVIEWS)
    for i, entity in enumerate(get_json_lines(WIKIDATA_ENTITIES), 1):
        if (i % 100000) == 0: logging.info(f"Processed Entities: {i}")
        
        views_num = find_pageviews(pageviews, entity, lang)
        if views_num is not None:
            entity['pageviews'] = views_num
        elif skip_missing:
            continue
        
        entities.save_entry(entity)
    entities.close()


if __name__ == '__main__':
    init_logging()
    merge_entities_pageviews()
