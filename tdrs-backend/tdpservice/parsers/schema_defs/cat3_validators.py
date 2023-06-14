"""Collection of category three validators for TANF Section 1 records."""


from .. import validators

def validate_food_stamps(record):
    """Validate food stamp dependencies."""
    rec_fs = getattr(record, "RECEIVES_FOOD_STAMPS")
    fs_amount = getattr(record, "AMT_FOOD_STAMP_ASSISTANCE")

    if fs_amount > 0 and rec_fs != 1:
        return (False, "IF ITEM 16 > 0 THEN ITEM 15 == 1")

    return (True, None)

def validate_subsidized_child_care(record):
    """Validate subsidized child care dependencies."""
    rec_sub_cc = getattr(record, "RECEIVES_SUB_CC")
    amt_sub_cc = getattr(record, "AMT_SUB_CC")

    if amt_sub_cc > 0 and rec_sub_cc == 3:
        return (False, "IF ITEM 18 > 0 THEN ITEM 17 != 3")

    return (True, None)

def validate_cash_amount_and_nbr_months(record):
    """Validate cash and cash equivalents dependencies."""
    cash_amount = getattr(record, "CASH_AMOUNT")
    nbr_months = getattr(record, "NBR_MONTHS")

    if cash_amount == 0 and nbr_months < 0:
        return (False, "ITEM 21A AND ITEM 21B MUST => 0")

    if cash_amount > 0 and nbr_months <= 0:
        return (False, "IF ITEM 21A > 0, ITEM 21B MUST > 0")

    return (True, None)


def validate_child_care(record):
    """Validate child care dependencies."""
    cc_amount = getattr(record, "CC_AMOUNT")
    children_covered = getattr(record, "CHILDREN_COVERED")
    cc_nbr_months = getattr(record, "CC_NBR_MONTHS")

    if cc_amount == 0 and children_covered < 0:
        return (False, "ITEM 22A AND ITEM 22B MUST => 0")

    if cc_amount > 0 and children_covered <= 0 and cc_nbr_months <= 0:
        return (False, "IF ITEM 22A > 0, ITEM 22B MUST > 0, ITEM 22C MUST > 0")

    return (True, None)


def validate_transportation(record):
    """Validate transportation dependencies."""
    transp_amount = getattr(record, "TRANSP_AMOUNT")
    transp_nbr_months = getattr(record, "TRANSP_NBR_MONTHS")

    if transp_amount == 0 and transp_nbr_months < 0:
        return (False, "ITEM 23A AND ITEM 23B MUST => 0")

    if transp_amount > 0 and transp_nbr_months <= 0:
        return (False, "IF ITEM 23A > 0, ITEM 23B MUST > 0")

    return (True, None)


def validate_transitional_services(record):
    """Validate transitional services dependencies."""
    trans_svc_amount = getattr(record, "TRANSITION_SERVICES_AMOUNT")
    trans_nbr_months = getattr(record, "TRANSITION_NBR_MONTHS")

    if trans_svc_amount == 0 and trans_nbr_months < 0:
        return (False, "ITEM 24A AND ITEM 24B MUST => 0")

    if trans_svc_amount > 0 and trans_nbr_months <= 0:
        return (False, "IF ITEM 24A > 0, ITEM 24B MUST > 0")

    return (True, None)


def validate_other(record):
    """Validate other dependencies."""
    other_amount = getattr(record, "OTHER_AMOUNT")
    other_nbr_months = getattr(record, "OTHER_NBR_MONTHS")

    if other_amount == 0 and other_nbr_months < 0:
        return (False, "ITEM 25A AND ITEM 25B MUST => 0")

    if other_amount > 0 and other_nbr_months <= 0:
        return (False, "IF ITEM 25A > 0, ITEM 25B MUST > 0")

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

    between = validators.between(0, 3)

    truth_val = (between(work_req_sanction)[0] or between(family_sanc_adult)[0] or between(sanc_teen_parent)[0] or
                 between(non_cooperation_case)[0] or between(failure_to_comply)[0] or between(other_sanction)[0])

    if sanc_reduction_amount > 0 and truth_val:
        return (False, "IF ITEM 26Ai > 0, ITEMS 26Aii THRU")

    truth_val = between(family_cap)[0] or between(reductions_on_receipts)[0] or between(other_non_sanction)[0]

    if other_total_reductions > 0 and truth_val:
        return (False, "IF ITEM 26Ci > 0, ITEMS 26Cii THRU")

    return (True, None)

