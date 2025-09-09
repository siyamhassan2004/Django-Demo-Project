from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import friend_list,friend_request

# Register your models here.
admin.site.register(friend_request)
admin.site.register(friend_list)
