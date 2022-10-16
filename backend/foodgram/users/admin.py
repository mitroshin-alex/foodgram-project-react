from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class OwnUserAdmin(UserAdmin):
    # list_display = ('pk', 'username', 'email',
    #                 'first_name', 'last_name', 'password')
    # search_fields = ('email',)
    list_filter = ('email', 'username')
    # empty_value_display = '-пусто-'


admin.site.register(User, OwnUserAdmin)
