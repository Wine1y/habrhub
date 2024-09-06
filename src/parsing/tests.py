from django.test import TestCase
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from .models import Hub
from .forms import HubCreationForm, HubUpdateForm


def new_hub(
    title="TestHub", url="http://www.sample.com",
    interval_minutes=10, enabled:bool=True
) -> Hub:
    interval = IntervalSchedule.objects.create(
        every=interval_minutes, period=IntervalSchedule.MINUTES
    )

    form = HubCreationForm({
        "title": title, "url": url,
        "interval": interval, "task_enabled": enabled
    })
    return form.save()

class HubTests(TestCase):
    def test_hub_create_form(self):
        self.assertTrue(Hub.objects.count() == 0, "No hubs should exist")
        self.assertTrue(PeriodicTask.objects.count() == 0, "No periodic tasks should exist")
        
        interval = IntervalSchedule(every=10, period=IntervalSchedule.MINUTES)
        interval.save()

        form = HubCreationForm({
            "title": "TestHub", "url": "http://www.sample.com",
            "interval": interval, "task_enabled": True
        })
        self.assertTrue(form.is_valid(), "Form should be valid")

        hub = form.save()
        self.assertTrue(Hub.objects.count() == 1, "Hub should be added")
        self.assertTrue(PeriodicTask.objects.count() == 1, "Periodic tasks should be added with hub")
        self.assertTrue(hub.parse_task is not None, "Hub should have a parse_task linked")

    def test_hub_update_form(self):
        hub = new_hub()
        self.assertTrue(Hub.objects.count() == 1, "Hub should be added")
        self.assertTrue(PeriodicTask.objects.count() == 1, "Periodic tasks should be added with hub")

        new_interval = IntervalSchedule(every=1, period=IntervalSchedule.HOURS)
        new_interval.save()
        update_form = HubUpdateForm({
            "title": "TestHubUpdated", "url": "http://www.newsample.com",
            "interval": new_interval, "task_enabled": False
        }, instance=hub)
        self.assertTrue(update_form.is_valid(), "Update form should be valid")
        
        hub = update_form.save()
        self.assertEqual(hub.title, "TestHubUpdated", "Hub title should be updated")
        self.assertEqual(hub.url, "http://www.newsample.com", "Hub url should be updated")
        self.assertEqual(hub.parse_task.interval, new_interval, "Hub parse task interval should be updated")
        self.assertEqual(hub.parse_task.enabled, False, "Hub parse task should be disabled")
    
    def test_hub_deletion(self):
        self.assertTrue(Hub.objects.count() == 0, "No hubs should exist")

        hub = new_hub()
        self.assertTrue(Hub.objects.count() == 1, "Hub should be created")
        self.assertTrue(PeriodicTask.objects.count() == 1, "Periodic Task should be created with hub")

        # OneToOneField CASCADE test 
        hub.parse_task.delete()
        self.assertTrue(Hub.objects.count() == 0, "Hub should be deleted")
        self.assertTrue(PeriodicTask.objects.count() == 0, "Periodic Task should be deleted with hub")

        hub = new_hub()
        self.assertTrue(Hub.objects.count() == 1, "Hub should be created")
        self.assertTrue(PeriodicTask.objects.count() == 1, "Periodic Task should be created with hub")

        # OneToOneField Reverse CASCADE test (post_delete signal)
        hub.delete()
        self.assertTrue(Hub.objects.count() == 0, "Hub should be deleted")
        self.assertTrue(PeriodicTask.objects.count() == 0, "Periodic Task should be deleted with hub")

