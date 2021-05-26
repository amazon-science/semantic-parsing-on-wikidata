# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from semantic_parsing.mrl.data import MRL, Predicate, Object

class MRL_ParsingException(Exception): pass


DEBUG = False
def debug_info(depth, msg):
    if not DEBUG: return
    print("%s%s" % ("    " * depth, msg))


EXP_START, MRL_OBJ, MRL_STR, STRING_START, VAR_OR_PRED = 0, 1, 2, 3, 4
def parse_mrl_obj(text, i=0, depth=0, gobble_operator=True):
    # The following state machine either:
    # - return a Object
    # - return a String
    # - return a Variable
    # - return None
    # - initialise an MRL predicate
    mrl, state = None, EXP_START
    square_brakets = 0
    while i < len(text):
        c = text[i]
        
        if state == EXP_START:
            start_obj = i
            if c.isspace():
                pass
            elif c == '[':
                square_brakets += 1
                state = MRL_OBJ
            elif c == '"':
                state = STRING_START
            elif c == ')':
                return None, i
            else:
                state = VAR_OR_PRED
        
        elif state == MRL_OBJ:
            if c == '"':
                state = MRL_STR
            elif c == '[':
                square_brakets += 1
            elif c == ']':
                square_brakets -= 1
                if square_brakets == 0:
                    # Return TKQL object, including final square bracket
                    return Object.parse(text[start_obj:i+1].strip()), i+1
        
        elif state == MRL_STR:
            if c == '"':
                state = MRL_OBJ
        
        elif state == STRING_START:
            if c == '"':
                # Return String, including the quotation marks
                return text[start_obj:i+1], i+1
        
        elif state == VAR_OR_PRED:
            if c == '(':
                mrl = MRL()
                mrl.predicate = Predicate.parse(text[start_obj:i])
                break
            
            # Return Variable
            elif c in {',', ')'}:
                return Object.parse(text[start_obj:i].strip()), i
            elif i+1 == len(text):
                return Object.parse(text[start_obj:i+1].strip()), i+1
        
        i += 1
    
    if not mrl:
        raise MRL_ParsingException("Unexpected end of the expression: %s" % text)
    
    debug_info(depth, 'PREDICATE: %s    -> "%s"' % (mrl.predicate, text[i:]))
    depth += 1
    
    # Arguments
    while i < len(text):
        c = text[i]
        if c == ')':
            i += 1
            break
        
        elif c in {'(', ','}:
            arg, i = parse_mrl_obj(text, i+1, depth)
            if arg:
                mrl.args.append(arg)
                debug_info(depth, 'ARG: %s (type: %s)    -> "%s"' % (arg, type(arg), text[i:]))
            
            if isinstance(arg, MRL) and i < len(text) and text[i] == ')':
                i += 1
                break
        
        else:
            i += 1
    
    # Operators
    # By default, all the operators apply to the first MRL node in the chain.
    # Example: mrl.pred.a([obj1]) & mrl.pred.b([obj2]) & mrl.pred.b([obj3])
    # By definition, in the above expression the condition "mrl.pred.b([obj3])"
    # applies to "mrl.pred.a([obj1])" and not to "mrl.pred.b([obj2])"
    if not gobble_operator:
        return mrl, i
    
    while i < len(text):
        c = text[i]
        if c in {',', ')'}:
            break
        
        elif c == '&':
            condition, i = parse_mrl_obj(text, i+1, depth, gobble_operator=False)
            mrl.conditions.append(condition)
        
        elif c == '^':
            condition, i = parse_mrl_obj(text, i+1, depth, gobble_operator=False)
            if mrl.temporal_condition:
                raise MRL_ParsingException("We can express only one temporal condition: %s" % text)
            mrl.temporal_condition = condition
        
        else:
            i += 1
    
    return mrl, i


def parse_mrl_expr(text: str):
    obj, i = parse_mrl_obj(text)
    return obj, text[i:].strip()


def parse_mrl(text: str):
    if text.startswith('['):
        mrl = []
        while True:
            obj, not_parsed = parse_mrl_expr(text[1:])
            mrl.append(obj)
            if not not_parsed.startswith(','):
                break
            text = not_parsed
    else:
        mrl, not_parsed = parse_mrl_expr(text)
        if not_parsed:
            raise MRL_ParsingException('MRL: "%s"\nPart of the expression was not parsed: "%s"' % (text, not_parsed))
    return mrl
