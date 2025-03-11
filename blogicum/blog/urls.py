from django.urls import path
from .views import RegisterView


from .views import (
    IndexListView,
    post_detail,
    ProfileListView,
    CategoryPostsListView,
    edit_profile,
    create_post,
    edit_post,
    delete_post,
    create_comment,
    edit_comment,
    delete_comment,
)

app_name = 'blog'

urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         CategoryPostsListView.as_view(), name='category_posts'),
    path('profile/<str:username>/', ProfileListView.as_view(), name='profile'),
    path('auth/registration/', RegisterView.as_view(), name='registration'),
    path('profile/edit', edit_profile, name='edit_profile'),
    path('posts/create/', create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('posts/<int:post_id>/comment/', create_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         delete_comment, name='delete_comment'),
]
