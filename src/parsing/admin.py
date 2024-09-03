from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Hub, ArticleAuthor, Article


class HubAdmin(admin.ModelAdmin):
    model = Hub
    list_display = ("title", "url_display", "parse_period", "id")
    search_fields = ("title", "url")
    sortable_by = ("id", "title", "parse_period")

    @admin.display(description="URL")
    def url_display(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.url)

class ArticleAuthorAdmin(admin.ModelAdmin):
    model = ArticleAuthor
    list_display = ("username", "url_display", "id")
    search_fields = ("username", "url")
    sortable_by = ("id", "username")

    @admin.display(description="URL")
    def url_display(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.url)

class ArticleAdmin(admin.ModelAdmin):
    model = Article
    list_display = ("title", "url_display", "author_display", "hub_display", "published_at", "id")
    search_fields = ("title", "text", "url")
    sortable_by = ("id", "title", "published_at")

    @admin.display(description="URL")
    def url_display(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.url)

    @admin.display(description="Author")
    def author_display(self, obj):
        author = obj.author
        author_url = reverse(f"admin:{author._meta.app_label}_{author._meta.model_name}_change", args=[author.id])
        return format_html("<a href='{url}'>{username}</a>", url=author_url, username=author.username)

    @admin.display(description="Hub")
    def hub_display(self, obj):
        hub = obj.hub
        hub_url = reverse(f"admin:{hub._meta.app_label}_{hub._meta.model_name}_change", args=[hub.id])
        return format_html("<a href='{url}'>{title}</a>", url=hub_url, title=hub.title)

    autocomplete_fields = ("hub", "author")

admin.site.register(Hub, HubAdmin)
admin.site.register(ArticleAuthor, ArticleAuthorAdmin)
admin.site.register(Article, ArticleAdmin)
