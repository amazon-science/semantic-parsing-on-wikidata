# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json


def load_json(filepath):
    return json.load(open(filepath))


class TextCleaner:
    def __init__(self, remove_characters):
        self.translation_table = dict.fromkeys(map(ord, remove_characters), None)
    
    def clean(self, text):
        if not text: return ""
        return text.translate(self.translation_table)
