from typing import List
from datetime import timezone

from celery import shared_task
from asgiref.sync import async_to_sync

from .parser import HabrParser, ParsedArticle
from .models import Hub, Article, ArticleAuthor


async def parse_hub(hub_url: str) -> List[ParsedArticle]:
    async with HabrParser() as parser:
        return await parser.parse_hub_articles(hub_url)

@shared_task
def parse_hub_task(hub_id: int):
    hub = Hub.objects.get(id=hub_id)
    parsed_articles = async_to_sync(parse_hub)(hub.url)

    authors = ArticleAuthor.objects.bulk_create(
        [
            ArticleAuthor(
                username=parsed_article.author.username,
                url=parsed_article.author.url,
            )
        for parsed_article in parsed_articles
        ],
        update_conflicts=True,
        update_fields=["username"],
        unique_fields=["url"]
    )

    Article.objects.bulk_create(
        [
            Article(
                title=parsed_article.title,
                text=parsed_article.text,
                url=parsed_article.url,
                author=authors[i],
                hub=hub,
                published_at=parsed_article.published_at.replace(tzinfo=timezone.utc)
            )
            for i, parsed_article in enumerate(parsed_articles)
        ],
        update_conflicts=True,
        update_fields=["title", "text"],
        unique_fields=["url"]
    )