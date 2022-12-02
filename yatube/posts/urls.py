from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

app_name = 'posts'

CACHE_SEC = 20

urlpatterns = [
    path('', cache_page(CACHE_SEC)(views.PostIndex.as_view()),
         name='index'),
    path('group/<slug:slug>/',
         views.PostGroup.as_view(),
         name='group_list'),
    path('profile/<str:username>/',
         views.PostProfile.as_view(),
         name='profile'),
    path('posts/<int:post_id>/', views.PostDetail.as_view(),
         name='post_detail'),
    path('create/', views.PostCreate.as_view(),
         name='post_create'),
    path('posts/<int:post_id>/edit/', views.PostEdit.as_view(),
         name='post_edit'),
    path('posts/<int:post_id>/comment/',
         views.PostCommentAdd.as_view(),
         name='add_comment'),
    path('follow/', views.FollowIndex.as_view(),
         name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.ProfileFollow.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnfollow.as_view(),
        name='profile_unfollow'
    ),
]