def validate_sum_amounts(record):
    """Validate the sum of all 'amount' fields."""
    fs_amount = getattr(record, "AMT_FOOD_STAMP_ASSISTANCE")
    amt_sub_cc = getattr(record, "AMT_SUB_CC")
    cc_amount = getattr(record, "CC_AMOUNT")
    transp_amount = getattr(record, "TRANSP_AMOUNT")
    trans_svc_amount = getattr(record, "TRANSITION_SERVICES_AMOUNT")
    other_amount = getattr(record, "OTHER_AMOUNT")

    sum = fs_amount + amt_sub_cc + cc_amount + transp_amount + trans_svc_amount + other_amount

    if sum < 0:
        return (False, "SUM(ITEMS 16, 18, 22A, 23A, 24A, 25A )> 0")

    return (True, None)


t1_validators = [
    validate_food_stamps,
    validate_subsidized_child_care,
    validate_cash_amount_and_nbr_months,
    validate_child_care,
    validate_transportation,
    validate_transitional_services,
    validate_other,
    validate_reasons_for_amount_of_assistance_reductions,
    validate_sum_amounts
]

def cat3_validate_t1(record):
    """Execute all post-parsing category three validators."""
    validator_errors = []
    for validator in t1_validators:
        validator_is_valid, validator_error = validator(record)
        if not validator_is_valid:
            validator_errors.append(validator_error)

    if len(validator_errors):
        return (False, validator_errors)

    return (True, None)


"""T2 Validators"""
def validate_ssn(record):
    """Validate social security number dependencies."""
    ssn = getattr(record, "SSN")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")
    oneOf = validators.oneOf(("999999999", "000000000"))

    if family_affiliation == "1" and oneOf(ssn)[0]:
        return (False, "IF ITEM 30 == 1 THEN ITEM 33 != 000000000 -- 999999999")

    return (True, None)

def validate_race_ethnicity(record):
    """Validate race/ethnicity dependencies."""
    races = [getattr(record, "RACE_HISPANIC"), getattr(record, "RACE_AMER_INDIAN"),
             getattr(record, "RACE_ASIAN"), getattr(record, "RACE_BLACK"),
             getattr(record, "RACE_HAWAIIAN"), getattr(record, "RACE_WHITE")]
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")
    fa_oneOf = validators.oneOf((1, 2, 3))
    race_oneOf = validators.oneOf(("1", "2"))

    for race in races:
        if fa_oneOf(family_affiliation)[0] and not race_oneOf(race)[0]:
            return (False, "IF ITEM 30 == 1, 2, OR 3, THEN ITEMS 34A-34F == 1 OR 2")

    return (True, None)

def validate_marital_status(record):
    """Validate marital status dependencies."""
    marital_status = getattr(record, "MARITAL_STATUS")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")
    fa_oneOf = validators.oneOf((1, 2, 3))
    ms_oneOf = validators.oneOf(("1", "2", "3", "4", "5"))

    if fa_oneOf(family_affiliation)[0] and not ms_oneOf(marital_status)[0]:
        return (False, "IF ITEM 30 == 1, 2, OR 3, THEN ITEM 37 == 1, 2, 3, 4, or 5")

    return (True, None)

def validate_parent_with_minor(record):
    """Validate parent with a minor child dependencies."""
    parent_with_minor = getattr(record, "PARENT_WITH_MINOR_CHILD")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    fa_oneOf = validators.oneOf((1, 2))
    pmc_oneOf = validators.oneOf(("1", "2", "3"))

    if fa_oneOf(family_affiliation)[0] and not pmc_oneOf(parent_with_minor)[0]:
        return (False, "IF ITEM 30 == 1, 2 THEN ITEM 39 MUST = 1-3")

    return (True, None)

def validate_education_level(record):
    """Validate education level dependencies."""
    education_level = getattr(record, "EDUCATION_LEVEL")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    between = validators.between(0, 4)
    first_oneOf = validators.oneOf(("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14",
                                    "15", "16", "98", "99"))

    if between(family_affiliation)[0] and not first_oneOf(education_level)[0]:
        return (False, "IF ITEM 30 == 1-3 ITEM 41 MUST == 01-16,98,99")

    return (True, None)

