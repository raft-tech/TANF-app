"""Validators for TANF data parser."""

# T1 Category 2 TANF Fatal Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_fatal_edits_sections_1_and_4.pdf

def t1_003(model_obj):
    """Validate stratum."""
    return _get_field_by_item_number(model_obj, '5') > 0 and _get_field_by_item_number(model_obj, '5') < 100

def t1_006(model_obj):
    """Validate report month."""
    month = model_obj.RPT_MONTH_YEAR
    return int(str(month)[0:4]) >= 1998

def t1_007(model_obj):
    """Validate report year."""
    month = model_obj.RPT_MONTH_YEAR
    return int(str(month)[4:6]) >= 1 and int(str(month)[4:6]) <= 12

def t1_008(model_obj):
    """Validate disposition."""
    return model_obj.DISPOSITION in [1, 2]

def t1_010(model_obj):
    """Validate number of family members."""
    return model_obj.NBR_FAMILY_MEMBERS > 0 and model_obj.NBR_FAMILY_MEMBERS < 100

def t1_011(model_obj):
    """Validate family type for work participation."""
    return model_obj.FAMILY_TYPE in [1, 2, 3]

def t1_013(model_obj):
    """Validate recieves subsidiesed child care."""
    return model_obj.RECEIVES_SUB_CC in [1, 2, 3]

# T1 Category 2 TANF Warning Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf

def t1_097(model_obj):
    """Validate funding stream."""
    return model_obj.FUNDING_STREAM in [1, 2]

def t1_099(model_obj):
    """Validate receives subsidized housing."""
    return model_obj.RECEIVES_SUB_HOUSING in [1, 2, 3]

def t1_100(model_obj):
    """Validate receives medical assistance."""
    return model_obj.RECEIVES_MED_ASSISTANCE in [1, 2]

def t1_101(model_obj):
    """Validate receives food stamps."""
    return model_obj.RECEIVES_FOOD_STAMPS in [1, 2]

def t1_102(model_obj):
    """Validate amount of food stamp assistance."""
    return model_obj.AMT_FOOD_STAMP_ASSISTANCE >= 0

def t1_103(model_obj):
    """Validate amount of subsidized child care."""
    return model_obj.AMT_SUB_CC >= 0

def t1_104(model_obj):
    """Validate amount of child support."""
    return model_obj.CHILD_SUPPORT_AMT >= 0

def t1_105(model_obj):
    """Validate amount of family's cash resources."""
    return model_obj.FAMILY_CASH_RESOURCES >= 0

def t1_107(model_obj):
    """Validate cash and cash equivalents."""
    return model_obj.CASH_AMOUNT >= 0 and model_obj.NBR_MONTHS >= 0

def t1_108(model_obj):
    """Validate tanf child care."""
    return model_obj.CC_AMOUNT >= 0 and model_obj.CHILDREN_COVERED >= 0

def t1_110(model_obj):
    """Validate transportation."""
    return model_obj.TRANSP_AMOUNT >= 0 and model_obj.TRANSP_NBR_MONTHS >= 0

def t1_112(model_obj):
    """Validate transitional services."""
    return model_obj.TRANSITION_SERVICES_AMOUNT >= 0 and model_obj.TRANSITION_NBR_MONTHS >= 0

def t1_114(model_obj):
    """Validate other."""
    return model_obj.OTHER_AMOUNT >= 0 and model_obj.OTHER_NBR_MONTHS >= 0

def t1_117(model_obj):
    """Validate reason for & amount of assistance reductions."""
    return model_obj.RECOUPMENT_PRIOR_OVRPMT >= 0

def t1_121(model_obj):
    """Validate waiver evaluation experimental & control groups."""
    return model_obj.WAIVER_EVAL_CONTROL_GRPS in [9, '']

def t1_122(model_obj):
    """Validate is tanf family exempt from federal time limit provisions."""
    return model_obj.FAMILY_EXEMPT_TIME_LIMITS in [1, 2, 3, 4, 6, 7, 8, 9]

def t1_123(model_obj):
    """Validate is tanf family a new child only family."""
    return model_obj.FAMILY_NEW_CHILD in [1, 2]

# T1 Category 3 TANF Fatal Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_fatal_edits_sections_1_and_4.pdf

def t1_004(model_obj):
    """Validate case number."""
    return model_obj.CASE_NUMBER != ''  # TODO not sure how to check a blank char, Is this cat 1?

def t1_009(model_obj):
    """Validate disposition.

    TODO add check for item 1
    """
    if model_obj.DISPOSITION == 2:
        return model_obj.CASE_NUMBER != '' and model_obj.STRATUM != '' and model_obj.RPT_MONTH_YEAR != ''
    return True


# T1 Category 3 TANF Warning Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf


def t1_106(model_obj):
    """Validate cash and cash equivalents."""
    if _get_field_by_item_number(model_obj, '21A') > 0:
        return _get_field_by_item_number(model_obj, '21B') > 0
    return False

def t1_109(model_obj):
    """Validate tanf child care."""
    if model_obj.CC_AMOUNT > 0:
        return model_obj.CHILDREN_COVERED > 0
    return False

def t1_139(model_obj):
    """Validate tanf child care."""
    if model_obj.CC_AMOUNT > 0:
        return model_obj.CC_NBR_MONTHS > 0
    return False

def t1_111(model_obj):
    """Validate transportation."""
    if model_obj.TRANSP_AMOUNT > 0:
        return model_obj.TRANSP_NBR_MONTHS > 0
    return False

def t1_113(model_obj):
    """Validate transitional services."""
    if model_obj.TRANSITION_SERVICES_AMOUNT > 0:
        return model_obj.TRANSITION_NBR_MONTHS > 0
    return False

def t1_115(model_obj):
    """Validate other."""
    if model_obj.OTHER_AMOUNT > 0:
        return model_obj.OTHER_NBR_MONTHS > 0
    return False

def t1_116(model_obj):
    """Validate reason for & amount of assistance reductions."""
    if model_obj.SANC_REDUCTION_AMT > 0:
        return (model_obj.WORK_REQ_SANCTION == 1 or model_obj.WORK_REQ_SANCTION == 2 and
                model_obj.FAMILY_SANC_ADULT == 1 or model_obj.FAMILY_SANC_ADULT == 2 and
                model_obj.SANC_TEEN_PARENT == 1 or model_obj.SANC_TEEN_PARENT == 2 and
                model_obj.NON_COOPERATION_CSE == 1 or model_obj.NON_COOPERATION_CSE == 2 and
                model_obj.FAILURE_TO_COMPLY == 1 or model_obj.FAILURE_TO_COMPLY == 2 and
                model_obj.OTHER_SANCTION == 1 or model_obj.OTHER_SANCTION == 2)
    return False

def t1_118(model_obj):
    """Validate reason for & amount of assistance reductions."""
    if model_obj.OTHER_TOTAL_REDUCTIONS > 0:
        return (model_obj.FAMILY_CAP == 1 or model_obj.FAMILY_CAP == 2 and
                model_obj.REDUCTIONS_ON_RECEIPTS == 1 or model_obj.REDUCTIONS_ON_RECEIPTS == 2 and
                model_obj.OTHER_NON_SANCTION == 1 or model_obj.OTHER_NON_SANCTION == 2)
    return False

def _get_field_by_item_number(model_obj, item_number):
    """Get field name by item number."""
    from .schema_defs.tanf import t1_schema
    for field in t1_schema():
        if field['item_number'] == str(item_number):
            name = field['description']
            return model_obj._meta.get_field(name).value_from_object(model_obj)
    return None
