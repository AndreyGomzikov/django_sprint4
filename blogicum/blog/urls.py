from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (IndexListView,
                    post_detail,
                    ProfileListView,
                    register,
                    CategoryPostsListView,
                    edit_profile,
                    create_post,
                    edit_post,
                    delete_post,
                    create_comment,
                    edit_comment,
                    delete_comment, custom_permission_denied_view,
                    custom_page_not_found_view,)

app_name = 'blog'

urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         CategoryPostsListView.as_view(), name='category_posts'),
    path('profile/<str:username>/', ProfileListView.as_view(), name='profile'),
    path('auth/registration/', register, name='registration'),
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

handler403 = custom_permission_denied_view
handler404 = custom_page_not_found_view

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
