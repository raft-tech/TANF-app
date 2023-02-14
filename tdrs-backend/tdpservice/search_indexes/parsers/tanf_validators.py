"""Validators for TANF data parser."""
from cerberus import Validator


class FatalEditWarningsValidator(Validator):
    def _validate_gt(self, constraint, field, value):
        """Validate that value is greater than a constraint."""
        if not value > constraint:
            self._error(field, f"Value: {value}, is not greater than {constraint}.")

    def _validate_lt(self, constraint, field, value):
        """Validate that value is less than a constraint."""
        if not value < constraint:
            self._error(field, f"Value: {value}, is not less than {constraint}.")
        
    def _validate_gte(self, constraint, field, value):
        """Validate that value is greater than or equal to a constraint."""
        if not value >= constraint:
            self._error(field, f"Value: {value}, is not greater than or equal to {constraint}.")

    def _validate_lte(self, constraint, field, value):
        """Validate that value is less than or equal to a constraint."""
        if not value <= constraint:
            self._error(field, f"Value: {value}, is not less than or equal to {constraint}.")

    def _validate_in(self, constraint, field, value):
        """Validate that value is in a list of constraints."""
        if not value in constraint:
            self._error(field, f"Value: {value}, is not in {constraint}.")
        
        

# T1 Category 2 TANF Fatal Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_fatal_edits_sections_1_and_4.pdf

def validate_cat3(name: str, value: str, condition: dict, model_obj) -> tuple:
    """Validate catagoy 2 errors."""
    document = {name: value}
    validator = FatalEditWarningsValidator(condition)
    validator.allow_unknown = True

    condition.pop(name)
    field = list(condition.keys())[0]
    value = getattr(model_obj, field)

    document[field] = value
    validator.validate(document)

    if name in validator.errors.keys():
        return []
    
    return validator.errors

def validate_cat2(name: str, value: str, condition: dict, model_obj) -> tuple:
    """Validate catagoy 2 errors."""
    schema = {name: condition}
    document = {name: value}

    return _validate(schema, document)

def t1_006(model_obj):
    """Validate model_obj.RPT_MONTH_YEAR for year."""
    name = "YEAR value from RPT_MONTH_YEAR"
    value = int(str(model_obj.RPT_MONTH_YEAR)[0:4])
    schema = {name: {'gte': 1998}}
    document = {name: value}

    return _validate(schema, document)

def t1_007(model_obj):
    """Validate model_obj.RPT_MONTH_YEAR for month."""
    name = "MONTH value from RPT_MONTH_YEAR"
    value = int(str(model_obj.RPT_MONTH_YEAR)[4:6])
    schema = {name: {'gte': 1, 'lte': 12}}
    document = {name: value}

    return _validate(schema, document)

def t1_107(model_obj):
    """Validate cash and cash equivalents."""

    schema = {'CASH_AMOUNT': {'gte': 0}, 'NBR_MONTHS': {'gte': 0}}
    document = {'CASH_AMOUNT': model_obj.CASH_AMOUNT, 'NBR_MONTHS': model_obj.NBR_MONTHS}

    return _validate(schema, document)

def t1_116(model_obj):
    """Validate reason for & amount of assistance reductions."""
    schema = {
        'SANC_REDUCTION_AMT': {'gt': 0},
        'WORK_REQ_SANCTION': {'in': [1, 2]},
        'FAMILY_SANC_ADULT': {'in': [1, 2]},
        'SANC_TEEN_PARENT': {'in': [1, 2]},
        'NON_COOPERATION_CSE': {'in': [1, 2]},
        'FAILURE_TO_COMPLY': {'in': [1, 2]},
        'OTHER_SANCTION': {'in': [1, 2]}
    }
    document = {}
    for key in schema.keys():
        document[key] = getattr(model_obj, key)
    
    validator = FatalEditWarningsValidator(schema)
    validator.validate(document)

    if 'SANC_REDUCTION_AMT' in validator.errors.keys():
        return []
    
    return validator.errors