def validate_citizenship(record):
    """Validate citizenship dependencies."""
    citizenship = getattr(record, "CITIZENSHIP_STATUS")
    ssn = getattr(record, "SSN")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    citizen_oneOf = validators.oneOf(("1", "2"))
    ssn_oneOf = validators.oneOf(("999999999", "000000000"))

    if family_affiliation == 2 and citizen_oneOf(citizenship)[0] and ssn_oneOf(ssn)[0]:
        return (False, "IF ITEM 30 == 2 AND ITEM 42 == 1 OR 2, THEN ITEM 33 != 000000000 -- 999999999")

    if family_affiliation == 1 and not citizen_oneOf(citizenship)[0]:
        return (False, "IF ITEM 30 == 1 THEN ITEM 42 == 1 OR 2")

    return (True, None)

def validate_cooperation_with_child_support(record):
    """Validate cooperation with child support dependencies."""
    cooperation_with_child_support = getattr(record, "COOPERATION_CHILD_SUPPORT")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    between = validators.between(0, 4)
    oneOf = validators.oneOf(("1", "2", "9"))

    if between(family_affiliation)[0] and not oneOf(cooperation_with_child_support)[0]:
        return (False, "IF ITEM 30 == 1, 2, or 3, THEN ITEM 43 == 1,2, or 9")

    return (True, None)

def validate_months_federal_time_limit(record):
    """Validate federal countable months dependencies."""
    months_fed_time_limit = getattr(record, "MONTHS_FED_TIME_LIMIT")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")
    relationsip_to_hoh = getattr(record, "RELATIONSHIP_HOH")

    oneOf = validators.oneOf((1, 2))

    if family_affiliation == 1 and oneOf(relationsip_to_hoh)[0] and int(months_fed_time_limit) < 1:
        return (False, "IF ITEM 30 = 1 AND ITEM 38=1 OR 2, THEN ITEM 44 MUST => 1")

    return (True, None)

def validate_employment_status(record):
    """Validate employment status dependencies."""
    employment_status = getattr(record, "EMPLOYMENT_STATUS")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    between = validators.between(0, 4)
    oneOf = validators.oneOf(("1", "2", "3"))

    if between(family_affiliation)[0] and not oneOf(employment_status)[0]:
        return (False, "IF ITEM 30 = 1-4 THEN ITEM 47 MUST = 1-3")

    return (True, None)

def validate_work_eligible_indicator(record):
    """Validate work eligibility dependencies."""
    work_eligible_indicator = getattr(record, "WORK_ELIGIBLE_INDICATOR")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    between = validators.between(0, 3)
    oneOf = validators.oneOf(("01", "02", "03", "04", "05", "06", "07", "08", "09", "12"))

    if between(family_affiliation)[0] and not oneOf(work_eligible_indicator)[0]:
        return (False, "IF ITEM 30 == 1 or 2, THEN ITEM 48 == 01-09, OR 12")

    return (True, None)

def validate_work_participation(record):
    """Validate work participation dependencies."""
    work_part = getattr(record, "WORK_PART_STATUS")
    work_eligible_indicator = getattr(record, "WORK_ELIGIBLE_INDICATOR")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    between = validators.between(0, 3)
    oneOf = validators.oneOf(("01", "02", "05", "07", "09", "15", "16", "17", "18", "19", "99"))
    wei_oneOf = validators.oneOf(("01", "02", "03", "04", "05"))

    if between(family_affiliation)[0] and not oneOf(work_part)[0]:
        return (False, "IF ITEM 30 == 1 or 2, THEN ITEM 49 MUST = 01-02, 05, 07, 09, 15-19, or 99")

    if wei_oneOf(work_eligible_indicator)[0] and work_part == "99":
        return (False, "IF ITEM 48 == 01-05, THEN ITEM 49 != 99")

    return (True, None)


t2_validators = [
    validate_ssn,
    validate_race_ethnicity,
    validate_marital_status,
    validate_parent_with_minor,
    validate_education_level,
    validate_citizenship,
    validate_cooperation_with_child_support,
    validate_months_federal_time_limit,
    validate_employment_status,
    validate_work_eligible_indicator,
    validate_work_participation,
]

