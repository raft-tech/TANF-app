"""Search indexes admin tests."""

from django.urls import reverse

import pytest
from rest_framework import status

from tdpservice.search_indexes.models.reparse_meta import ReparseMeta


@pytest.mark.django_db
def test_reparse_meta_change_view_displays_record_totals_once(client, admin_user):
    """Reparse record totals are not duplicated on the admin change page."""
    reparse_meta = ReparseMeta.objects.create(db_backup_location="/tmp/backup.pg")
    client.login(username=admin_user.username, password="test_password")

    response = client.get(
        reverse("admin:search_indexes_reparsemeta_change", args=(reparse_meta.id,))
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.rendered_content.count("Total num records initial:") == 1
    assert response.rendered_content.count("Total num records post:") == 1