def _get_field_by_item_number(model_obj, item_number):
    """Get field name by item number."""
    from .schema_defs.tanf import t1_schema
    for field in t1_schema():
        if field['item_number'] == str(item_number):
            name = field['description']
            return model_obj._meta.get_field(name).value_from_object(model_obj)
    return None

def _validate(schema, document):
    """Validate the a document."""
    validator = FatalEditWarningsValidator(schema)
    validator.allow_unknown = True
    validator.validate(document)

    return validator.errors

# def t1_003(name, value):
#     """Validate model_obj.STRATUM."""
#     schema = make_field_schema(name, [{'gt': 0, 'lt': 100}])
#     document = make_document(name, value)

#     v = FatalEditWarningsValidator(schema)
#     v.validate(document, schema)
#     return v.errors

# T1 Category 2 TANF Warning Edits
# https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf

# def t1_097(name, value):
#     """Validate funding stream."""
#     schema = make_field_schema(name, [{'contains': [1, 2]}])
#     document = make_document(name, value)

# def t1_115(name, value):
#     """Validate other."""
#     is_valid = True
#     if model_obj.OTHER_AMOUNT > 0:
#         is_valid = model_obj.OTHER_NBR_MONTHS > 0

#     return _check('OTHER_NBR_MONTHS', Cat3, is_valid)


# def t1_008(model_obj):
#     """Validate disposition."""
#     fields_to_check = {'DISPOSITION': model_obj.DISPOSITION in [1, 2]}
#     return _check(fields_to_check, Cat2)

# def t1_010(model_obj):
#     """Validate number of family members."""
#     fields_to_check = {'NBR_FAMILY_MEMBERS': model_obj.NBR_FAMILY_MEMBERS > 0 and model_obj.NBR_FAMILY_MEMBERS < 100}
#     return _check(fields_to_check, Cat2)

# def t1_011(model_obj):
#     """Validate family type for work participation."""
#     fields_to_check = {'FAMILY_TYPE': model_obj.FAMILY_TYPE in [1, 2, 3]}
#     return _check(fields_to_check, Cat2)

# def t1_013(model_obj):
#     """Validate recieves subsidiesed child care."""
#     fields_to_check = {'RECEIVES_SUB_CC': model_obj.RECEIVES_SUB_CC in [1, 2, 3]}
#     return _check(fields_to_check, Cat2)

# # T1 Category 2 TANF Warning Edits
# # https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf

# def t1_097(model_obj):
#     """Validate funding stream."""
#     fields_to_check = {'FUNDING_STREAM': model_obj.FUNDING_STREAM in [1, 2]}
#     return _check(fields_to_check, Cat2)

# def t1_099(model_obj):
#     """Validate receives subsidized housing."""
#     fields_to_check = {'RECEIVES_SUB_HOUSING': model_obj.RECEIVES_SUB_HOUSING in [1, 2, 3]}
#     return _check(fields_to_check, Cat2)

# def t1_100(model_obj):
#     """Validate receives medical assistance."""
#     fields_to_check = {'RECEIVES_MED_ASSISTANCE': model_obj.RECEIVES_MED_ASSISTANCE in [1, 2]}
#     return _check(fields_to_check, Cat2)

# def t1_101(model_obj):
#     """Validate receives food stamps."""
#     fields_to_check = {'RECEIVES_FOOD_STAMPS': model_obj.RECEIVES_FOOD_STAMPS in [1, 2]}
#     return _check(fields_to_check, Cat2)

# def t1_102(model_obj):
#     """Validate amount of food stamp assistance."""
#     fields_to_check = {'AMT_FOOD_STAMP_ASSISTANCE': model_obj.AMT_FOOD_STAMP_ASSISTANCE >= 0}
#     return _check(fields_to_check, Cat2)

# def t1_103(model_obj):
#     """Validate amount of subsidized child care."""
#     fields_to_check = {'AMT_SUB_CC': model_obj.AMT_SUB_CC >= 0}
#     return _check(fields_to_check, Cat2)

