# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from semantic_parsing.sparql.data import Object


class Predicate:
    def __init__(self, obj, reverse=False, ns='wd', ptype='predicate'):
        self.ns = ns
        self.ptype = ptype
        self.obj = obj
        self.reverse = reverse
    
    @staticmethod
    def parse(pred_str):
        tokens = pred_str.split('.')
        if len(tokens) != 3:
            raise Exception('Malformed predicate string: "%s"' % pred_str)
        ns, ptype, pred_id = tokens
        
        if pred_id.startswith('*'):
            reverse = True
            pred_id = pred_id[1:]
        else:
            reverse = False
        obj = Object.parse(pred_id)
        
        return Predicate(obj, reverse, ns, ptype)
    
    def __str__(self):
        reverse = '*' if self.reverse else ''
        return f'{self.ns}.{self.ptype}.{reverse}{self.obj}'


class MRL:
    def __init__(self, predicate=None):
        self.predicate = predicate
        self.args = []
        
        self.conditions = []
        self.temporal_condition = None
    
    def __str__(self):
        s = ['%s(%s)' % (self.predicate, ', '.join(map(str, self.args)))]
        
        if self.conditions:
            for condition in self.conditions:
                s.append("& %s" % str(condition))
        
        if self.temporal_condition:
            s.append("^ %s" % str(self.temporal_condition))
        
        return ' '.join(s)
    
    def __repr__(self):
        return str(self)
