from django.contrib import admin
from .models import Website, Cultivator, Post


class WebsiteAdmin(admin.ModelAdmin):

    list_display = [
        'domain',
    ]


class CultivatorAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'number',
        'is_trusted',
        'website_id',
    ]

    def has_change_permission(self, request, obj=None):
        return False


class PostAdmin(admin.ModelAdmin):

    list_display = [
        'author_id',
        'post_num',
        'body_head',
        'get_url',
        'date',
    ]

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Website, WebsiteAdmin)
admin.site.register(Cultivator, CultivatorAdmin)
admin.site.register(Post, PostAdmin)