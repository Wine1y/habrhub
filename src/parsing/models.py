from django.db import models


class Hub(models.Model):
    title = models.CharField(max_length=150)
    url = models.URLField(unique=True)
    parse_period = models.DurationField()

    def __str__(self) -> str:
        return self.title

class ArticleAuthor(models.Model):
    username = models.CharField(max_length=150)
    url = models.URLField()

    def __str__(self) -> str:
        return self.username

class Article(models.Model):
    title = models.CharField(max_length=250)
    text = models.TextField()
    url = models.URLField(unique=True)
    author = models.ForeignKey(ArticleAuthor, on_delete=models.CASCADE)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    published_at = models.DateTimeField()

    def __str__(self) -> str:
        return self.title

