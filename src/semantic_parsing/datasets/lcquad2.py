# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import logging
from os import path

from pyparsing import ParseException

from semantic_parsing.datasets.utils import load_json, TextCleaner
from semantic_parsing.sparql.sparql_to_mrl import sparql_to_mrl


class LC_QUAD2:
    """
    GitHub: https://github.com/AskNowQA/LC-QuAD2.0
    Paper: http://jens-lehmann.org/files/2019/iswc_lcquad2.pdf
    """
    def __init__(self, git_checkout):
        self.train_path = path.join(git_checkout, 'dataset', 'train.json')
        self.test_path = path.join(git_checkout, 'dataset', 'test.json')
        
        self.text_cleaner = TextCleaner('{}')
    
    def load_entries(self, test=False):
        for entry in load_json(self.test_path if test else self.train_path):
            yield entry
    
    def preprocess_entries(self, test=False):
        for entry in self.load_entries(test):
            try:
                yield {
                    "uid": entry['uid'],
                    'question': self.text_cleaner.clean(entry['question']),
                    'paraphrased_question': self.text_cleaner.clean(entry['paraphrased_question']),
                    'sparql': entry['sparql_wikidata'],
                    'mrl': sparql_to_mrl(entry['sparql_wikidata']),
                }
            except ParseException as e:
                logging.error(f"Error Parsing: {entry['sparql_wikidata']}:\n{e}")
            except Exception as e:
                logging.error(f"Error Compiling: {entry['sparql_wikidata']}:\n{e}")
                break
