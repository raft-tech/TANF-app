"""Houses definitions for TANF datafile schemas."""

from ..util import RowSchema

def t1_schema():
    """Return a RowSchema for T1 records.

                    FAMILY CASE CHARACTERISTIC DATA

    DESCRIPTION         LENGTH  FROM    TO  COMMENTS
    RECORD TYPE         2       1       2   "T1" - SECTION 1
    REPORTING MONTH     6       3       8   Numeric
    CASE NUMBER         11      9       19  Alphanumeric
    COUNTY FIPS CODE    3       20      22  Numeric
    STRATUM             2       23      24  Numeric
    ZIP CODE            5       25      29  Alphanumeric
    FUNDING STREAM      1       30      30  Numeric
    DISPOSITION         1       31      31  Numeric
    NEW APPLICANT       1       32      32  Numeric
    FAMILY MEMBERS      2       33      34  Numeric
    TYPE OF FAMILY      1       35      35  Numeric
    SUBSIDIZED HOUSING  1       36      36  Numeric
    MEDICAL ASSISTANCE  1       37      37  Numeric
    FOOD STAMPS         1       38      38  Numeric
    FOOD STAMP AMOUNT   4       39      42  Numeric
    SUB CHILD CARE      1       43      43  Numeric
    AMT CHILD CARE      4       44      47  Numeric
    AMT CHIILD SUPPORT  4       48      51  Numeric
    FAMILY'S CASH       4       52      55  Numeric
    CASH
    AMOUNT              4       56      59  Numeric
    NBR_MONTH           3       60      62  Numeric
    TANF CHILD CARE
    AMOUNT              4       63      66  Numeric
    CHILDREN_COVERED    2       67      68  Numeric
    NBR_MONTHS          3       69      71  Numeric
    TRANSPORTATION
    AMOUNT              4       72      75  Numeric
    NBR_MONTHS          3       76      78  Numeric
    TRANSITIONAL SERVICES
    AMOUNT              4       79      82  Numeric
    NBR_MONTHS          3       83      85  Numeric
    OTHER
    AMOUNT              4       86      89  Numeric
    NBR_MONTHS          3       90      92  Numeric
    REASON FOR & AMOUNT OF ASSISTANCE
    REDUCTION
    SANCTIONS AMT       4       93      96  Numeric
    WORK REQ            1       97      97  Alphanumeric
    NO DIPLOMA          1       98      98  Alphanumeric
    NOT IN SCHOOL       1       99      99  Alphanumeric
    NOT CHILD SUPPORT   1       100     100 Alphanumeric
    IRP FAILURE         1       101     101 Alphanumeric
    OTHER SANCTION      1       102     102 Alphanumeric
    PRIOR OVERPAYMENT   4       103     106 Alphanumeric
    TOTAL REDUC AMOUNT  4       107     110 Alphanumeric
    FAMILY CAP          1       111     111 Alphanumeric
    LENGTH OF ASSIST    1       112     112 Alphanumeric
    OTHER, NON-SANCTION 1       113     113 Alphanumeric
    WAIVER_CONTROL_GRPS 1       114     114 Alphanumeric
    TANF FAMILY
    EXEMPT TIME_LIMITS  2       115     116 Numeric
    CHILD ONLY FAMILY   1       117     117 Numeric
    BLANK               39      118     156 Spaces
    """
    family_case_schema = RowSchema()
    family_case_schema.add_fields(
        [  # does it make sense to try to include regex (e.g., =r'^T1$')
            ('RecordType', 2, 1, 2, "Alphanumeric"),
            ('RPT_MONTH_YEAR', 6, 3, 8, "Numeric"),
            ('CASE_NUMBER', 11, 9, 19, "Alphanumeric"),
            ('COUNTY_FIPS_CODE', 3, 20, 22, "Numeric"),
            ('STRATUM', 2, 23, 24, "Numeric"),
            ('ZIP_CODE', 5, 25, 29, "Alphanumeric"),
            ('FUNDING_STREAM', 1, 30, 30, "Numeric"),
            ('DISPOSITION', 1, 31, 31, "Numeric"),
            ('NEW_APPLICANT', 1, 32, 32, "Numeric"),
            ('NBR_FAMILY_MEMBERS', 2, 33, 34, "Numeric"),
            ('FAMILY_TYPE', 1, 35, 35, "Numeric"),
            ('RECEIVES_SUB_HOUSING', 1, 36, 36, "Numeric"),
            ('RECEIVES_MED_ASSISTANCE', 1, 37, 37, "Numeric"),
            ('RECEIVES_FOOD_STAMPS', 1, 38, 38, "Numeric"),
            ('AMT_FOOD_STAMP_ASSISTANCE', 4, 39, 42, "Numeric"),
            ('RECEIVES_SUB_CC', 1, 43, 43, "Numeric"),
            ('AMT_SUB_CC', 4, 44, 47, "Numeric"),
            ('CHILD_SUPPORT_AMT', 4, 48, 51, "Numeric"),
            ('FAMILY_CASH_RESOURCES', 4, 52, 55, "Numeric"),
            ('CASH_AMOUNT', 4, 56, 59, "Numeric"),
            ('NBR_MONTHS', 3, 60, 62, "Numeric"),
            ('CC_AMOUNT', 4, 63, 66, "Numeric"),
            ('CHILDREN_COVERED', 2, 67, 68, "Numeric"),
            ('CC_NBR_MONTHS', 3, 69, 71, "Numeric"),
            ('TRANSP_AMOUNT', 4, 72, 75, "Numeric"),
            ('TRANSP_NBR_MONTHS', 3, 76, 78, "Numeric"),
            ('TRANSITION_SERVICES_AMOUNT', 4, 79, 82, "Numeric"),
            ('TRANSITION_NBR_MONTHS', 3, 83, 85, "Numeric"),
            ('OTHER_AMOUNT', 4, 86, 89, "Numeric"),
            ('OTHER_NBR_MONTHS', 3, 90, 92, "Numeric"),
            ('SANC_REDUCTION_AMT', 4, 93, 96, "Numeric"),
            ('WORK_REQ_SANCTION', 1, 97, 97, "Numeric"),
            ('FAMILY_SANC_ADULT', 1, 98, 98, "Numeric"),
            ('SANC_TEEN_PARENT', 1, 99, 99, "Numeric"),
            ('NON_COOPERATION_CSE', 1, 100, 100, "Numeric"),
            ('FAILURE_TO_COMPLY', 1, 101, 101, "Numeric"),
            ('OTHER_SANCTION', 1, 102, 102, "Numeric"),
            ('RECOUPMENT_PRIOR_OVRPMT', 4, 103, 106, "Numeric"),
            ('OTHER_TOTAL_REDUCTIONS', 4, 107, 110, "Numeric"),
            ('FAMILY_CAP', 1, 111, 111, "Numeric"),
            ('REDUCTIONS_ON_RECEIPTS', 1, 112, 112, "Numeric"),
            ('OTHER_NON_SANCTION', 1, 113, 113, "Numeric"),
            ('WAIVER_EVAL_CONTROL_GRPS', 1, 114, 114, "Numeric"),
            ('FAMILY_EXEMPT_TIME_LIMITS', 2, 115, 116, "Numeric"),
            ('FAMILY_NEW_CHILD', 1, 117, 117, "Numeric"),
            ('BLANK', 39, 118, 156, "Spaces"),
        ]
    )
    return family_case_schema

