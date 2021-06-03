# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import logging
from rdflib.term import Variable

from wd_semantic_parsing.mrl.data import MRL, Object, Predicate
from wd_semantic_parsing.sparql.data import SPARQL, SPARQL_SELECT, SPARQL_ASK, ContainsExpr, YearExpr, LiteralExpr, LCaseExpr, RelationalExpr, LangExpr, StrStartsExpr


OPERATORS = {
    '=': 'equal',
    '>': 'greater_than',
    '<': 'less_than'
}


class SparqlCompilerException(Exception): pass


def build_mrl(predicate, arg, reverse=False, ns='wd'):
    mrl = MRL(Predicate(predicate, reverse, ns=ns))
    mrl.args.append(arg)
    return mrl


def operator_mrl(operator_name, args, ns='wd'):
    mrl = MRL(Predicate(ns=ns, ptype='operator', obj=operator_name))
    mrl.args = args
    return mrl


def str_check_mrl(check, str_check, lang, ns='wd'):
    return operator_mrl(check, [f'"{str_check}"', f'"{lang}"'], ns=ns)


def contains_value_mrl(predicate, value, ns='wd'):
    return operator_mrl('contains_value', [str(predicate), f'"{value}"'], ns=ns)


def order_by_mrl(ans, order, predicate, limit_num=None, ns='wd'):
    mrl = operator_mrl('order_by', [ans, order, predicate], ns=ns)
    if limit_num is not None:
        mrl.args.append(limit_num)
    return mrl


def comparison_mrl(operator, compared_mrl, value, ns='wd'):
    return operator_mrl(OPERATORS[operator], [compared_mrl, value], ns=ns)


def compile_year_filter(f, triples, ns='wd'):
    if not isinstance(f, ContainsExpr) or not isinstance(f.arg1, YearExpr) or not isinstance(f.arg2, LiteralExpr):
        return False
    year = operator_mrl('year', [f.arg2.s], ns=ns)
    
    year_node = triples.get_var_name(f.arg1.var)
    year_node.predicate.reverse = False
    temporal_condition = MRL(year_node.predicate)
    temporal_condition.args.append(year)
    
    if len(year_node.args) != 1:
        return False
    fact_node = year_node.args[0]
    
    fact_node.temporal_condition = temporal_condition
    return True


def compile_contains_filter(f, triples, ns='wd'):
    if not isinstance(f, ContainsExpr):
        return False
    
    var = str(f.arg1)
    if var not in triples.vars:
        return False
    
    value_node = triples.get_var_name(var)
    fact_node = value_node.args[0]
    value_node.predicate.reverse = False
    fact_node.conditions.append(contains_value_mrl(value_node.predicate, f.arg2, ns))
    return True


def compile_label_filter(filters, triples):
    f_check = filters[0]
    check = None
    if isinstance(f_check, ContainsExpr):
        check = 'label_contains_string'
    elif isinstance(f_check, StrStartsExpr):
        check = 'label_starts_with'
    if not check or not isinstance(f_check.arg1, LCaseExpr):
        return False
    var_check = f_check.arg1.var
    str_check = f_check.arg2
    
    f_lang = filters[1]
    if not isinstance(f_lang, RelationalExpr) or not isinstance(f_lang.arg1, LangExpr):
        return False
    var_lang = f_lang.arg1.var
    lang = f_lang.arg2
    
    if var_check != var_lang or var_check not in triples.vars:
        return False
    
    label = triples.get_var_name(var_check)
    label.conditions.append(str_check_mrl(check, str_check, lang))
    return True


def compile_filters(filters, triples):
    if len(filters) == 1:
        if compile_year_filter(filters[0], triples):
            return True
        if compile_contains_filter(filters[0], triples):
            return True
    elif len(filters) == 2:
        if compile_label_filter(filters, triples):
            return True
    return False


class Triples:
    def __init__(self):
        self.vars = {}
        self.assertions = []
    
    def add_ref(self, name, mrl):
        if name in self.vars:
            self.vars[name].conditions.append(mrl)
        else:
            self.vars[name] = mrl
    
    def get_var_name(self, var_name):
        if var_name not in self.vars:
            raise SparqlCompilerException(f"'{var_name}' not in {list(self.vars.keys())}")
        return self.vars[var_name]
    
    def get_var(self, v):
        if not (isinstance(v, Variable) and str(v) in self.vars):
            return None
        return self.get_var_name(str(v))
    
    def __str__(self):
        return f'vars: {self.vars}\nassertions: {self.assertions}'


def sparql_to_mrl(sparql_str, ns='wd'):
    query = SPARQL.parse(sparql_str)
    
    triples = Triples()
    for triple in query.triples:
        sbj, pred, obj = triple
        if isinstance(pred, Variable):
            raise SparqlCompilerException("Currently unable to handle variable predicate.")
        
        if isinstance(sbj, Variable):
            if isinstance(obj, Object):
                arg = obj
            else:
                arg = triples.get_var(obj)
            
            if arg is not None:
                triples.add_ref(str(sbj), build_mrl(pred, arg, ns=ns))
        
        if isinstance(obj, Variable):
            if isinstance(sbj, Object):
                arg = sbj
            else:
                arg = triples.get_var(sbj)
            
            if arg is not None:
                triples.add_ref(str(obj), build_mrl(pred, arg, reverse=True, ns=ns))
        
        if not isinstance(sbj, Variable) and not isinstance(obj, Variable):
            triples.assertions.append(operator_mrl('assert', [sbj, Predicate(pred, ns=ns), obj], ns=ns))
    logging.debug(triples)
    
    filters = query.filters
    
    ans = None
    if query.form == SPARQL_SELECT:
        if query.count is not None:
            ans = operator_mrl('count', [triples.get_var_name(query.count)], ns=ns)
        elif query.sum is not None:
            ans = operator_mrl('sum', [triples.get_var_name(query.sum)], ns=ns)
        elif len(query.variables) == 1:
            ans = triples.get_var_name(query.variables[0])
        else:
            ans = []
            for var in query.variables:
                ans.append(triples.get_var_name(var))
            
            # There are queries returning both the entity IDs and their labels, in these cases we can simply return the labels
            if len(ans) == 2:
                for a in ans:
                    if str(a.predicate) == f'{ns}.predicate.*rdfs:label':
                        ans = a
                        break
    
    elif query.form == SPARQL_ASK:
        if len(filters) == 1 and isinstance(filters[0], RelationalExpr):
            comparison = filters[0]
            
            ans = comparison_mrl(comparison.op, triples.get_var_name(str(comparison.arg1)), comparison.arg2)
            filters.pop()
        elif triples.assertions:
            ans = triples.assertions
        elif len(triples.vars) == 1:
            values = list(triples.vars.values())
            ans = operator_mrl('assert', [values[0]], ns=ns)
    else:
        raise SparqlCompilerException(f'Query not supported: {query.form}')
    
    if filters:
        if not compile_filters(filters, triples):
            raise SparqlCompilerException(f'Unable to compile filters: {filters}')
    
    if query.order_by:
        order_by = triples.get_var_name(query.order_by.var)
        order_by.predicate.reverse = False
        ans = order_by_mrl(ans, query.order_by.order, order_by.predicate, query.limit)
    
    return ans
