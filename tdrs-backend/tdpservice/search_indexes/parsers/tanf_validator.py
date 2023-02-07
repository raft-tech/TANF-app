"""Validators for TANF data parser."""

from .models import ParserError

def t1_003(model_obj):
    return model_obj.stratum > 0 and model_obj.stratum < 100

#TODO ask about ITEM 6? MUST NOT BE BLANK
def t1_004(model_obj):
    """Validates case number."""
    return type(model_obj.case_number) == int

def t1_006(model_obj):
    month = model_obj.reporting_month
    return int(str(month)[0:4]) >= 1998

def t1_007(model_obj):
    month = model_obj.reporting_month
    return int(str(month)[4:6]) >= 1 and int(str(month)[4:6]) <= 12

def t1_008(model_obj):
    return model_obj.disposition in [1 ,2]

# TODO need item 1 from header
# def t1_009(model_obj):
#     if model_obj.disposition == 2:
#         return model_obj.disposition_date != None

def t1_010(model_obj):
    """Validator for num family members."""
    return model_obj.family_size > 0 and model_obj.family_size < 100

def t1_011(model_obj):
    """"Validator for faamioly type for work participation."""
    return model_obj.family_type in [1, 2, 3]

def t1_013(model_obj):
    """Validator for recieves subsidiesed child care."""
    return model_obj.receives_sub_child_care in [1, 2, 3]
