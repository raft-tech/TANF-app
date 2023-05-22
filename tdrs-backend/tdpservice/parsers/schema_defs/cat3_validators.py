"""Collection of category three validators for TANF Section 1 records."""


from .. import validators


def validate_disposition(record):
    """Validate that dispotion and it's dependent fields."""
    disposition = getattr(record, "DISPOSITION")
    if disposition == 2:
        items = ["COUNTY_FIPS_CODE", "RPT_MONTH_YEAR", "STRATUM", "CASE_NUMBER"]
        validator = validators.notEmpty()
        for item in items:
            item_value = getattr(record, item)
            validator_is_valid, validator_error = validator(str(item_value))
            if not validator_is_valid:
                return (False, "FATAL: IF ITEM 9 = 2, THEN ITEMS 1,4-6 MUST NOT BE BLANK")
    return (True, None)


def validate_cash_amount_and_nbr_months(record):
    """Validate cash and cash equivalents dependencies."""
    cash_amount = getattr(record, "CASH_AMOUNT")
    nbr_months = getattr(record, "NBR_MONTHS")

    if cash_amount == 0 and nbr_months < 0:
        return (False, "WARNING: ITEM 21A AND ITEM 21B MUST => 0")

    if cash_amount > 0 and nbr_months <= 0:
        return (False, "WARNING: IF ITEM 21A > 0, ITEM 21B MUST > 0")

    return (True, None)


def validate_child_care(record):
    """Validate child care dependencies."""
    cc_amount = getattr(record, "CC_AMOUNT")
    children_covered = getattr(record, "CHILDREN_COVERED")
    cc_nbr_months = getattr(record, "CC_NBR_MONTHS")

    if cc_amount == 0 and children_covered < 0:
        return (False, "WARNING: ITEM 22A AND ITEM 22B MUST => 0")

    if cc_amount > 0 and children_covered <= 0 and cc_nbr_months <= 0:
        return (False, "WARNING: IF ITEM 22A > 0, ITEM 22B MUST > 0, ITEM 22C MUST > 0")

    return (True, None)


def validate_transportation(record):
    """Validate transportation dependencies."""
    transp_amount = getattr(record, "TRANSP_AMOUNT")
    transp_nbr_months = getattr(record, "TRANSP_NBR_MONTHS")

    if transp_amount == 0 and transp_nbr_months < 0:
        return (False, "WARNING: ITEM 23A AND ITEM 23B MUST => 0")

    if transp_amount > 0 and transp_nbr_months <= 0:
        return (False, "WARNING: IF ITEM 23A > 0, ITEM 23B MUST > 0")

    return (True, None)


def validate_transitional_services(record):
    """Validate transitional services dependencies."""
    trans_svc_amount = getattr(record, "TRANSITION_SERVICES_AMOUNT")
    trans_nbr_months = getattr(record, "TRANSITION_NBR_MONTHS")

    if trans_svc_amount == 0 and trans_nbr_months < 0:
        return (False, "WARNING: ITEM 24A AND ITEM 24B MUST => 0")

    if trans_svc_amount > 0 and trans_nbr_months <= 0:
        return (False, "WARNING: IF ITEM 24A > 0, ITEM 24B MUST > 0")

    return (True, None)


def validate_other(record):
    """Validate other dependencies."""
    other_amount = getattr(record, "OTHER_AMOUNT")
    other_nbr_months = getattr(record, "OTHER_NBR_MONTHS")

    if other_amount == 0 and other_nbr_months < 0:
        return (False, "WARNING: ITEM 25A AND ITEM 25B MUST => 0")

    if other_amount > 0 and other_nbr_months <= 0:
        return (False, "WARNING: IF ITEM 25A > 0, ITEM 25B MUST > 0")

    return (True, None)


def validate_reasons_for_amount_of_assistance_reductions(record):
    """Validate assistance reduction dependencies."""
    sanc_reduction_amount = getattr(record, "SANC_REDUCTION_AMT")
    work_req_sanction = getattr(record, "WORK_REQ_SANCTION")
    family_sanc_adult = getattr(record, "FAMILY_SANC_ADULT")
    sanc_teen_parent = getattr(record, "SANC_TEEN_PARENT")
    non_cooperation_case = getattr(record, "NON_COOPERATION_CSE")
    failure_to_comply = getattr(record, "FAILURE_TO_COMPLY")
    other_sanction = getattr(record, "OTHER_SANCTION")
    other_total_reductions = getattr(record, "OTHER_TOTAL_REDUCTIONS")
    family_cap = getattr(record, "FAMILY_CAP")
    reductions_on_receipts = getattr(record, "REDUCTIONS_ON_RECEIPTS")
    other_non_sanction = getattr(record, "OTHER_NON_SANCTION")

    if sanc_reduction_amount > 0 and (work_req_sanction < 0 or family_sanc_adult < 0 or sanc_teen_parent or
                                      non_cooperation_case < 0 or failure_to_comply < 0 or other_sanction < 0):
        return (False, "WARNING: IF ITEM 26Ai > 0, ITEMS 26Aii THRU")

    if other_total_reductions > 0 and (family_cap < 0 or reductions_on_receipts < 0 or other_non_sanction < 0):
        return (False, "WARNING: IF ITEM 26Ci > 0, ITEMS 26Cii THRU")

    return (True, None)


t1_validators = {
    "DISPOSITION": validate_disposition,
    "CASH_AMOUNT_&_NBR_MONTHS": validate_cash_amount_and_nbr_months,
    "CC_AMOUNT_&_CHILDREN_COVERED_&_CC_NBR_MONTHS": validate_child_care,
    "TRANSP_AMOUNT_&_TRANSP_NBR_MONTHS": validate_transportation,
    "TRANSITION_SERVICES_AMOUNT_&_TRANSITION_NBR_MONTHS": validate_transitional_services,
    "OTHER_AMOUNT_&_OTHER_NBR_MONTHS": validate_other,
    "REASONS_FOR_AMOUNT_OF_ASSISTANCE_REDUCTIONS": validate_reasons_for_amount_of_assistance_reductions,
}

def cat3_validate_t1(record):
    """Execute all post-parsing category three validators."""
    validator_errors = []
    for field, validator in t1_validators.items():
        validator_is_valid, validator_error = validator(record)
        if not validator_is_valid:
            validator_errors.append(validator_error)

    if len(validator_errors):
        return (False, validator_errors)

    return (True, None)
