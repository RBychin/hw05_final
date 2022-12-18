from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordChangeView
)
from django.views.generic import TemplateView
from .views import UserEditor
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(
            template_name='users/logged_out.html'
        ),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        LoginView.as_view(
            template_name='users/login.html'
        ),
        name='login'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password_change/done/',
        PasswordChangeView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    # path('info/', TemplateView.as_view(
    #     template_name='users/includes/info_last.html',
    # ),
    #      name='info_last'
    #      ),
    path('info/', views.UserInfo.as_view(), name='info_last'),
    path('user/edit/', UserEditor.as_view(), name='user_edit'),
    path('info/comments/', TemplateView.as_view(
        template_name='users/includes/info_comments.html'
    ), name='info_comments'),
    path('info/posts/', TemplateView.as_view(
        template_name='users/includes/info_posts.html'
    ), name='info_posts'),
    path('info/likes/', TemplateView.as_view(
        template_name='users/includes/info_likes.html'
    ), name='info_likes'),
]