def cat3_validate_t2(record):
    """Execute all post-parsing category three validators."""
    validator_errors = []
    for validator in t1_validators:
        validator_is_valid, validator_error = validator(record)
        if not validator_is_valid:
            validator_errors.append(validator_error)

    if len(validator_errors):
        return (False, validator_errors)

    return (True, None)


"""T3 Validators"""
def validate_t3_ssn(record):
    """Validate social security number dependencies."""
    ssn = getattr(record, "SSN")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")
    oneOf = validators.oneOf(("999999999", "000000000"))

    if family_affiliation == "1" and oneOf(ssn)[0]:
        return (False, "IF ITEM 67 == 1 THEN ITEM 33 != 000000000 -- 999999999")

    return (True, None)

def validate_t3_race_ethnicity(record):
    """Validate race/ethnicity dependencies."""
    races = [getattr(record, "RACE_HISPANIC"), getattr(record, "RACE_AMER_INDIAN"),
             getattr(record, "RACE_ASIAN"), getattr(record, "RACE_BLACK"),
             getattr(record, "RACE_HAWAIIAN"), getattr(record, "RACE_WHITE")]
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")
    fa_oneOf = validators.oneOf((1, 2, 3))
    race_oneOf = validators.oneOf(("1", "2"))

    for race in races:
        if fa_oneOf(family_affiliation)[0] and not race_oneOf(race)[0]:
            return (False, "IF ITEM 67 == 1, 2, OR 3, THEN ITEMS 70A-70F == 1 OR 2")

    return (True, None)

def validate_relationship_hoh(record):
    """Validate relationship to head of household dependencies."""
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")
    relationsip_to_hoh = getattr(record, "RELATIONSHIP_HOH")

    between = validators.between(0, 3)
    oneOf = validators.oneOf(("04", "05", "06", "07", "08", "09"))

    if between(family_affiliation) and not oneOf(relationsip_to_hoh)[0]:
        return (False, "IF ITEM 67 == 1 or 2, THEN ITEM 73 == 04-09")

    return (True, None)

def validate_t3_parent_with_minor(record):
    """Validate parent with a minor child dependencies."""
    parent_with_minor = getattr(record, "PARENT_WITH_MINOR_CHILD")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    fa_oneOf = validators.oneOf((1, 2))
    pmc_oneOf = validators.oneOf(("1", "2", "3"))

    if fa_oneOf(family_affiliation)[0] and not pmc_oneOf(parent_with_minor)[0]:
        return (False, "IF ITEM 67 == 1, 2 THEN ITEM 39 MUST = 1-3")

    return (True, None)

def validate_t3_education_level(record):
    """Validate education level dependencies."""
    education_level = getattr(record, "EDUCATION_LEVEL")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    if family_affiliation == 1 and education_level == "99":
        return (False, "IF ITEM 67 == 1 THEN ITEM 75 != 99")

    return (True, None)

def validate_t3_citizenship(record):
    """Validate citizenship dependencies."""
    citizenship = getattr(record, "CITIZENSHIP_STATUS")
    family_affiliation = getattr(record, "FAMILY_AFFILIATION")

    first_citizen_oneOf = validators.oneOf(("1", "2"))
    second_citizen_oneOf = validators.oneOf(("2", "9"))

    if family_affiliation == 1 and not first_citizen_oneOf(citizenship)[0]:
        return (False, "IF ITEM 67 == 1 THEN ITEM 76 == 1 OR 2")

    if family_affiliation == 2 and not second_citizen_oneOf(citizenship)[0]:
        return (False, "IF ITEM 67 == 2 THEN ITEM 76 == 2 OR 9")

    return (True, None)


t3_validators = [
    validate_t3_ssn,
    validate_t3_race_ethnicity,
    validate_relationship_hoh,
    validate_t3_parent_with_minor,
    validate_t3_education_level,
    validate_t3_citizenship,
]

def cat3_validate_t3(record):
    """Execute all post-parsing category three validators."""
    validator_errors = []
    for validator in t1_validators:
        validator_is_valid, validator_error = validator(record)
        if not validator_is_valid:
            validator_errors.append(validator_error)

    if len(validator_errors):
        return (False, validator_errors)

    return (True, None)
