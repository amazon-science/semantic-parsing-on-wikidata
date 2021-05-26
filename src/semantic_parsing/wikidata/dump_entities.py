# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import argparse
import io
import gzip
import json
import logging

from semantic_parsing.wikidata import WIKIDATA_DIR, WIKIDATA_DUMP_URL, WIKIDATA_DUMP_PATH, WIKIDATA_ENTITIES, WIKIMEDIA_DISAMBIGUATION_PAGES
from semantic_parsing.utils import init_logging, JsonEntries, mkdir, wget


def has_path(dct, keys):
    for key in keys:
        if key not in dct:
            return False
        dct = dct[key]
    return True


def extract_entity_data(entry, languages=['en']):
    if has_path(entry, ['claims', 'P31']):
        classes = [class_entry['mainsnak']['datavalue']['value']['id'] for class_entry in entry['claims']['P31']
                          if has_path(class_entry, ['mainsnak', 'datavalue', 'value', 'id'])]
    else:
        classes = []
    
    if set(classes) & WIKIMEDIA_DISAMBIGUATION_PAGES:
        return None
    
    data = {
        'id': entry['id'],
    
        'classes': classes,
        'properties': [],
    
        'wiki_title': {},
        'labels': {},
        'aliases': {},
    }
    
    if has_path(entry, ['claims']):
        data['properties'] = list(entry['claims'].keys())
    
    for lang in languages:
        if has_path(entry, ['sitelinks', '%swiki' % lang, 'title']):
            data['wiki_title'][lang] = entry['sitelinks']['%swiki' % lang]['title']
        
        if has_path(entry, ['labels', lang, 'value']):
            data['labels'][lang] = entry['labels'][lang]['value']
        
        if has_path(entry, ['aliases', lang]):
            data['aliases'][lang] = [alias['value'] for alias in entry['aliases'][lang] if 'value' in alias]
    
    if not data['labels'] and not data['wiki_title'] and not data['aliases']:
        return None
    
    return data


def load_dump(filepath, gzipped=True):
    if gzipped:
        f = gzip.open(filepath)
    else:
        f = io.open(filepath, mode='r')
    
    line_no = 0
    while True:
        try:
            line_no += 1
            if line_no % 100000 == 0:
                logging.info(f"Processed Lines: {line_no}")
            line = f.readline()
            line = line.decode("utf-8").strip().rstrip(',')
            if line == '[': continue
            if line == '': break
            yield json.loads(line)
        except Exception as e:
            logging.error(f"Error loading line {line_no} in: {filepath}\n{e}")


def load_entities(filepath, languages, gzipped=True):
    for entry in load_dump(filepath, gzipped):
        try:
            entity = extract_entity_data(entry, languages)
            if not entity: continue
            yield entity
        except Exception as e:
            logging.error(f"Error loading entity: {entry}\n{e}")


def extract_entities(languages):
    mkdir(WIKIDATA_DIR)
    
    wget(WIKIDATA_DUMP_URL, WIKIDATA_DUMP_PATH)
    
    entities = JsonEntries(WIKIDATA_ENTITIES)
    for entity in load_entities(WIKIDATA_DUMP_PATH, languages):
        entities.save_entry(entity)
    entities.close()
    logging.info("Completed entity extraction.")


if __name__ == '__main__':
    init_logging()
    
    parser = argparse.ArgumentParser("Preprocess Wikidata Dump")
    parser.add_argument('languages', nargs='*', default=['en'])
    args = parser.parse_args()
    
    extract_entities(args.languages)
