from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/password_change/', auth_views.PasswordChangeView.as_view(),
         name='password_change'),
]

handler404 = 'pages.views.custom404'
handler500 = 'pages.views.custom500'
handler403 = 'pages.views.custom403'
