# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import logging
from rdflib.term import Variable

from wd_semantic_parsing.mrl.data import MRL, Predicate
from wd_semantic_parsing.mrl.parser import parse_mrl
from wd_semantic_parsing.sparql.data import SPARQL, SPARQL_ASK, SPARQL_SELECT, ContainsExpr, YearExpr, OrderBy, RelationalExpr, LCaseExpr, LangExpr, StrStartsExpr


COMPARISONS = {
    'equal': '=',
    'greater_than': '>',
    'less_than' : '<'
}
ASK_OPERATORS = {'assert'} | set(COMPARISONS.keys())
LABEL_OPERATORS = {'label_contains_string', 'label_starts_with'}


def assign_var(var_index):
    return Variable(f'x_{var_index}'), var_index + 1


def build_triple(predicate, bound_var, obj):
    if not isinstance(predicate, Predicate):
        predicate = Predicate.parse(str(predicate))
    
    if predicate.reverse:
        return (obj, predicate.obj, bound_var)
    else:
        return (bound_var, predicate.obj, obj)


def compile_mrl(mrl, sparql, bound_var, var_index=0):
    var = Variable(bound_var) if bound_var else None
    logging.debug(f'var: {var}\nmrl: {mrl}')
    
    if mrl.predicate.ptype == 'predicate':
        arg = mrl.args[0]
        if isinstance(arg, MRL):
            obj, var_index = assign_var(var_index)
            compile_mrl(arg, sparql, str(obj), var_index)
        else:
            obj = arg
        sparql.triples.append(build_triple(mrl.predicate, var, obj))
        
        for condition in mrl.conditions:
            if condition.predicate.ptype == 'operator':
                pid = str(condition.predicate.obj)
                if pid == 'label_contains_string':
                    sparql.filters.append(ContainsExpr(LCaseExpr(var), condition.args[0]))
                elif pid == 'label_starts_with':
                    sparql.filters.append(StrStartsExpr(LCaseExpr(var), condition.args[0]))
                elif pid == 'contains_value':
                    obj, var_index = assign_var(var_index)
                    sparql.triples.append(build_triple(condition.args[0], var, obj))
                    sparql.filters.append(ContainsExpr(obj, condition.args[1]))
                
                if pid in LABEL_OPERATORS:
                    # Common features of queries working on labels
                    sparql.filters.append(RelationalExpr(LangExpr(var), '=', condition.args[1]))
                    sparql.distinct = True
                    sparql.limit = 25
            else:
                compile_mrl(condition, sparql, bound_var, var_index)
        
        if mrl.temporal_condition:
            tc = mrl.temporal_condition
            obj, var_index = assign_var(var_index)
            sparql.triples.append(build_triple(tc.predicate, var, obj))
            operator = tc.args[0]
            if str(operator.predicate) == 'wd.operator.year':
                sparql.filters.append(ContainsExpr(YearExpr(obj), f"'{operator.args[0]}'"))
    
    elif mrl.predicate.ptype == 'operator':
        o_id = str(mrl.predicate.obj)
        if o_id == 'count':
            compile_mrl(mrl.args[0], sparql, bound_var, var_index)
            sparql.count = bound_var
        
        if o_id == 'sum':
            compile_mrl(mrl.args[0], sparql, bound_var, var_index)
            sparql.sum = bound_var
        
        elif o_id == 'order_by':
            compile_mrl(mrl.args[0], sparql, bound_var, var_index)
            obj, var_index = assign_var(var_index)
            sparql.triples.append(build_triple(mrl.args[2], var, obj))
            sparql.order_by = OrderBy(obj, mrl.args[1])
            if len(mrl.args) > 3:
                sparql.limit = int(str(mrl.args[3]))
        
        elif o_id in COMPARISONS:
            obj, var_index = assign_var(var_index)
            compile_mrl(mrl.args[0], sparql, obj, var_index)
            sparql.filters.append(RelationalExpr(obj, COMPARISONS[o_id], mrl.args[1]))
        
        elif o_id == 'assert':
            if len(mrl.args) == 1:
                obj, var_index = assign_var(var_index)
                compile_mrl(mrl.args[0], sparql, str(obj), var_index)


def mrl_to_sparql(mrl):
    if isinstance(mrl, str):
        mrl = parse_mrl(mrl)
    
    if isinstance(mrl, MRL):
        ptype, pid = str(mrl.predicate.ptype), str(mrl.predicate.obj)
    else:
        ptype, pid = None, None
    
    if isinstance(mrl, MRL) and ptype == 'operator' and pid in ASK_OPERATORS:
        form = SPARQL_ASK
    else:
        form = SPARQL_SELECT
    sparql = SPARQL(form)
    
    if form == SPARQL_SELECT:
        if type(mrl) == list:
            num_vars = len(mrl)
        else:
            num_vars = 1
        for i in range(num_vars):
            sparql.variables.append(f'ans_{i}')
        
        if  isinstance(mrl, MRL) and ptype == 'operator' and pid == 'count':
            sparql.count = sparql.variables[0]
    
    if type(mrl) == list:
        for i, expr in enumerate(mrl):
            bound_var = None if form == SPARQL_ASK else sparql.variables[i]
            compile_mrl(expr, sparql, bound_var)
    else:
        bound_var = None if form == SPARQL_ASK else sparql.variables[0]
        compile_mrl(mrl, sparql, bound_var)
    
    return sparql
