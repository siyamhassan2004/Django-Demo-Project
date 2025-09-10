from django import forms
from .models import User_posts,Login_info_new_p

class UserPostsForm(forms.ModelForm):
    class Meta:
        model = User_posts
        fields = ['post']