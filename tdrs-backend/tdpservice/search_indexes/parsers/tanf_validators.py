"""Validators for TANF data parser."""

class FatalEditWarnings(Exception):
    """TANF Errors."""

    def __init__(self, field, message):
        """Initialize the error."""
        self.field = field
        self.message = f"{field} {message}"
        super().__init__(self.message)

class Cat2(FatalEditWarnings):
    """TANF Category 2 Errors."""

    def __init__(self, field):
        """Initialize the error."""
        message = "is out of range."
        super().__init__(field, message)

class Cat3(FatalEditWarnings):
    """TANF Category 2 Errors."""

    def __init__(self, field):
        """Initialize the error."""
        message = "is not valid."
        super().__init__(field, message)

def _check(
    fields_to_check: list,
    Catagory: FatalEditWarnings,
    group_description: tuple = ("All fields in this check are invalid.", "Some fields in this check are invalid.")
    ):
    exception_group = []

    for field, is_valid in fields_to_check.items():
        if not is_valid:
            exception_group.add_exception(Catagory(field))

    if len(exception_group) == len(fields_to_check):
        raise ExceptionGroup(group_description[0],
            exception_group)
    elif len(exception_group) > 1:
        raise ExceptionGroup(group_description[1],
            exception_group)
    elif len(exception_group) == 1:
        raise exception_group[0]

    return True


# T1 Category 2 TANF Fatal Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_fatal_edits_sections_1_and_4.pdf

def t1_003(model_obj):
    """Validate model_obj.STRATUM."""
    fields_to_check =  {'STRATUM': model_obj.STRATUM > 0 and model_obj.STRATUM < 100}
    return _check(fields_to_check, Cat2)

def t1_006(model_obj):
    """Validate report month."""
    fields_to_check = {'RPT_MONTH_YEAR': int(str(model_obj.RPT_MONTH_YEAR)[0:4]) >= 1998}
    return _check(fields_to_check, Cat2)

def t1_007(model_obj):
    """Validate report year."""
    fields_to_check = {'RPT_MONTH_YEAR': int(str(model_obj.RPT_MONTH_YEAR)[4:6]) >= 1 and int(str(model_obj.RPT_MONTH_YEAR)[4:6]) <= 12}
    return _check(fields_to_check, Cat2)

def t1_008(model_obj):
    """Validate disposition."""
    fields_to_check = {'DISPOSITION': model_obj.DISPOSITION in [1, 2]}
    return _check(fields_to_check, Cat2)

def t1_010(model_obj):
    """Validate number of family members."""
    fields_to_check = {'NBR_FAMILY_MEMBERS': model_obj.NBR_FAMILY_MEMBERS > 0 and model_obj.NBR_FAMILY_MEMBERS < 100}
    return _check(fields_to_check, Cat2)

def t1_011(model_obj):
    """Validate family type for work participation."""
    fields_to_check = {'FAMILY_TYPE': model_obj.FAMILY_TYPE in [1, 2, 3]}
    return _check(fields_to_check, Cat2)

def t1_013(model_obj):
    """Validate recieves subsidiesed child care."""
    fields_to_check = {'RECEIVES_SUB_CC': model_obj.RECEIVES_SUB_CC in [1, 2, 3]}
    return _check(fields_to_check, Cat2)

# T1 Category 2 TANF Warning Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf

def t1_097(model_obj):
    """Validate funding stream."""
    fields_to_check = {'FUNDING_STREAM': model_obj.FUNDING_STREAM in [1, 2]}
    return _check(fields_to_check, Cat2)

def t1_099(model_obj):
    """Validate receives subsidized housing."""
    fields_to_check = {'RECEIVES_SUB_HOUSING': model_obj.RECEIVES_SUB_HOUSING in [1, 2, 3]}
    return _check(fields_to_check, Cat2)

def t1_100(model_obj):
    """Validate receives medical assistance."""
    fields_to_check = {'RECEIVES_MED_ASSISTANCE': model_obj.RECEIVES_MED_ASSISTANCE in [1, 2]}
    return _check(fields_to_check, Cat2)

def t1_101(model_obj):
    """Validate receives food stamps."""
    fields_to_check = {'RECEIVES_FOOD_STAMPS': model_obj.RECEIVES_FOOD_STAMPS in [1, 2]}
    return _check(fields_to_check, Cat2)

