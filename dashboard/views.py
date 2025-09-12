from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseForbidden
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
    U_id = request.session.get('user_id')
    posts = User_posts.objects.all().order_by('-create_at')

    post_data = []
    for post in posts:
        log_user = post.u_name
        post_data.append({
            "id": post.id,
            "name": f"{log_user.fname} {log_user.lname}",
            "post": post.post,
            "likes": Like.objects.filter(post=post).count(),
            "comments": User_comment.objects.filter(post=post).count(),
            "is_owner": (U_id == log_user.id),  # True/False
        })

    return render(request, "dashboard/landing_page.html", {"posts": post_data})






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
            post = form.save(commit=False)
            post.u_name = Login_info_new_p.objects.get(email=request.session.get('email'))
            post.save()
            return redirect("home")
    else:
        form = UserPostsForm()
    return HttpResponse("Post Was not Added.")



def edit_post(request, post_id):
    post = get_object_or_404(User_posts, id=post_id)

    # Get current logged-in user from session
    current_user_id = request.session.get('user_id')
    if not current_user_id:
        return redirect('login')  # Not logged in

    current_user = Login_info_new_p.objects.get(id=current_user_id)

    # Check ownership
    if post.u_name != current_user:
        return HttpResponseForbidden("You can't edit this post.")

    if request.method == 'POST':
        new_content = request.POST.get('post')
        post.post = new_content
        post.save()
        return redirect('home')

    return render(request, 'dashboard/edit_post.html', {'post': post})


def delete_post(request, post_id):
    post = get_object_or_404(User_posts, id=post_id)

    # Get current logged-in user from session
    current_user_id = request.session.get('user_id')
    if not current_user_id:
        return redirect('login')  # Not logged in

    current_user = Login_info_new_p.objects.get(id=current_user_id)

    # Check ownership
    if post.u_name != current_user:
        return HttpResponseForbidden("You can't delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return redirect('home')





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



# Delete comment
def delete_comment(request, comment_id):
    comment = get_object_or_404(User_comment, id=comment_id)
    post_id = comment.post.id

    # Optional: Only allow the comment owner to delete
    user_email = request.session.get("email")
    if user_email and comment.user.email == user_email:
        comment.delete()
    
    return redirect("add_comment", post_id=post_id)

# Edit comment
def edit_comment(request, comment_id):
    comment = get_object_or_404(User_comment, id=comment_id)
    post_id = comment.post.id

    # Only allow comment owner to edit
    user_email = request.session.get("email")
    if not (user_email and comment.user.email == user_email):
        return redirect("add_comment", post_id=post_id)

    if request.method == "POST":
        new_text = request.POST.get("comment")
        if new_text:
            comment.comment = new_text
            comment.save()
            return redirect("add_comment", post_id=post_id)

    return render(request, "dashboard/edit_comment.html", {"comment": comment})


@require_POST
@csrf_exempt   
def add_like(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        post_id = data.get("post_id")
        user_id = request.session.get("user_id") 

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