# def t1_104(model_obj):
#     """Validate amount of child support."""
#     fields_to_check = {'CHILD_SUPPORT_AMT': model_obj.CHILD_SUPPORT_AMT >= 0}
#     return _check(fields_to_check, Cat2)

# def t1_105(model_obj):
#     """Validate amount of family's cash resources."""
#     fields_to_check = {'FAMILY_CASH_RESOURCES': model_obj.FAMILY_CASH_RESOURCES >= 0}
#     return _check(fields_to_check, Cat2)


# def t1_107(model_obj):
#     """Validate cash and cash equivalents."""
#     fields_to_check={}
#     fields_to_check.update({'CASH_AMOUNT': model_obj.CASH_AMOUNT >= 0})
#     fields_to_check.update({'NBR_MONTHS': model_obj.NBR_MONTHS >= 0})

#     return _check(fields_to_check, Cat2)

# def t1_108(model_obj):
#     """Validate tanf child care."""
#     fields_to_check={}
#     fields_to_check.update({'CC_AMOUNT': model_obj.CC_AMOUNT >= 0})
#     fields_to_check.update({'CHILDREN_COVERED': model_obj.CHILDREN_COVERED >= 0})

#     return _check(fields_to_check, Cat2)

# def t1_110(model_obj):
#     """Validate transportation."""
#     fields_to_check={}
#     fields_to_check.update({'TRANSP_AMOUNT': model_obj.TRANSP_AMOUNT >= 0})
#     fields_to_check.update({'TRANSP_NBR_MONTHS': model_obj.TRANSP_NBR_MONTHS >= 0})

#     return _check(fields_to_check, Cat2)

# def t1_112(model_obj):
#     """Validate transitional services."""
#     fields_to_check = {}
#     fields_to_check.update({'TRANSITION_SERVICES_AMOUNT': model_obj.TRANSITION_SERVICES_AMOUNT >= 0})
#     fields_to_check.update({'TRANSITION_NBR_MONTHS': model_obj.TRANSITION_NBR_MONTHS >= 0})

#     return _check(fields_to_check, Cat2)

# def t1_114(model_obj):
#     """Validate other."""
#     fields_to_check = {}
#     fields_to_check.update({'OTHER_AMOUNT': model_obj.OTHER_AMOUNT >= 0})
#     fields_to_check.update({'OTHER_NBR_MONTHS': model_obj.OTHER_NBR_MONTHS >= 0})

#     return _check(fields_to_check, Cat2)

# def t1_117(model_obj):
#     """Validate reason for & amount of assistance reductions."""
#     fields_to_check = {'RECOUPMENT_PRIOR_OVRPMT': model_obj.RECOUPMENT_PRIOR_OVRPMT >= 0}
#     return _check(fields_to_check, Cat2)
    
# def t1_121(model_obj):
#     """Validate waiver evaluation experimental & control groups."""
#     fields_to_check = {'WAIVER_EVAL_CONTROL_GRPS': model_obj.WAIVER_EVAL_CONTROL_GRPS in [9, '']}
#     return _check(fields_to_check, Cat2)

# def t1_122(model_obj):
#     """Validate is tanf family exempt from federal time limit provisions."""
#     fields_to_check = {'FAMILY_EXEMPT_TIME_LIMITS': model_obj.FAMILY_EXEMPT_TIME_LIMITS in [1, 2, 3, 4, 6, 7, 8, 9]}
#     return _check(fields_to_check, Cat2)

# def t1_123(model_obj):
#     """Validate is tanf family a new child only family."""
#     fields_to_check = {'FAMILY_NEW_CHILD': model_obj.FAMILY_NEW_CHILD in [1, 2]}
#     return _check(fields_to_check, Cat2)

# # T1 Category 3 TANF Fatal Edits
# # https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_fatal_edits_sections_1_and_4.pdf

# def t1_009(model_obj):
#     """Validate disposition.

#     TODO add check for item 1
#     TODO make sure blank char is valid
#     """
#     if model_obj.DISPOSITION == 2:
#         return model_obj.CASE_NUMBER != '' and model_obj.STRATUM != '' and model_obj.RPT_MONTH_YEAR != ''
#     return False


