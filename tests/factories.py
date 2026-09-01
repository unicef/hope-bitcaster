import factory
from django.contrib.auth import get_user_model
from django.db.models import signals


@factory.django.mute_signals(signals.post_save, signals.pre_delete)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: "user%03d" % n)
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True
