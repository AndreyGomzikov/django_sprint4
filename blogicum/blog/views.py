from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.views.generic import ListView
from django.http import HttpResponse

from .forms import UserUpdateForm, PostUpdateForm, CommentUpdateForm
from .models import Post, Category, User, Comment


# Кастомные функции обработки ошибок
def custom_permission_denied_view(request, exception=None):
    print("403 Error: Permission Denied")
    return render(request, 'pages/403csrf.html', status=403)


def custom_page_not_found_view(request, exception=None):
    print("404 Error: Page Not Found")
    return render(request, 'pages/404.html', status=404)


def custom_server_error_view(request):
    print("500 Error: Server Error")
    return render(request, 'pages/500.html', status=500)


def get_published_posts(posts_queryset=Post.objects):
    return posts_queryset.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True
    ).select_related("category", "author", "location")


class IndexListView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(is_published=True,
                                       pub_date__lte=now(),
                                       category__is_published=True)
        return queryset


def post_detail(request, post_id):
    comment_form = CommentUpdateForm()
    comments = Comment.objects.filter(post=post_id)
    post = get_object_or_404(Post, id=post_id)
    if request.user.id == post.author.id:
        return render(request,
                      "blog/detail.html",
                      {"post": post,
                       'form': comment_form,
                       'comments': comments}
                      )
    elif not post.is_published or not post.category.is_published:
        return HttpResponse('Страница снята с публикации', status=404)
    return render(
        request, "blog/detail.html",
        {"post": get_object_or_404(get_published_posts(
        ), pk=post_id), 'form': comment_form, 'comments': comments}
    )


class CategoryPostsListView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        queryset = Post.objects.filter(
            category=category.id, pub_date__lte=now(), is_published=True)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug'], is_published=True)
        return context


class ProfileListView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        queryset = Post.objects.filter(author=user.id)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['profile'] = User.objects.get(username=self.kwargs['username'])
        return context


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST' and request.user.id == post.author.id:
        post_form = PostUpdateForm(request.POST, request.FILES, instance=post)
        if post_form.is_valid() and post.author.id == request.user.id:
            post_form.save()
            return redirect('blog:post_detail', int(post.id))
    else:
        if post.author.id != request.user.id:
            return redirect('blog:post_detail', int(post.id))
        post_form = PostUpdateForm(instance=post)
    return render(request, 'blog/create.html', {'form': post_form})


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST' and post.author.id == request.user.id:
        post.delete()
        return redirect('blog:index')
    else:
        if post.author != request.user:
            return redirect('blog:post_detail', int(post.id))
        post_form = PostUpdateForm(instance=post)
        return render(request, 'blog/create.html', {'form': post_form})


def create_comment(request, post_id):
    comment_form = CommentUpdateForm(request.POST)
    if comment_form.is_valid() and request.user.is_authenticated:
        comment = comment_form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()

        post = get_object_or_404(Post, id=post_id)
        post.comment_count += 1
        post.save()
    return redirect('blog:post_detail', post_id)


def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if (request.method == "POST" and request.user.is_authenticated
            and comment.author.id == request.user.id):
        comment_form = CommentUpdateForm(request.POST, instance=request.user)
        if comment_form.is_valid():
            comment.text = comment_form.cleaned_data['text']
            comment.save()
            return redirect('blog:post_detail', post_id)
    else:
        comment_form = CommentUpdateForm(instance=comment)
        return render(
            request,
            'blog/comment.html',
            {'form': comment_form, 'comment': comment}
        )


def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST' and comment.author.id == request.user.id:
        comment.delete()
        post = get_object_or_404(Post, id=post_id)
        post.comment_count -= 1
        post.save()
        return redirect('blog:post_detail', post_id)
    else:
        return render(request, 'blog/comment.html', {'comment': comment})


@login_required
def create_post(request):
    if request.method == 'POST':
        post_form = PostUpdateForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', request.user.username)
    else:
        post_form = PostUpdateForm()
    return render(request, 'blog/create.html', {'form': post_form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('blog:profile', request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        return render(request, 'blog/user.html', {'form': user_form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request,
                  'registration/registration_form.html', {'form': form}
                  )
