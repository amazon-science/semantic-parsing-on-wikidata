# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from os import path
from collections import defaultdict
import logging

from semantic_parsing.wikidata import WIKIDATA_DIR, WIKIDATA_ENTITIES_WITH_PAGEVIEWS, WIKIMEDIA_DISAMBIGUATION_PAGES
from semantic_parsing.utils import init_logging, JsonSQLite, get_json_lines, interactive


GAZETTEER_PATH = path.join(WIKIDATA_DIR, 'gazetteer.sqlite3')


def build_gazetteer(lang='en', skip_less_than_three_chars=True):
    logging.info("Collecting Denotationals")
    gazetteer = defaultdict(list)
    for i, entity in enumerate(get_json_lines(WIKIDATA_ENTITIES_WITH_PAGEVIEWS), 1):
        if i % 100000 == 0:
            logging.info(f"Processed: {i} entities. {len(gazetteer)} denotationals")
        
        if set(entity['classes']) & WIKIMEDIA_DISAMBIGUATION_PAGES:
            continue
        
        denotationals = set()
        if lang in entity['aliases']:
            for den in entity['aliases'][lang]:
                denotationals.add(den.lower())
        
        if lang in entity['labels']:
            denotationals.add(entity['labels'][lang].lower())
        
        if lang in entity['wiki_title']:
            denotationals.add(entity['wiki_title'][lang].lower())
        
        for denotational in denotationals:
            if skip_less_than_three_chars and len(denotational) < 3:
                continue
            
            gazetteer[denotational].append((entity['pageviews'], entity['id']))
    
    logging.info("Building Gazetteer")
    with JsonSQLite(GAZETTEER_PATH) as db:
        i = 0
        for i, (denotational, entities) in enumerate(gazetteer.items(), 1):
            if i % 100000 == 0:
                db.commit()
                logging.info(f"Processed {i} denotationals.")
            db.write(denotational, [entity for _, entity in sorted(entities, reverse=True)])
        logging.info(f"Gazetteer populated with {i} strings.")


def get_gazetteer(lang='en', skip_less_than_three_chars=True):
    if not path.exists(GAZETTEER_PATH):
        build_gazetteer(lang, skip_less_than_three_chars)
    
    return JsonSQLite(GAZETTEER_PATH)


if __name__ == '__main__':
    init_logging()
    
    gazetteer = get_gazetteer('en')
    
    interactive(lambda line: print(gazetteer.read(line.lower())),
                history_name='gazetteer')
