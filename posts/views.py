from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group
from django.contrib.auth.models import User
from .forms import PostForm
from django.core.paginator import Paginator
from django.http import HttpResponse


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "index.html",
                  {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date")[:10]
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "group.html",
                  {"group": group, "page": page, "paginator": paginator})


@login_required
def new_post(request):

    next_url = request.GET.get("next")

    next_param = ""
    if next_url:
        next_param = "?next="+next_url

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
                
            return redirect(reverse("index"))

        return render(request, "new_post.html", 
                      {"form": form, "mode": "add", "next_param": next_param})

    form = PostForm()
    return render(request, "new_post.html",
                  {"form": form, "mode": "add", "next_param": next_param})


def profile(request, username):
    user = get_object_or_404(User, username=username)

    post_list = Post.objects.filter(author=user).order_by("-pub_date")
    post_count = len(post_list)

    profile_info = {"user": user, "post_count": post_count}

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request, "profile.html",
        {"page": page, "paginator": paginator, "profile_info": profile_info}
        )


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user).order_by("-pub_date")
    post_count = post_list.count()

    try:
        post = post_list[post_id-1]
    except IndexError:
        return HttpResponse(status=404)

    profile_info = {"user": user, "post_count": post_count}
    return render(
            request, "post.html",
            {"profile_info": profile_info, "post": post, "post_id": post_id}
        )


@login_required
def post_edit(request, username, post_id):

    user = get_object_or_404(User, username=username)

    if request.user != user:
        return HttpResponse(status=403)

    try:
        post = Post.objects.filter(author=user).order_by("-pub_date")[post_id-1]
    except IndexError:
        return HttpResponse(status=404)

    # Form a next page param string
    next_url = request.GET.get("next")
    next_param = ""
    if next_url:
        next_param = "?next="+next_url

    if request.method == "POST":
        form = PostForm(request.POST or None, instance=post)

        if form.is_valid():
            next_url = request.GET.get("next")
            form.save()
            if next_url:
                return redirect(next_url)
            return redirect("/"+username)

        context = {
            "form": form,
            "mode": "edit",
            "post_id": post_id,
            "next_param": next_param
        }
        return render(request, "new_post.html", context)

    form = PostForm(instance=post)

    context = {
        "form": form,
        "mode": "edit",
        "post_id": post_id,
        "next_param": next_param
    }
    return render(request, "new_post.html", context)