def t1_102(model_obj):
    """Validate amount of food stamp assistance."""
    fields_to_check = {'AMT_FOOD_STAMP_ASSISTANCE': model_obj.AMT_FOOD_STAMP_ASSISTANCE >= 0}
    return _check(fields_to_check, Cat2)

def t1_103(model_obj):
    """Validate amount of subsidized child care."""
    fields_to_check = {'AMT_SUB_CC': model_obj.AMT_SUB_CC >= 0}
    return _check(fields_to_check, Cat2)

def t1_104(model_obj):
    """Validate amount of child support."""
    fields_to_check = {'CHILD_SUPPORT_AMT': model_obj.CHILD_SUPPORT_AMT >= 0}
    return _check(fields_to_check, Cat2)

def t1_105(model_obj):
    """Validate amount of family's cash resources."""
    fields_to_check = {'FAMILY_CASH_RESOURCES': model_obj.FAMILY_CASH_RESOURCES >= 0}
    return _check(fields_to_check, Cat2)


def t1_107(model_obj):
    """Validate cash and cash equivalents."""
    fields_to_check={}
    fields_to_check.update({'CASH_AMOUNT': model_obj.CASH_AMOUNT >= 0})
    fields_to_check.update({'NBR_MONTHS': model_obj.NBR_MONTHS >= 0})

    return _check(fields_to_check, Cat2)

def t1_108(model_obj):
    """Validate tanf child care."""
    fields_to_check={}
    fields_to_check.update({'CC_AMOUNT': model_obj.CC_AMOUNT >= 0})
    fields_to_check.update({'CHILDREN_COVERED': model_obj.CHILDREN_COVERED >= 0})

    return _check(fields_to_check, Cat2)

def t1_110(model_obj):
    """Validate transportation."""
    fields_to_check={}
    fields_to_check.update({'TRANSP_AMOUNT': model_obj.TRANSP_AMOUNT >= 0})
    fields_to_check.update({'TRANSP_NBR_MONTHS': model_obj.TRANSP_NBR_MONTHS >= 0})

    return _check(fields_to_check, Cat2)

def t1_112(model_obj):
    """Validate transitional services."""
    fields_to_check = {}
    fields_to_check.update({'TRANSITION_SERVICES_AMOUNT': model_obj.TRANSITION_SERVICES_AMOUNT >= 0})
    fields_to_check.update({'TRANSITION_NBR_MONTHS': model_obj.TRANSITION_NBR_MONTHS >= 0})

    return _check(fields_to_check, Cat2)

def t1_114(model_obj):
    """Validate other."""
    fields_to_check = {}
    fields_to_check.update({'OTHER_AMOUNT': model_obj.OTHER_AMOUNT >= 0})
    fields_to_check.update({'OTHER_NBR_MONTHS': model_obj.OTHER_NBR_MONTHS >= 0})

    return _check(fields_to_check, Cat2)

def t1_117(model_obj):
    """Validate reason for & amount of assistance reductions."""
    fields_to_check = {'RECOUPMENT_PRIOR_OVRPMT': model_obj.RECOUPMENT_PRIOR_OVRPMT >= 0}
    return _check(fields_to_check, Cat2)
    
def t1_121(model_obj):
    """Validate waiver evaluation experimental & control groups."""
    fields_to_check = {'WAIVER_EVAL_CONTROL_GRPS': model_obj.WAIVER_EVAL_CONTROL_GRPS in [9, '']}
    return _check(fields_to_check, Cat2)

def t1_122(model_obj):
    """Validate is tanf family exempt from federal time limit provisions."""
    fields_to_check = {'FAMILY_EXEMPT_TIME_LIMITS': model_obj.FAMILY_EXEMPT_TIME_LIMITS in [1, 2, 3, 4, 6, 7, 8, 9]}
    return _check(fields_to_check, Cat2)

def t1_123(model_obj):
    """Validate is tanf family a new child only family."""
    fields_to_check = {'FAMILY_NEW_CHILD': model_obj.FAMILY_NEW_CHILD in [1, 2]}
    return _check(fields_to_check, Cat2)

# T1 Category 3 TANF Fatal Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_fatal_edits_sections_1_and_4.pdf

