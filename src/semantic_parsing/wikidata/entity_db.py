# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from os import path
import logging

from semantic_parsing.wikidata import WIKIDATA_DIR, WIKIDATA_ENTITIES_WITH_PAGEVIEWS
from semantic_parsing.utils import init_logging, JsonSQLite, get_json_lines, interactive


ENTITIES_PATH = path.join(WIKIDATA_DIR, 'entities.sqlite3')


def build_entity_db():
    logging.info("Building Entity DB")
    with JsonSQLite(ENTITIES_PATH) as db:
        for i, entity in enumerate(get_json_lines(WIKIDATA_ENTITIES_WITH_PAGEVIEWS), 1):
            if i % 100000 == 0:
                db.commit()
                logging.info(f"Processed {i} entities.")
            db.write(entity['id'], entity)
    logging.info("Completed")


def get_entity_db():
    if not path.exists(ENTITIES_PATH):
        build_entity_db()
    
    return JsonSQLite(ENTITIES_PATH)


if __name__ == '__main__':
    init_logging()
    
    entities = get_entity_db()
    
    interactive(lambda line: print(entities.read(line)),
                history_name='entities')