def t2_schema():
    """Return the RowSchema for T2 records.

        Adult Data

    DESCRIPTION                                                           LENGTH  FROM    TO  COMMENTS
    RECORD TYPE                                                           2       1       2   "T2" UP TO 6 ADULT RECORDS
    REPORTING MONTH                                                       6       3       8   Numeric
    CASE NUMBER                                                           11      9       19  Alphanumeric
    FAMILY AFFILIATIION                                                   1       20      20  Numeric
    NONCUSTODIAL PARENT                                                   1       21      21  Numeric
    DOB                                                                   8       22      29  Numeric
    SSN                                                                   9       30      38  Alphanumeric
    RACE/ETHNICIY
      ITEM34A_HISPANIC OR LATINO                                          1       39      39  Alphanumeric
      ITEM34B_AMERICAN INDIAN OR ALASKAN NATIVE                           1       40      40  Alphanumeric
      ITEM34C_ASIAN                                                       1       41      41  Alphanumeric
      ITEM34D_BLACK OR AFRICAN AMERICAN                                   1       42      42  Alphanumeric
      ITEM34E_NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER                   1       43      43  Alphanumeric
      ITEM34F_WHITE                                                       1       44      44  Alphanumeric
    GENDER                                                                1       45      45  Numeric
    RECEIVES FEDERAL DISABILITY BENEFITS
      ITEM36A_RECEIVES FEDERAL DISABILITY INSURNACE OASDI PROGRAM         1       46      46  Alphanumeric
      ITEM36B_RECEIVES BENEFITS BASED ON FEDERAL DISABILITY STATUS        1       47      47  Alphanumeric
      ITEM36C_RECEIVES AID TO THE PERMANENTLY AND TOTALLY                 1       48      48  Alphanumeric
              DISABLED UNDER TITLE XIV-APDT
      ITEM36D_RECEIVES AID TO THE AGED, BLIND                             1       49      49  Alphanumeric
      ITEM36E_RECEIVES SUPPLEMENTAL SECURITY INCOME UNDER                 1       50      50  Alphanumeric
              TITLE XVI-SSI
    MARITAL STATUS                                                        1       51      51  Alphanumeric
    RELATIONSHIP TO HEAD OF HOUSEHOLD                                     2       52      53  Alphanumeric
    PARENT WITH MINOR CHILD                                               1       54      54  Alphanumeric
    NEEDS OF A PREGNANT WOMAN                                             1       55      55  Alphanumeric
    EDUCATION LEVEL                                                       2       56      57  Alphanumeric
    CITIZENSHIP STATUS                                                    1       58      58  Alphanumeric
    COOPERATION WITH CHILD SUPPORT                                        1       59      59  Alphanumeric
    NUMBER OF COUNTABLE MONTHS
      TOWARD FEDERAL TIME-LIMIT                                           3       60      62  Alphanumeric
    NUMBER OF COUNTABLE MONTHS REMAINING
      UNDER STATE/TIBE TIME-LIMIT                                         2       63      64  Alphanumeric
    CURRENT MONTH EXEMPT FROM STATE
      TRIBE TIME-LIMIT                                                    1       65      65  Alphanumeric
    EMPLYMENT STATUS                                                      1       66      66  Alphanumeric
    WORK ELIGIBLE INDIVIDUAL INDICATOR                                    2       67      68  Alphanumeric
    WORK PARTICIPATION STATUS                                             2       69      70  Alphanumeric
    UNSUBSIDIZED EMPLOYMENT                                               2       71      72  Alphanumeric
    SUBSIDIZED PRIVATE EMPLOYMENT                                         2       73      74  Alphanumeric
    SUBSIDIZED PUBLIC EMPLOYMENT                                          2       75      76  Alphanumeric
    WORK EXPERIENCE
      ITEM53A_HOURS OF PARTICIPATION                                      2       77      78  Alphanumeric
      ITEM53B_EXCUSED ABSENSES                                            2       79      80  Alphanumeric
      ITEM53C_HOLIDAYS                                                    2       81      82  Alphanumeric
    ON THE JOB TRAINING                                                   2       83      84  Alphanumeric
    JOB SEARCH & JOB READINESS
      ITEM55A_HOURS OF PARTICIPATION                                      2       85      86  Alphanumeric
      ITEM55B_EXCUSED ABSENSES                                            2       87      88  Alphanumeric
      ITEM55C_HOLIDAYS                                                    2       89      90  Alphanumeric
    COMMUNITY SVS PROG.
      ITEM56A_HOURS OF PARTICIPATION                                      2       91      92  Alphanumeric
      ITEM56B_EXCUSED ABSENSES                                            2       93      94  Alphanumeric
      ITEM56C_HOLIDAYS                                                    2       95      96  Alphanumeric
    VOCATIONAL EDUCATION TRAINING
      ITEM57A_HOURS OF PARTICIPATION                                      2       97      98  Alphanumeric
      ITEM57B_EXCUSED ABSENSES                                            2       99      100  Alphanumeric
      ITEM57C_HOLIDAYS                                                    2       101     102  Alphanumeric
    JOB SKILLS TRAINING EMPLOYMENT RELATED
      EMPLOYMENT
      ITEM58A_HOURS OF PARTICIPATION                                      2       103     104  Alphanumeric
      ITEM58B_EXCUSED ABSENSES                                            2       105     106  Alphanumeric
      ITEM58C_HOLIDAYS                                                    2       107     108  Alphanumeric
    EDUCATION RELATED TO EMPLOYMENT WITH
      NO HIGH SCHOOL DIPLOMA
      ITEM59A_HOURS OF PARTICIPATION                                      2       109     110  Alphanumeric
      ITEM59B_EXCUSED ABSENSES                                            2       111     112  Alphanumeric
      ITEM59C_HOLIDAYS                                                    2       113     114  Alphanumeric
    SATISFACTORY SCHOOL ATTENDENCE
      ITEM60A_HOURS OF PARTICIPATION                                      2       115     116  Alphanumeric
      ITEM60B_EXCUSED ABSENSES                                            2       117     118  Alphanumeric
      ITEM60C_HOLIDAYS                                                    2       119     120  Alphanumeric
    PROVIDING CHILDE CARE
      ITEM61A_HOURS OF PARTICIPATION                                      2       121     122  Alphanumeric
      ITEM61B_EXCUSED ABSENSE                                             2       123     124  Alphanumeric
      ITEM61C_HOLIDAYS                                                    2       125     126  Alphanumeric
    OTHER WORK ACTIVITIES                                                 2       127     128  Alphanumeric
    NUMBER OF DEEMED CORE HOURS FOR                                       2       129     130  Alphanumeric
      OVERALL RATE
    NUMBER OF DEEMED CORE HOURS FOR                                       2       131     132  Alphanumeric
      THE TWO-PARENT RATE
    AMOUNT OF EARNED INCOME                                               4       133     136  Alphanumeric
    AMOUNT OF UNEARNED INCOME
      ITEM66A_EARNED INCOME TAX CREDIT                                    4       137     140 Alphanumeric
      ITEM66B_SOCIAL SECURITY                                             4       141     144 Alphanumeric
      ITEM66C_SSI                                                         4       145     148 Alphanumeric
      ITEM66D_WORKERS COMPENSATION                                        4       149     152 Alphanumeric
      ITEM66D_OTHER UNEARNED INCOME                                       4       153     156 Alphanumeric
    """
    adult_data_schema = RowSchema()
    adult_data_schema.add_fields(
        [
            ('RecordType', 2, 1, 2, "Alphanumeric"),
            ('RPT_MONTH_YEAR', 6, 3, 8, "Numeric"),
            ('CASE_NUMBER', 11, 9, 19, "Alphanumeric"),
            ('FAMILY_AFFILIATION', 1, 20, 20, "Numeric"),
            ('NONCUSTODIAL_PARENT', 1, 21, 21, "Numeric"),
            ('DOB', 8, 22, 29, "Numeric"),
            ('SSN', 9, 30, 38, "Alphanumeric"),
            ('ITEM34A_HISPANIC OR LATINO', 1, 39, 39, "Alphanumeric"),
            ('ITEM34B_AMERICAN INDIAN OR ALASKA NATIVE', 1, 40, 40, "Alphanumeric"),
            ('ITEM34C_ASIAN', 1, 41, 41, "Alphanumeric"),
            ('ITEM34D_BLACK OR AFRICAN AMERICAN', 1, 42, 42, "Alphanumeric"),
            ('ITEM34E_NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDE', 1, 43, 43, "Alphanumeric"),
            ('ITEM34F_WHITE', 1, 44, 44, "Alphanumeric"),
            ('GENDER', 1, 45, 45, "Alphanumeric"),
            ('ITEM36A_RECEIVES FEDERAL DISABILITY INSURANCE OASDI PROGRA', 1, 46, 46, "Alphanumeric"),
            ('ITEM36B_RECEIVES BENEFITS BASED ON FEDERAL DISABILITY STATUs', 1, 47, 47, "Alphanumeric"),
            ('ITEM36C_RECEIVES AID TO THE PERMANENTLY AND TOTALLY DISABLED UNDER TITLE XIV-APDT',
             1, 48, 48, "Alphanumeric"),
            ('ITEM36D_RECEIVES AID TO THE AGED, BLIND', 1, 49, 49, "Alphanumeric"),
            ('ITEM36E_RECEIVES SUPPLEMENTAL SECURITY INCOME UNDER TITLE XVI-SSI', 1, 50, 50, "Alphanumeric"),
            ('MARITAL_STATUS', 1, 51, 51, "Alphanumeric"),
            ('RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD', 2, 52, 53, "Numeric"),
            ('PARENT_WITH_MINOR_CHILD', 1, 54, 54, "Alphanumeric"),
            ('NEEDS_OF_A_PREGNANT_WOMAN', 1, 55, 55, "Alphanumeric"),
            ('EDUCATION_LEVEL', 2, 56, 57, "Alphanumeric"),
            ('CITIZENSHIP_STATUS', 1, 58, 58, "Alphanumeric"),
            ('COOPERATION_WITH_CHILD_SUPPORT', 1, 59, 59, "Alphanumeric"),
            ('NUMBER_OF_COUNTABLE_MONTHS', 3, 60, 62, "Alphanumeric"),
            ('NUMBER_OF_COUNTABLE_MONTHS_REMAINING', 2, 63, 64, "Alphanumeric"),
            ('CURRENT_MONTH_EXEMPT_FROM_STATE', 1, 65, 65, "Alphanumeric"),
            ('EMPLOYMENT_STATUS', 1, 66, 66, "Alphanumeric"),
            ('WORK_ELIGIBLE_INDIVIDUAL_INDICATOR', 2, 67, 68, "Alphanumeric"),
            ('WORK_PARTICIPATION_STATUS', 2, 69, 70, "Alphanumeric"),
            ('UNSUBSIDIZED_EMPLOYMENT', 2, 71, 72, "Alphanumeric"),
            ('SUBSIDIZED_PRIVATE_EMPLOYMENT', 2, 73, 74, "Alphanumeric"),
            ('SUBSIDIZED_PUBLIC_EMPLOYMENT', 2, 75, 76, "Alphanumeric"),
            ('ITEM53A_HOURS_OF_PARTICIPATION', 2, 77, 78, "Alphanumeric"),
            ('ITEM53B_EXCUSED_ABSENCES', 2, 79, 80, "Alphanumeric"),
            ('ITEM53C_HOLIDAYS', 2, 81, 82, "Alphanumeric"),
            ('ON_THE_JOB_TRAINING', 2, 83, 84, "Alphanumeric"),
            ('ITEM55A_HOURS_OF_PARTICIPATION', 2, 85, 86, "Alphanumeric"),
            ('ITEM55B_EXCUSED_ABSENCES', 2, 87, 88, "Alphanumeric"),
            ('ITEM55C_HOLIDAYS', 2, 89, 90, "Alphanumeric"),
            ('ITEM56A_HOURS_OF_PARTICIPATION', 2, 91, 92, "Alphanumeric"),
            ('ITEM56B_EXCUSED_ABSENCES', 2, 93, 94, "Alphanumeric"),
            ('ITEM56C_HOLIDAYS', 2, 95, 96, "Alphanumeric"),
            ('ITEM57A_HOURS_OF_PARTICIPATION', 2, 97, 98, "Alphanumeric"),
            ('ITEM57B_EXCUSED_ABSENCES', 2, 99, 100, "Alphanumeric"),
            ('ITEM57C_HOLIDAYS', 2, 101, 102, "Alphanumeric"),
            ('ITEM58A_HOURS_OF_PARTICIPATION', 2, 103, 104, "Alphanumeric"),
            ('ITEM58B_EXCUSED_ABSENCES', 2, 105, 106, "Alphanumeric"),
            ('ITEM58C_HOLIDAYS', 2, 107, 108, "Alphanumeric"),
            ('ITEM59A_HOURS_OF_PARTICIPATION', 2, 109, 110, "Alphanumeric"),
            ('ITEM59B_EXCUSED_ABSENCES', 2, 111, 112, "Alphanumeric"),
            ('ITEM59C_HOLIDAYS', 2, 113, 114, "Alphanumeric"),
            ('ITEM60A_HOURS_OF_PARTICIPATION', 2, 115, 116, "Alphanumeric"),
            ('ITEM60B_EXCUSED_ABSENCES', 2, 117, 118, "Alphanumeric"),
            ('ITEM60C_HOLIDAYS', 2, 119, 120, "Alphanumeric"),
            ('ITEM61A_HOURS_OF_PARTICIPATION', 2, 121, 122, "Alphanumeric"),
            ('ITEM61B_EXCUSED_ABSENCES', 2, 123, 124, "Alphanumeric"),
            ('ITEM61C_HOLIDAYS', 2, 125, 126, "Alphanumeric"),
            ('OTHER_WORK_ACTIVITIES', 2, 127, 128, "Alphanumeric"),
            ('NUMBER_OF_DEEMED_CORE_HOURS_FOR_OVERALL_RATE', 2, 129, 130, "Alphanumeric"),
            ('NUMBER_OF_DEEMED_CORE_HOURS_FOR_TWO_PARENT_RATE', 2, 131, 132, "Alphanumeric"),
            ('AMOUNT_OF_EARNED_INCOME', 4, 133, 136, "Alphanumeric"),
            ('ITEM66A_EARNED INCOME TAX CREDIT', 4, 137, 140, "Alphanumeric"),
            ('ITEM66B_SOCIAL SECURITY', 4, 141, 144, "Alphanumeric"),
            ('ITEM66C_SSI', 4, 145, 148, "Alphanumeric"),
            ('ITEM66D_WORKERS COMPENSATION', 4, 149, 152, "Alphanumeric"),
            ('ITEM66E_OTHER UNEARNED INCOME', 4, 153, 156, "Alphanumeric"),
        ])
    return adult_data_schema
