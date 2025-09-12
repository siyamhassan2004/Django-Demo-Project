from django.urls import path
from . import views


urlpatterns = [
    path('dash/',views.demo,name="home"),
    path('profile/',views.profile,name="mypost"),
    
    path('login/',views.login,name="login"),
    path('logout/',views.logout_view,name="logout"),
    path('register/',views.register,name="register"),
    
    path('add_post/',views.add_post,name="add_post"),
    path('delete_post/<int:post_id>/',views.delete_post,name="delete_post"),
    path('edit_post/<int:post_id>/',views.edit_post,name="edit_post"),

    path('add_comment/<int:post_id>/', views.add_comment, name="add_comment"),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name="delete_comment"),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name="edit_comment"),
    
    path('add_like/', views.add_like, name="add_like"),

]