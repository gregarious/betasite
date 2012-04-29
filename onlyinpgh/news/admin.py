from django.contrib import admin
from onlyinpgh.news.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'publication_date']

admin.site.register(Article, ArticleAdmin)
