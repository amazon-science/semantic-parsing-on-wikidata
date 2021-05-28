# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from wd_semantic_parsing.wikidata.gazetteer import get_gazetteer
from wd_semantic_parsing.wikidata.entity_db import get_entity_db


class EntityLinker:
    def __init__(self, lang='en'):
        self.gazetteer = get_gazetteer(lang)
        self.entities = get_entity_db()
    
    def link_entity(self, mention, class_name=None, property_name=None):
        candidates = []
        
        for candidate in self.gazetteer.read(mention.strip().lower()):
            if class_name or property_name:
                entity = self.entities.read(candidate)
                if class_name and class_name not in entity['classes']:
                        continue
                if property_name and property_name not in entity['properties']:
                        continue
            candidates.append(candidate)
        
        return candidates
