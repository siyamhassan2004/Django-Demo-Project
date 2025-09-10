from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class Login_info_new_p(models.Model):
    fname = models.CharField(max_length=100,default="Mr.")
    lname = models.CharField(max_length=100,default="Unknown") 
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    
    def __str__(self):
        return self.email
    

class User_posts(models.Model):
    id = models.AutoField(primary_key=True)
    u_name = models.ForeignKey(Login_info_new_p,on_delete=models.CASCADE)
    post = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.u_name)
    
    
class User_comment(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(User_posts, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(Login_info_new_p, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.comment)