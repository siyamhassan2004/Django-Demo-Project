from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Login_info_new_p,User_posts,User_comment,Like
# Register your models here.
admin.site.register(Login_info_new_p)
admin.site.register(User_posts)
admin.site.register(User_comment)
admin.site.register(Like)