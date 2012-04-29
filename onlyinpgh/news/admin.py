from django.contrib import admin
from onlyinpgh.news.models import Article

# renable after app has been added back to project
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'publication_date']

admin.site.register(Article, ArticleAdmin)
