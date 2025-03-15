from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import ListView
from django.db.models import Count

from .forms import UserUpdateForm, PostUpdateForm, CommentUpdateForm
from .models import Post, Category, User, Comment

PAGINATE_BY = 10


def get_available_post(post_id, user):
    post = get_object_or_404(Post, id=post_id)
    if (not (post.is_published
             and post.pub_date <= now()
             and post.category.is_published)
            and post.author != user):
        raise Http404("Страница снята с публикации")
    return post


def get_filtered_posts(posts=Post.objects, filter_published=True):
    if filter_published:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        )
    posts = posts.select_related('author', 'category').annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    return posts


class IndexListView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY
    queryset = get_filtered_posts()


def post_detail(request, post_id):
    post = get_available_post(post_id, request.user)

    return render(request, "blog/detail.html", {
        "post": post,
        "form": CommentUpdateForm(),
        "comments": post.comments.all(),
    })


class CategoryPostsListView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs["category_slug"],
            is_published=True
        )

    def get_queryset(self):
        return get_filtered_posts(self.get_category().posts.all())

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(**kwargs) | {
            'category': self.get_category()
        }


class ProfileListView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "posts"
    paginate_by = PAGINATE_BY

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_queryset(self):
        author = self.get_author()
        posts = author.posts.all()

        if self.request.user != author:
            posts = get_filtered_posts(posts)

        posts = posts.select_related('author', 'category').annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

        return posts

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(**kwargs, profile=self.get_author())


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("blog:post_detail", post_id=post.id)

    form = PostUpdateForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post.id)

    return render(request, "blog/create.html", {"form": form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post.id)
    if request.method == "POST":
        post.delete()
        return redirect("blog:index")
    return render(request, "blog/create.html", {"post": post})


@login_required
def create_comment(request, post_id):
    comment_form = CommentUpdateForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.author = request.user
        post = get_object_or_404(Post, id=post_id)
        comment.post = post
        comment.save()
        return redirect("blog:post_detail", post_id=post.id)

    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id)

    form = CommentUpdateForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)

    return render(request, "blog/comment.html", {"form": form,
                                                 "comment": comment})


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST" and comment.author.id == request.user.id:
        comment.delete()
        return redirect("blog:post_detail", post_id)

    return render(request, "blog/comment.html", {"comment": comment})


@login_required
def create_post(request):
    post_form = PostUpdateForm(request.POST or None, request.FILES or None)
    if not post_form.is_valid():
        return render(request, "blog/create.html", {"form": post_form})

    post = post_form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("blog:profile", request.user.username)


@login_required
def edit_profile(request):
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    if user_form.is_valid():
        user_form.save()
        return redirect("blog:profile", request.user.username)

    return render(request, "blog/user.html", {"form": user_form})
