"""generate_cypress_users command."""

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.conf import settings

User = get_user_model()


def get_or_create_user(username):
    """Create a new user for a given username if one doesn't exist."""
    user = None

    try:
        user = User.objects.get(username=username)
        print(f'found {username}')
    except User.DoesNotExist:
        user = User.objects.create(username=username)
        print(f'created {username}')

    return user


def get_or_create_superuser(username):
    """Create a new super user for a given username if one doesn't exist."""
    super_user = None

    try:
        super_user = User.objects.get(username=username)
        print(f'found {username}')
    except User.DoesNotExist:
        super_user = User.objects.create_superuser(username=username, email=username)
        print(f'created super user {username}')

    return super_user


class Command(BaseCommand):
    """Command class."""

    help = "Generate test users if they don't exist."

    def handle(self, *args, **options):
        """Generate test users if they don't exist."""
        if settings.DEBUG:
            get_or_create_user('new-cypress@teamraft.com')
            get_or_create_superuser('cypress-admin@teamraft.com')
        else:
            raise Exception('Cannot create cypress users in non-dev environments.')
