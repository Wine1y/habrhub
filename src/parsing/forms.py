import json
from datetime import datetime, timezone

from django import forms
from django.db.transaction import atomic
from django_celery_beat.models import IntervalSchedule
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django_celery_beat.models import PeriodicTask
from django.contrib import admin

from .models import Hub


class HubCreationForm(forms.ModelForm):
    interval = forms.ModelChoiceField(IntervalSchedule.objects.all(), label="Parsing period")
    task_enabled = forms.BooleanField(label="Parsing enabled", initial=True, required=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        rel = PeriodicTask._meta.get_field("interval").remote_field
        self.fields["interval"].widget = RelatedFieldWidgetWrapper(self.fields["interval"].widget, rel, admin.site, can_add_related=True, can_change_related=True)

    class Meta:
        model = Hub
        exclude = ("parse_task",)

    @atomic
    def save(self, commit: bool = True) -> Hub:
        super().save(commit=False)

        hub = Hub(
            title=self.cleaned_data.get("title"),
            url=self.cleaned_data.get("url")
        )
        hub.save()
        
        task = PeriodicTask.objects.create(
            name=f"Parse {self.cleaned_data.get('url')}",
            task="parsing.tasks.parse_hub_task",
            interval=self.cleaned_data.get("interval"),
            enabled=self.cleaned_data.get("task_enabled"),
            kwargs=json.dumps({"hub_id": hub.id}),
            start_time=datetime.now(tz=timezone.utc)
        )
        hub.parse_task = task

        if commit:
            hub.save()
        return hub

class HubUpdateForm(forms.ModelForm):
    interval = forms.ModelChoiceField(IntervalSchedule.objects.all(), label="Parsing period")
    task_enabled = forms.BooleanField(label="Parsing enabled", required=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        rel = PeriodicTask._meta.get_field("interval").remote_field
        self.fields["interval"].widget = RelatedFieldWidgetWrapper(self.fields["interval"].widget, rel, admin.site, can_add_related=True, can_change_related=True)
        
        self.fields["interval"].initial = self.instance.parse_task.interval
        self.fields["task_enabled"].initial = self.instance.parse_task.enabled

    class Meta:
        model = Hub
        exclude = ("parse_task",)

    @atomic
    def save(self, commit: bool = True) -> Hub:
        super().save(commit=False)
        self.instance.parse_task.interval = self.cleaned_data.get("interval")
        self.instance.parse_task.enabled = self.cleaned_data.get("task_enabled")
        self.instance.parse_task.name = f"Parse {self.cleaned_data.get('url')}"
        self.instance.parse_task.save()
        
        self.instance.title = self.cleaned_data.get("title")
        self.instance.url = self.cleaned_data.get("url")

        if commit:
            self.instance.save()
        return self.instance