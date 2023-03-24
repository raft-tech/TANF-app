"""generate_cypress_users command."""

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.conf import settings

User = get_user_model()

def get_or_create_superuser(username, password):
    """Create a new super user for a given username if one doesn't exist."""
    super_user = None

    try:
        super_user = User.objects.get(username=username)
        print(f'found {username}')
    except User.DoesNotExist:
        super_user = User.objects.create_superuser(username=username, email=username, password=password)
        print(f'created super user {username}')

    return super_user


class Command(BaseCommand):
    """Command class."""

    help = "Generate test super users if they don't exist."

    def handle(self, *args, **options):
        """Generate test users if they don't exist."""
        if settings.DEBUG:
            get_or_create_superuser('new-super-cypress@teamraft.com', 'cypress_super')
        else:
            raise Exception('Cannot create cypress super users in non-dev environments.')
