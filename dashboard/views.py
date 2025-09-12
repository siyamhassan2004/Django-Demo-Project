from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Login_info_new_p,User_posts,User_comment,Like
from django.contrib import messages
from django.contrib.auth import logout
from .forms import UserPostsForm
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# Create your views here.
def demo(request):
    posts = User_posts.objects.all().order_by('-create_at')
    users = []
    U_posts = []
    U_ids = []
    likes_list = []

    for post in posts:
        # get user full name
        log_user = Login_info_new_p.objects.get(email=post.u_name)
        u_name = log_user.fname + " " + log_user.lname
        users.append(u_name)

        # store post info
        U_posts.append(post.post)
        U_ids.append(post.id)

        # count likes for this post
        likes_count = Like.objects.filter(post=post).count()
        likes_list.append(likes_count)

    # pass everything as zipped lists
    return render(request, "dashboard/landing_page.html", {"posts": zip(users, U_posts, U_ids, likes_list)})


def register(request):
    if request.session.get('user_id'):
        return redirect("home")
    else:
        if request.method == "POST":
            R_fname = request.POST.get("fname")
            R_lname = request.POST.get("lname")
            R_email = request.POST.get("email")
            R_password = request.POST.get("password")
            R_confirm_password = request.POST.get("confirm_password")
            
            if R_password != R_confirm_password:
                messages.error(request,"Password does not match")
                return redirect("register")

            if Login_info_new_p.objects.filter(email=R_email).exists():
                messages.error(request,"Email already exits")
                return redirect("register")

            else:
                new_user = Login_info_new_p.objects.create(fname=R_fname,lname=R_lname,email=R_email,password=R_password)
                new_user.save()
                messages.success(request,"Account Created.")
                return redirect("login")
        return render(request,"dashboard/login_signup.html",{})


def profile(request):
    # Get user email from session
    s_email = request.session.get('email')
    if not s_email:
        return render(request, "dashboard/landing_page.html", {"posts": []})
    
    log_user = get_object_or_404(Login_info_new_p, email=s_email)
    
    posts = User_posts.objects.filter(u_name=log_user).select_related('u_name')
    
    post_data = [
        (f"{log_user.fname} {log_user.lname}", post.post)
        for post in posts
    ]
    return render(request, "dashboard/profile.html", {"posts": post_data})

def login(request):
    if request.session.get('user_id'):
        return redirect("home")
    else:
        if request.method == "POST":
            u_email = request.POST.get("email")
            u_password = request.POST.get("password")
            try:
                logged_user = Login_info_new_p.objects.get(email=u_email,password=u_password)
                request.session['user_id'] = logged_user.id
                request.session["email"] = u_email
                request.session["name"] = logged_user.lname
                
                return redirect("home")
            except:
                messages.error(request,"Invalid Password or E-mail")
                # return render(request,"dashboard/login_signup.html",{})
                return redirect("login")
        else:
            return render(request,"dashboard/login_signup.html",{})
    
    
def logout_view(request):
    logout(request)
    return redirect("login")

def add_post(request):
    if request.method == "POST":
        form = UserPostsForm(request.POST)
        
        if form.is_valid():
            # return HttpResponse("Post Added Successfully.")
            post = form.save(commit=False)
            post.u_name = Login_info_new_p.objects.get(email=request.session.get('email'))
            post.save()
            return redirect("home")
    else:
        form = UserPostsForm()
    return HttpResponse("Post Was not Added.")

def add_comment(request, post_id):
    post = User_posts.objects.get(id=post_id)
    comments = post.comments.all().order_by("-created_at")
    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            user_email = request.session.get('email')
            if user_email:
                user = Login_info_new_p.objects.get(email=user_email)
                new_comment = User_comment(post=post, user=user, comment=comment_text)
                new_comment.save()
                return redirect("add_comment", post_id=post_id)
            else:
                return redirect("login")
    return render(request, "dashboard/comment.html", {"post": post, "comments": comments})

@require_POST
@csrf_exempt   # remove this if you already send CSRF via JS (recommended to keep CSRF)
def add_like(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        post_id = data.get("post_id")
        user_id = request.session.get("user_id")  # assuming you store user_id in session after login

        if not user_id:
            return JsonResponse({"success": False, "error": "User not logged in"}, status=403)

        post = User_posts.objects.get(id=post_id)
        user = Login_info_new_p.objects.get(id=user_id)

        # toggle like (if already liked, remove; else create)
        like, created = Like.objects.get_or_create(post=post, user=user)

        if not created:
            like.delete()
            return JsonResponse({"success": True, "liked": False, "likes_count": post.likes.count()})
        else:
            return JsonResponse({"success": True, "liked": True, "likes_count": post.likes.count()})

    except User_posts.DoesNotExist:
        return JsonResponse({"success": False, "error": "Post not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
