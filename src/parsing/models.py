from django.db import models
from django_celery_beat.models import PeriodicTask
from django.dispatch import receiver


class Hub(models.Model):
    title = models.CharField(max_length=150)
    url = models.URLField(unique=True)
    parse_task = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self) -> str:
        return f"{self.title}(#{self.id})"

@receiver(models.signals.post_delete, sender=Hub)
def delete_hub_parse_task(sender, instance: Hub, **kwargs):
    instance.parse_task.delete()

class ArticleAuthor(models.Model):
    username = models.CharField(max_length=150)
    url = models.URLField(unique=True)

    def __str__(self) -> str:
        return f"{self.username}(#{self.id})"

class Article(models.Model):
    title = models.CharField(max_length=250)
    text = models.TextField()
    url = models.URLField(unique=True)
    author = models.ForeignKey(ArticleAuthor, on_delete=models.CASCADE)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    published_at = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.title}(#{self.id})"

