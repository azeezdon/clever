from django.contrib import admin
from .models import Comment, Post
from mptt.admin import MPTTModelAdmin
from metatags.admin import MetaTagInline
from metatags.admin import MetaTagAbleMixin


class CustomModelAdmin(admin.ModelAdmin):
    inlines = (MetaTagInline,)


@admin.register(Post)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'status', 'slug', 'author')
    prepopulated_fields = {'slug': ('title',), }


admin.site.register(Comment, MPTTModelAdmin)