def t1_009(model_obj):
    """Validate disposition.

    TODO add check for item 1
    TODO make sure blank char is valid
    """
    if model_obj.DISPOSITION == 2:
        return model_obj.CASE_NUMBER != '' and model_obj.STRATUM != '' and model_obj.RPT_MONTH_YEAR != ''
    return False


# T1 Category 3 TANF Warning Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf


def t1_106(model_obj):
    """Validate cash and cash equivalents."""
    fields_to_check = {}
    if model_obj.CASH_AMOUNT > 0:
        fields_to_check = {'NBR_MONTHS': model_obj.NBR_MONTHS > 0}
    
    return _check(fields_to_check, Cat3, ())

def t1_109(model_obj):
    """Validate tanf child care."""
    is_valid = True
    if model_obj.CC_AMOUNT > 0:
        is_valid = model_obj.CHILDREN_COVERED > 0

    return _check('CHILDREN_COVERED', Cat3, is_valid)

def t1_139(model_obj):
    """Validate tanf child care."""
    is_valid = True
    if model_obj.CC_AMOUNT > 0:
        is_valid = model_obj.CC_NBR_MONTHS > 0

    return _check('CC_NBR_MONTHS', Cat3, is_valid)

def t1_111(model_obj):
    """Validate transportation."""
    is_valid = True
    if model_obj.TRANSP_AMOUNT > 0:
        is_valid = model_obj.TRANSP_NBR_MONTHS > 0

    return _check('TRANSP_NBR_MONTHS', Cat3, is_valid)

def t1_113(model_obj):
    """Validate transitional services."""
    is_valid = True
    if model_obj.TRANSITION_SERVICES_AMOUNT > 0:
        is_valid = model_obj.TRANSITION_NBR_MONTHS > 0

    return _check('TRANSITION_NBR_MONTHS', Cat3, is_valid)

def t1_115(model_obj):
    """Validate other."""
    is_valid = True
    if model_obj.OTHER_AMOUNT > 0:
        is_valid = model_obj.OTHER_NBR_MONTHS > 0

    return _check('OTHER_NBR_MONTHS', Cat3, is_valid)

def t1_116(model_obj):
    """Validate reason for & amount of assistance reductions."""
    exception_group = []
    fields = ['WORK_REQ_SANCTION',
              'FAMILY_SANC_ADULT',
              'SANC_TEEN_PARENT',
              'NON_COOPERATION_CSE',
              'FAILURE_TO_COMPLY',
              'OTHER_SANCTION']
    if model_obj.SANC_REDUCTION_AMT > 0:
        if model_obj.WORK_REQ_SANCTION in [1, 2]:
            exception_group.append(Cat3(fields[0]))
        if model_obj.FAMILY_SANC_ADULT in [1, 2]:
            exception_group.append(Cat3(fields[1]))
        if model_obj.SANC_TEEN_PARENT in [1, 2]:
            exception_group.append(Cat3(fields[2]))
        if model_obj.NON_COOPERATION_CSE in [1, 2]:
            exception_group.append(Cat3(fields[3]))
        if model_obj.FAILURE_TO_COMPLY in [1, 2]:
            exception_group.append(Cat3(fields[4]))
        if model_obj.OTHER_SANCTION in [1, 2]:
            exception_group.append(Cat3(fields[5]))
    
    return _check_multiple(fields, Cat3, exception_group)

def t1_118(model_obj):
    """Validate reason for & amount of assistance reductions."""
    exception_group = []
    fields = ['FAMILY_CAP',
              'REDUCTIONS_ON_RECEIPTS',
              'OTHER_NON_SANCTION']
    if model_obj.OTHER_TOTAL_REDUCTIONS > 0:
        if model_obj.FAMILY_CAP in [1, 2]:
            exception_group.append(Cat3(fields[0]))
        if model_obj.REDUCTIONS_ON_RECEIPTS in [1, 2]:
            exception_group.append(Cat3(fields[1]))
        if model_obj.OTHER_NON_SANCTION in [1, 2]:
            exception_group.append(Cat3(fields[2]))

    return _check_multiple(fields, Cat3, exception_group)

def _get_field_by_item_number(model_obj, item_number):
    """Get field name by item number."""
    from .schema_defs.tanf import t1_schema
    for field in t1_schema():
        if field['item_number'] == str(item_number):
            name = field['description']
            return model_obj._meta.get_field(name).value_from_object(model_obj)
    return None
