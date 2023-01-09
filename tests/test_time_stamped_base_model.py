import pytest

from django.utils import timezone
from freezegun import freeze_time

from tests.models import DateTimeModel


@pytest.mark.django_db
class TestTimeStampedModel:
    def setup_method(self):
        self.obj = DateTimeModel.objects.create()

    def test_time_stamped_base_creation_date(self):
        assert self.obj.created is not None

    def test_time_stamped_base_modification_date(self):
        old_modified = self.obj.modified
        self.obj.save()
        assert self.obj.modified > old_modified

    @freeze_time("2023-01-01")
    def test_time_stamped_base_auto_now_add(self):
        obj = DateTimeModel.objects.create()
        assert obj.created == timezone.now()

    def test_time_stamped_base_auto_now(self):
        old_modified = self.obj.modified
        timezone.timedelta(seconds=5)
        self.obj.save()
        assert self.obj.modified > old_modified
