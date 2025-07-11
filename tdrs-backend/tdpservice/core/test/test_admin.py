"""Core Admin class tests."""
import pytest
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType

from tdpservice.users.models import User


@pytest.mark.django_db
def test_log_entry_admin(admin_user, admin):
    """Tests the custom LogEntryAdmin."""
    log_entry = LogEntry(
        content_type_id=ContentType.objects.get_for_model(User).id,
        action_flag=ADDITION,
        object_id=admin_user.id,
        object_repr='OBJ_REPR'
    )
    assert 'OBJ_REPR' in admin.object_link(log_entry)
    assert '<a href="' in admin.object_link(log_entry)

from django.test import TestCase, Client
from django.urls import reverse
from tdpservice.users.models import UserChangeRequest, UserChangeRequestStatus
class TestAdminTemplates(TestCase):
    def setUp(self):
        # create a couple of users for testing
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
        )
        self.admin_user.is_active = True
        self.admin_user.save()

        return super().setUp()
    
    def test_user_change_request_form(self):
        """Test the user change request form template."""
        client = Client()
        # get reverse URL for admin/users/userchangerequest/ list view
        client.login(username='admin', password='adminpassword')
        response = client.get(reverse('admin:users_userchangerequest_changelist'))
        self.assertEqual(response.status_code, 200)
        
        self.assertNotContains(response=response, text='Approve</a>')
        self.assertNotContains(response=response, text='Reject</a>')

        UserChangeRequest.objects.create(
            user=self.admin_user,
            requested_by=self.admin_user,
            field_name='first_name',
            current_value='Admin',
            requested_value='NewAdmin',
            status=UserChangeRequestStatus.PENDING,
        )

        response = client.get(reverse('admin:users_userchangerequest_changelist'))
        self.assertContains(response=response, text='Approve</a>')
        self.assertContains(response=response, text='Reject</a>')

    def test_user_change_using_api(self):
        """Test the user change request approval."""
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Approve the change request using DRF API
        response = client.post('/v1/change-requests/', 
                               {
                                   'user': self.admin_user.id,
                                    'field_name': 'first_name',
                                    'requested_value': 'NewAdminAPI',
                               })
        self.assertEqual(response.status_code, 201)
        print(response.content)
        response = client.get(reverse('admin:users_userchangerequest_changelist'))
        self.assertContains(response=response, text='NewAdminAPI')
        self.assertContains(response=response, text='Approve</a>')
        self.assertContains(response=response, text='Reject</a>')

    def test_user_change_request_approve(self):
        """Test the user change request approval."""
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Create a change request
        change_request = UserChangeRequest.objects.create(
            user=self.admin_user,
            requested_by=self.admin_user,
            field_name='first_name',
            current_value='Admin',
            requested_value='NewAdmin',
            status=UserChangeRequestStatus.PENDING,
        )

        # Approve the change request
        response = client.post(reverse('admin:users_userchangerequest_changelist', args=[change_request.id]))
        self.assertEqual(response.status_code, 302)
