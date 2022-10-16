from django.contrib import admin

from .models import Tag, Subscription


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
