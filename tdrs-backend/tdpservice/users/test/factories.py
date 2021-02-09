"""Generate test data for users."""

import factory

from tdpservice.stts.test.factories import STTFactory


class BaseUserFactory(factory.django.DjangoModelFactory):
    """Generate test data for users."""

    class Meta:
        """Hardcoded metata data for users."""

        model = "users.User"
        django_get_or_create = ("username",)

    id = factory.Faker("uuid4")
    username = factory.Sequence(lambda n: "testuser%d" % n)
    password = "test_password"  # Static password so we can login.
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Add groups to user instance."""
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)



class UserFactory(BaseUserFactory):
    """General purpose user factory used through out most tests."""
    stt = factory.SubFactory(STTFactory)

class STTUserFactory(BaseUserFactory):
    """User factory for use in STT tests."""
    stt = None
