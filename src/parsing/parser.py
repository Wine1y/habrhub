import asyncio
from typing import List
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag


MAX_PARALLEL_REQUESTS = 3

@dataclass
class ParsedArticleAuthor:
    username: str
    url: str

@dataclass
class ParsedArticle:
    title: str
    text: str
    url: str
    hub_url: str
    author: ParsedArticleAuthor
    published_at: datetime


class HabrParser:
    base_url: str = "https://habr.com/"
    session: ClientSession
    request_semaphore: asyncio.Semaphore

    async def parse_hub_article_urls(self, hub_url: str) -> List[str]:
        if not hub_url.endswith('/'):
            hub_url = hub_url + '/'
        soup = await self._get_page_soup(urljoin(hub_url, "articles"))

        return [
            urljoin(self.base_url, a.attrs['href'])
            for a in soup.select("div.tm-articles-list article a.tm-title__link")
            if "href" in a.attrs
        ]
    
    async def parse_article(self, article_url: str, hub_url: str) -> ParsedArticle:
        soup = await self._get_page_soup(article_url)
        article_tag = soup.select_one("div.tm-article-presenter")
        author_tag = article_tag.select_one("a.tm-user-info__username")
        time_tag = article_tag.select_one("span.tm-article-datetime-published time")

        author = ParsedArticleAuthor(
            username=self._get_tag_text(author_tag),
            url=urljoin(self.base_url, author_tag.attrs.get('href'))
        )

        return ParsedArticle(
            title=self._get_tag_text(article_tag.select_one("h1.tm-title")),
            text=self._get_tag_text(article_tag.select_one("div.article-formatted-body")),
            url=article_url,
            hub_url=hub_url,
            author=author,
            published_at=datetime.strptime(time_tag.attrs["datetime"], r"%Y-%m-%dT%H:%M:%S.%fZ")
        )
    
    async def parse_hub_articles(self, hub_url: str) -> List[ParsedArticle]:
        article_urls = await self.parse_hub_article_urls(hub_url)
        return await asyncio.gather(*[
            self.parse_article(article_url, hub_url)
            for article_url in article_urls
        ])
    
    async def _get_page_soup(self, url: str) -> BeautifulSoup:
        async with self.request_semaphore:
            resp = await self.session.get(url)
        return BeautifulSoup(await resp.text(), features="lxml")
    
    def _get_tag_text(self, tag: Tag | None) -> str | None:
        if tag is None:
            return None
        return tag.text.replace('\xa0', ' ').strip("\r\n\t ")
    
    async def __aenter__(self):
        self.session = ClientSession()
        self.request_semaphore = asyncio.Semaphore(MAX_PARALLEL_REQUESTS)
        return self

    async def __aexit__(self, *_excinfo):
        await self.session.close()
