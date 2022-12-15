"""Tests for elasticsearch model mapping."""

import pytest
from faker import Faker
from django.db.utils import IntegrityError
from tdpservice.search_indexes.models import T1, T2, T3, T4, T5, T6, T7
from tdpservice.search_indexes import documents


fake = Faker()


@pytest.mark.django_db
def test_can_create_and_index_t1_submission():
    """T1 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = T1.objects.create(
        record_type=record_num,
        reporting_month=1,
        case_number='1',
        county_fips_code='1',
        stratum=1,
        zip_code='1',
        funding_stream=1,
        disposition=1,
        new_applicant=1,
        family_size=1,
        family_type=1,
        receives_sub_housing=1,
        receives_medical_assistance=1,
        receives_food_stamps=1,
        food_stamp_amount=1,
        receives_sub_child_care=1,
        child_care_amount=1,
        child_support_amount=1,
        family_cash_recources=1,
        family_cash_amount=1,
        family_cash_nbr_month=1,
        tanf_child_care_amount=1,
        children_covered=1,
        child_care_nbr_months=1,
        transportation_amount=1,
        transport_nbr_months=1,
        transition_services_amount=1,
        transition_nbr_months=1,
        other_amount=1,
        other_nbr_months=1,
        reduction_amount=1,
        reduc_work_requirements=1,
        reduc_adult_no_hs_diploma=1,
        reduc_teen_not_in_school=1,
        reduc_noncooperation_child_support=1,
        reduc_irp_failure=1,
        reduc_other_sanction=1,
        reduc_prior_overpayment=1,
        total_reduc_amount=1,
        reduc_family_cap=1,
        reduc_length_of_assist=1,
        other_non_sanction=1,
        waiver_control_grps=1,
        tanf_family_exempt_time_limits=1,
        tanf_new_child_only_family=1,
    )

    # submission.full_clean()

    assert submission.id is not None

    search = documents.T1DataSubmissionDocument.search().query(
        'match',
        record_type=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_t2_submission():
    """T2 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = T2.objects.create(
        record=record_num,
        rpt_month_year=1,
        case_number='1',
        fips_code='1',

        family_affiliation=1,
        noncustodial_parent=1,
        date_of_birth='1',
        ssn='1',
        race_hispanic=1,
        race_amer_indian=1,
        race_asian=1,
        race_black=1,
        race_hawaiian=1,
        race_white=1,
        gender=1,
        fed_oasdi_program=1,
        fed_disability_status=1,
        disabled_title_xivapdt=1,
        aid_aged_blind=1,
        receive_ssi=1,
        marital_status=1,
        relationship_hoh=1,
        parent_minor_child=1,
        needs_pregnant_woman=1,
        education_level=1,
        citizenship_status=1,
        cooperation_child_support=1,
        months_fed_time_limit=1,
        months_state_time_limit=1,
        current_month_state_exempt=1,
        employment_status=1,
        work_eligible_indicator=1,
        work_part_status=1,
        unsub_employment=1,
        sub_private_employment=1,
        sub_public_employment=1,
        work_experience_hop=1,
        work_experience_ea=1,
        work_experience_hol=1,
        ojt=1,
        job_search_hop=1,
        job_search_ea=1,
        job_search_hol=1,
        comm_services_hop=1,
        comm_services_ea=1,
        comm_services_hol=1,
        vocational_ed_training_hop=1,
        vocational_ed_training_ea=1,
        vocational_ed_training_hol=1,
        job_skills_training_hop=1,
        job_skills_training_ea=1,
        job_skills_training_hol=1,
        ed_no_high_school_dipl_hop=1,
        ed_no_high_school_dipl_ea=1,
        ed_no_high_school_dipl_hol=1,
        school_attendence_hop=1,
        school_attendence_ea=1,
        school_attendence_hol=1,
        provide_cc_hop=1,
        provide_cc_ea=1,
        provide_cc_hol=1,
        other_work_activities=1,
        deemed_hours_for_overall=1,
        deemed_hours_for_two_parent=1,
        earned_income=1,
        unearned_income_tax_credit=1,
        unearned_social_security=1,
        unearned_ssi=1,
        unearned_workers_comp=1,
        other_unearned_income=1
    )

    assert submission.id is not None

    search = documents.T2DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_t3_submission():
    """T3 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = T3.objects.create(
        record=record_num,
        rpt_month_year=1,
        case_number='1',
        fips_code='1',

        family_affiliation=1,
        date_of_birth=1,
        ssn='1',
        race_hispanic=1,
        race_amer_indian=1,
        race_asian=1,
        race_black=1,
        race_hawaiian=1,
        race_white=1,
        gender=1,
        receive_nonssa_benefits=1,
        receive_ssi=1,
        relationship_hoh=1,
        parent_minor_child=1,
        education_level=1,
        citizenship_status=1,
        unearned_ssi=1,
        other_unearned_income=1,
    )

    assert submission.id is not None

    search = documents.T3DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_t4_submission():
    """T4 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = T4.objects.create(
        record=record_num,
        rpt_month_year=1,
        case_number='1',
        disposition=1,
        fips_code='1',

        county_fips_code='1',
        stratum=1,
        zip_code='1',
        closure_reason=1,
        rec_sub_housing=1,
        rec_med_assist=1,
        rec_food_stamps=1,
        rec_sub_cc=1,
    )

    assert submission.id is not None

    search = documents.T4DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_t5_submission():
    """T5 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = T5.objects.create(
        record=record_num,
        rpt_month_year=1,
        case_number='1',
        fips_code='1',

        family_affiliation=1,
        date_of_birth='1',
        ssn='1',
        race_hispanic=1,
        race_amer_indian=1,
        race_asian=1,
        race_black=1,
        race_hawaiian=1,
        race_white=1,
        gender=1,
        rec_oasdi_insurance=1,
        rec_federal_disability=1,
        rec_aid_totally_disabled=1,
        rec_aid_aged_blind=1,
        rec_ssi=1,
        marital_status=1,
        relationship_hoh=1,
        parent_minor_child=1,
        needs_of_pregnant_woman=1,
        education_level=1,
        citizenship_status=1,
        countable_month_fed_time=1,
        countable_months_state_tribe=1,
        employment_status=1,
        amount_earned_income=1,
        amount_unearned_income=1
    )

    assert submission.id is not None

    search = documents.T5DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_t6_submission():
    """T6 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = T6.objects.create(
        record=record_num,
        rpt_month_year=1,
        fips_code='1',

        calendar_quarter=1,
        applications=1,
        approved=1,
        denied=1,
        assistance=1,
        families=1,
        num_2_parents=1,
        num_1_parents=1,
        num_no_parents=1,
        recipients=1,
        adult_recipients=1,
        child_recipients=1,
        noncustodials=1,
        births=1,
        outwedlock_births=1,
        closed_cases=1,
    )

    assert submission.id is not None

    search = documents.T6DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_t7_submission():
    """T7 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = T7.objects.create(
        record=record_num,
        rpt_month_year=1,
        fips_code='2',

        calendar_quarter=1,
        tdrs_section_ind='1',
        stratum='1',
        families=1
    )

    assert submission.id is not None

    search = documents.T7DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_does_not_create_index_if_model_creation_fails():
    """Index creation shouldn't happen if saving a model errors."""
    record_num = fake.uuid4()

    with pytest.raises(IntegrityError):
        submission = T7.objects.create(
            record=record_num
            # leave out a bunch of required fields
        )

        assert submission.id is None

    search = documents.T7DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )

    response = search.execute()

    assert response.hits.total.value == 0
