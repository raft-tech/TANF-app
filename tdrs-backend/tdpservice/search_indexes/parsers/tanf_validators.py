"""Validators for TANF data parser."""

# T1 Category 2 TANF Fatal Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_fatal_edits_sections_1_and_4.pdf

def t1_003(model_obj):
    return model_obj.STRATUM > 0 and model_obj.STRATUM < 100

def t1_006(model_obj):
    month = model_obj.RPT_MONTH_YEAR
    return int(str(month)[0:4]) >= 1998

def t1_007(model_obj):
    month = model_obj.RPT_MONTH_YEAR
    return int(str(month)[4:6]) >= 1 and int(str(month)[4:6]) <= 12

def t1_008(model_obj):
    return model_obj.DISPOSITION in [1 ,2]

def t1_010(model_obj):
    return model_obj.NBR_FAMILY_MEMBERS > 0 and model_obj.NBR_FAMILY_MEMBERS < 100

def t1_011(model_obj):
    '''Validator for family type for work participation.'''
    return model_obj.FAMILY_TYPE in [1, 2, 3]

def t1_013(model_obj):
    '''Validator for recieves subsidiesed child care.'''
    return model_obj.RECEIVES_SUB_CC in [1, 2, 3]

# T1 Category 2 TANF Warning Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf

def t1_097(model_obj):
    '''Validator for funding stream.'''
    return model_obj.FUNDING_STREAM in [1, 2]

def t1_099(model_obj):
    '''Validator for receives subsidized housing.'''
    return model_obj.RECEIVES_SUB_HOUSING in [1, 2, 3]

def t1_100(model_obj):
    '''Validator for receives medical assistance.'''
    return model_obj.RECEIVES_MED_ASSISTANCE in [1, 2]

def t1_101(model_obj):
    '''Validator for receives food stamps.'''
    return model_obj.RECEIVES_FOOD_STAMPS in [1, 2]

def t1_102(model_obj):
    '''Validator for amount of food stamp assistance.'''
    return model_obj.AMT_FOOD_STAMP_ASSISTANCE >= 0

def t1_103(model_obj):
    '''Validator for amount of subsidized child care.'''
    return model_obj.AMT_SUB_CC >= 0

def t1_104(model_obj):
    '''Validator for amount of child support.'''
    return model_obj.CHILD_SUPPORT_AMT >= 0

def t1_105(model_obj):
    '''Validator for amount of family's cash resources.'''
    return model_obj.FAMILY_CASH_RESOURCES >= 0

def t1_121(model_obj):
    '''Validator for waiver evaluation experimental & control groups.'''
    return model_obj.WAIVER_EVAL_CONTROL_GRPS in [9, '']

def t1_122(model_obj):
    '''Validator for is tanf family exempt from federal time limit provisions.'''
    return model_obj.FAMILY_EXEMPT_TIME_LIMITS in [1, 2, 3, 4, 6, 7, 8, 9]

def t1_123(model_obj):
    '''Validator for is tanf family a new child only family.'''
    return model_obj.FAMILY_NEW_CHILD in [1, 2]