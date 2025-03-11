from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import UserUpdateForm, PostUpdateForm, CommentUpdateForm
from .models import Post, Category, User, Comment


PAGINATE_BY = 10


def get_published_posts(posts=Post.objects, filter_published=True,
                        select_related_fields=None):
    if filter_published:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        )

    if select_related_fields:
        posts = posts.select_related(*select_related_fields)

    return posts


class RegisterView(CreateView):
    template_name = "registration/registration_form.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        messages.success(self.request, f"Аккаунт создан для {username}!")
        return response


class IndexListView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY
    queryset = get_published_posts()


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        if not post.is_published:
            return HttpResponse("Страница снята с публикации", status=404)

        post = get_object_or_404(get_published_posts(), id=post_id)

    comment_form = CommentUpdateForm()
    comments = Comment.objects.filter(post=post)

    return render(
        request,
        "blog/detail.html",
        {"post": post, "form": comment_form, "comments": comments}
    )


class CategoryPostsListView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs["category_slug"],
            is_published=True
        )
        return get_published_posts(category.posts.all())

    def get_context_data(self, *, object_list=None, **kwargs):
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True)
        return super().get_context_data(**kwargs, category=category)


class ProfileListView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY

    def get_profile_user(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        profile_user = self.get_profile_user()
        if self.request.user == profile_user:
            return profile_user.posts.all()
        return get_published_posts(profile_user.posts.all())

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(
            **kwargs, profile=self.get_profile_user()
        )


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("blog:post_detail", post_id=post.id)

    post_form = PostUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )

    if post_form.is_valid():
        post_form.save()
        return redirect("blog:post_detail", post_id=post.id)

    return render(request, "blog/create.html", {"form": post_form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST" and post.author.id == request.user.id:
        post.delete()
        return redirect("blog:index")

    if post.author != request.user:
        return redirect("blog:post_detail", int(post.id))

    post_form = PostUpdateForm(instance=post)
    return render(request, "blog/create.html", {"form": post_form})


@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment_form = CommentUpdateForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        post.comment_count = post.comments.count()
        post.save()

    return redirect("blog:post_detail", post_id=post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id=post_id)

    comment_form = CommentUpdateForm(request.POST or None, instance=comment)

    if comment_form.is_valid():
        comment_form.save()
        return redirect("blog:post_detail", post_id=post_id)

    return render(request, "blog/comment.html", {"form": comment_form,
                                                 "comment": comment})


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST" and comment.author.id == request.user.id:
        comment.delete()
        return redirect("blog:post_detail", post_id)
    else:
        return render(request, "blog/comment.html", {"comment": comment})


@login_required
def create_post(request):
    post_form = PostUpdateForm(request.POST or None, request.FILES or None)
    if post_form.is_valid():
        post = post_form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", request.user.username)

    return render(request, "blog/create.html", {"form": post_form})


@login_required
def edit_profile(request):
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    if user_form.is_valid():
        user_form.save()
        return redirect("blog:profile", request.user.username)

    return render(request, "blog/user.html", {"form": user_form})
