from django.urls import path
from . import views


app_name = 'posts'

CACHE_SEC = 0

urlpatterns = [
    path('', views.PostIndex.as_view(),
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
    path(
        'posts/<int:post_id>/like/',
        views.LikePost.as_view(),
        name='post_like'
    ),
    path(
        'posts/<int:post_id>/unlike/',
        views.UnlikePost.as_view(),
        name='post_unlike'
    ),
    path('posts/<int:post_id>/delete/', views.PostDelete.as_view(),
         name='post_delete'),
    path('posts/com/<int:comment_id>/delete/',
         views.CommentDelete.as_view(),
         name='comment_delete'),
    path('search/', views.PostTextSearch.as_view(), name='search')
]