# # T1 Category 3 TANF Warning Edits
# # https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_warning_edits_section_1.pdf


# def t1_106(model_obj):
#     """Validate cash and cash equivalents."""
#     fields_to_check = {}
#     if model_obj.CASH_AMOUNT > 0:
#         fields_to_check = {'NBR_MONTHS': model_obj.NBR_MONTHS > 0}
    
#     return _check(fields_to_check, Cat3, ())

# def t1_109(model_obj):
#     """Validate tanf child care."""
#     is_valid = True
#     if model_obj.CC_AMOUNT > 0:
#         is_valid = model_obj.CHILDREN_COVERED > 0

#     return _check('CHILDREN_COVERED', Cat3, is_valid)

# def t1_139(model_obj):
#     """Validate tanf child care."""
#     is_valid = True
#     if model_obj.CC_AMOUNT > 0:
#         is_valid = model_obj.CC_NBR_MONTHS > 0

#     return _check('CC_NBR_MONTHS', Cat3, is_valid)

# def t1_111(model_obj):
#     """Validate transportation."""
#     is_valid = True
#     if model_obj.TRANSP_AMOUNT > 0:
#         is_valid = model_obj.TRANSP_NBR_MONTHS > 0

#     return _check('TRANSP_NBR_MONTHS', Cat3, is_valid)

# def t1_113(model_obj):
#     """Validate transitional services."""
#     is_valid = True
#     if model_obj.TRANSITION_SERVICES_AMOUNT > 0:
#         is_valid = model_obj.TRANSITION_NBR_MONTHS > 0

#     return _check('TRANSITION_NBR_MONTHS', Cat3, is_valid)

# def t1_115(model_obj):
#     """Validate other."""
#     is_valid = True
#     if model_obj.OTHER_AMOUNT > 0:
#         is_valid = model_obj.OTHER_NBR_MONTHS > 0

#     return _check('OTHER_NBR_MONTHS', Cat3, is_valid)

# def t1_116(model_obj):
#     """Validate reason for & amount of assistance reductions."""
#     exception_group = []
#     fields = ['WORK_REQ_SANCTION',
#               'FAMILY_SANC_ADULT',
#               'SANC_TEEN_PARENT',
#               'NON_COOPERATION_CSE',
#               'FAILURE_TO_COMPLY',
#               'OTHER_SANCTION']
#     if model_obj.SANC_REDUCTION_AMT > 0:
#         if model_obj.WORK_REQ_SANCTION in [1, 2]:
#             exception_group.append(Cat3(fields[0]))
#         if model_obj.FAMILY_SANC_ADULT in [1, 2]:
#             exception_group.append(Cat3(fields[1]))
#         if model_obj.SANC_TEEN_PARENT in [1, 2]:
#             exception_group.append(Cat3(fields[2]))
#         if model_obj.NON_COOPERATION_CSE in [1, 2]:
#             exception_group.append(Cat3(fields[3]))
#         if model_obj.FAILURE_TO_COMPLY in [1, 2]:
#             exception_group.append(Cat3(fields[4]))
#         if model_obj.OTHER_SANCTION in [1, 2]:
#             exception_group.append(Cat3(fields[5]))
    
#     return _check_multiple(fields, Cat3, exception_group)

# def t1_118(model_obj):
#     """Validate reason for & amount of assistance reductions."""
#     exception_group = []
#     fields = ['FAMILY_CAP',
#               'REDUCTIONS_ON_RECEIPTS',
#               'OTHER_NON_SANCTION']
#     if model_obj.OTHER_TOTAL_REDUCTIONS > 0:
#         if model_obj.FAMILY_CAP in [1, 2]:
#             exception_group.append(Cat3(fields[0]))
#         if model_obj.REDUCTIONS_ON_RECEIPTS in [1, 2]:
#             exception_group.append(Cat3(fields[1]))
#         if model_obj.OTHER_NON_SANCTION in [1, 2]:
#             exception_group.append(Cat3(fields[2]))

#     return _check_multiple(fields, Cat3, exception_group)

