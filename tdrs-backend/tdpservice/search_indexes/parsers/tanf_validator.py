"""Validators for TANF data parser."""
def t1_006(model_obj):
    month = model_obj.reporting_month
    return int(str(month)[0:4]) >= 1998

def t1_007(model_obj):
    month = model_obj.reporting_month
    return int(str(month)[4:6]) >= 1 and int(str(month)[4:6]) <= 12

def t1_014(model_obj):
    return model_obj.family_affiliation in [1, 2, 3, 4, 5]

def t1_036(model_obj):
    if model_obj.family_affiliation in [2, 3, 4, 5]:
        return model_obj.education_level in [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 98, 99]

def t1_037(model_obj):
    if model_obj.family_affiliation == 1:
        return model_obj.education_level in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 98]

def t1_038(model_obj):
    if model_obj.education_level == None:
        return model_obj.family_affiliation == 5
