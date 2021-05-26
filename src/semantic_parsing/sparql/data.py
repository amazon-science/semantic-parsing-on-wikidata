# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""
See SPARQL 1.1 Query Language
https://www.w3.org/TR/2013/REC-sparql11-query-20130321/
"""
from pyparsing import ParseException

from rdflib.plugins.sparql.parser import parseQuery
from rdflib.term import Variable


class Object:
    def __init__(self, name, prefix=None):
        self.name = name
        self.prefix = prefix
    
    @staticmethod
    def parse(obj_str):
        if ':' in obj_str:
            prefix, name = obj_str.split(':')
        else:
            prefix, name = None, obj_str
        return Object(name, prefix)
    
    def __str__(self):
        if self.prefix:
            return f'{self.prefix}:{self.name}'
        return self.name
    
    def __repr__(self):
        return str(self)


def parse_obj(obj):
    if isinstance(obj, Variable):
        return obj
    
    tmp_obj = obj
    while True:
        if 'prefix' in tmp_obj:
            if 'localname' in tmp_obj:
                return Object(tmp_obj['localname'], tmp_obj['prefix'])
            else:
                raise ParseException(f'Missing name for object: {obj}')
        
        if 'part' in tmp_obj:
            tmp_obj = tmp_obj['part']
            continue
        
        if isinstance(tmp_obj, list):
            tmp_obj = tmp_obj[0]
            continue
        
        raise Exception(f"Unable to parse {obj}: {tmp_obj}")


def get_expr(e):
    while isinstance(e, dict) and len(e.keys()) == 1 and 'expr' in e:
        e = e['expr']
    return e


def obj_to_str(obj):
    return f'?{obj}' if isinstance(obj, Variable) else str(obj)


class YearExpr:
    def __init__(self, var):
        self.var = str(var)
    
    def __str__(self):
        return f'YEAR(?{self.var})'


class ContainsExpr:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
    
    def __str__(self):
        return f'CONTAINS({obj_to_str(self.arg1)}, {obj_to_str(self.arg2)})'
    
    def __repr__(self):
        return str(self)


class LiteralExpr:
    def __init__(self, s):
        self.s = str(s)
    
    def __str__(self):
        return self.s


class LangExpr:
    def __init__(self, var):
        self.var = str(var)
    
    def __str__(self):
        return f"LANG(?{self.var})"


class LCaseExpr:
    def __init__(self, var):
        self.var = str(var)
    
    def __str__(self):
        return f"LCASE(?{self.var})"


class StrStartsExpr:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
    
    def __str__(self):
        return f"STRSTARTS({self.arg1}, {self.arg2})"
    
    def __repr__(self):
        return str(self)


class RelationalExpr:
    def __init__(self, arg1, op, arg2):
        self.arg1 = arg1
        self.op = op
        self.arg2 = arg2
    
    def __str__(self):
        return f'{obj_to_str(self.arg1)} {self.op} {obj_to_str(self.arg2)}'
    
    def __repr__(self):
        return str(self)


def parse_expression(e):
    expr = get_expr(e)
    if hasattr(expr, 'name'):
        if expr.name == 'Builtin_CONTAINS':
            return ContainsExpr(parse_expression(expr['arg1']), parse_expression(expr['arg2']))
        elif expr.name == 'Builtin_YEAR':
            return YearExpr(parse_expression(expr['arg']))
        elif expr.name == 'literal':
            return LiteralExpr(expr['string'])
        elif expr.name == 'Builtin_LANG':
            return LangExpr(parse_expression(expr['arg']))
        elif expr.name == 'Builtin_LCASE':
            return LCaseExpr(parse_expression(expr['arg']))
        elif expr.name == 'RelationalExpression':
            return RelationalExpr(parse_expression(expr['expr']), expr['op'], parse_expression(expr['other']))
        elif expr.name == 'Builtin_STRSTARTS':
            return StrStartsExpr(parse_expression(expr['arg1']), parse_expression(expr['arg2']))
    return expr


class OrderBy:
    def __init__(self, var, order):
        self.var = str(var)
        self.order = order
    
    def __str__(self):
        return f'ORDER BY {self.order}(?{self.var})'


SPARQL_SELECT = 'SELECT'
SPARQL_ASK = 'ASK'

QUERY_FORMS = {
    'SelectQuery': SPARQL_SELECT,
    'AskQuery': SPARQL_ASK,
}


class SPARQL:
    """
    This class supports only a subset of SPARQL queries commonly used in Semantic Parsing.
    """
    
    def __init__(self, form=SPARQL_SELECT):
        self.form = form
        self.distinct = False
        self.variables = []
        self.count = None
        self.triples = []
        self.filters = []
        self.order_by = None
        self.limit = None
    
    def __str__(self):
        str_buffer = [self.form]
        
        if self.distinct:
            str_buffer.append('DISTINCT')
        
        if self.count is not None:
            str_buffer.append(f'(COUNT(?{self.count}) AS ?count)')
        else:
            for var in self.variables:
                str_buffer.append(f'?{var}')
        
        str_buffer.append('WHERE {')
        
        for triple in self.triples:
            for obj in triple:
                if isinstance(obj, Variable):
                    str_buffer.append(f'?{obj}')
                else:
                    str_buffer.append(str(obj))
            str_buffer.append('.')
        
        for expr in self.filters:
            str_buffer.append(f'FILTER({expr}) .')
        
        str_buffer.append('}')
        
        if self.order_by is not None:
            str_buffer.append(str(self.order_by))
        
        if self.limit is not None:
            str_buffer.append(f'LIMIT {self.limit}')
        
        return ' '.join(str_buffer)
    
    def __repr__(self):
        return str(self)
    
    @staticmethod
    def parse(sparql_str):
        results = parseQuery(sparql_str)
        assert len(results) == 2
        assert not results[0]
        query = results[1]
        form = QUERY_FORMS[query.name]
        sparql = SPARQL(form)
        sparql.distinct = query.modifier == 'DISTINCT'
        
        if form == SPARQL_SELECT:
            for p in query.projection:
                if len(p) == 1:
                    sparql.variables.append(str(p['var']))
                else:
                    expr = get_expr(p['expr'])
                    if expr.name == 'Aggregate_Count':
                        sparql.count = str(get_expr(expr['vars']))
        
        for part in query.where.part:
            if part.name == 'TriplesBlock':
                for triple in part.triples:
                    sbj, pred, obj = map(parse_obj, triple)
                    sparql.triples.append((sbj, pred, obj))
            elif part.name == 'Filter':
                sparql.filters.append(parse_expression(part))
        
        if 'limitoffset' in query:
            sparql.limit = int(query['limitoffset']['limit'])
        
        if 'orderby' in query:
            order_by = query['orderby']['condition'][0]
            sparql.order_by = OrderBy(get_expr(order_by['expr']), order_by['order'])
        
        return sparql
