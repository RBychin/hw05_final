from datetime import datetime

from django.shortcuts import get_object_or_404, redirect
from .models import Post, Group, User, Follow, Comment, Like
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm, CommentForm
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    FormView,
    View
)

P_COUNT = 10  # количество постов для пагинатора


class DataMixin:
    """Поключает пагинатор"""
    model = Post
    paginate_by = P_COUNT


class PostIndex(DataMixin, ListView):
    """Главная страница."""
    template_name = 'posts/index.html'

    def get_queryset(self):
        return Post.objects.select_related('author', 'group')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostIndex, self).get_context_data(**kwargs)
        context['form'] = PostForm
        return context

    def post(self, request):
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = self.request.user
            obj.save()
        return redirect(
            'posts:profile', request.user)


class PostGroup(DataMixin, ListView):
    """Страница с постами группы."""
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        group = get_object_or_404(Group, slug=self.kwargs.get('slug'))
        return Post.objects.filter(
            group=group
        ).select_related('author', 'group').all()


class PostProfile(DataMixin, ListView):
    """Страница с постами пользователя."""
    template_name = 'posts/profile.html'
    author: str

    def get_queryset(self):
        self.author = get_object_or_404(
            User, username=self.kwargs.get('username'))
        return Post.objects.filter(
            author=self.author
        ).select_related('author', 'group')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        if self.request.user.is_authenticated:
            context['following'] = Follow.objects.filter(
                user=self.request.user, author=self.author
            ).exists()
        return context


class PostDetail(DetailView):
    """Страница поста."""
    model = Post
    template_name = 'posts/post_detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        post = get_object_or_404(
            Post, pk=self.kwargs['post_id'])
        context = {
            'form': PostForm(self.request.POST or None,
                             files=self.request.FILES or None,
                             instance=post),
            'comments_form': CommentForm(self.request.POST or None),
            'comments': post.comments.all().select_related('author', ),
            'post': post,
            'following': Follow.objects.filter(
                user=self.request.user, author=post.author
            ).exists() if self.request.user.is_authenticated else False
        }
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post
                        )
        if form.is_valid() and request.user == post.author:
            obj = form.save(commit=False)
            obj.edit_date = datetime.now()
            obj.save()
        return redirect(
            'posts:post_detail', kwargs.get('post_id')
        )


class PostCreate(LoginRequiredMixin, CreateView):
    """Страница создания поста."""
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return redirect('posts:profile', self.request.user)

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post

class PostCommentAdd(LoginRequiredMixin, FormView):
    """Форма добавления комментария."""
    form_class = CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment.save()
        return redirect('posts:post_detail', post_id=self.kwargs['post_id'])

    def get(self, request, *args, **kwargs):
        return redirect('posts:post_detail', post_id=self.kwargs['post_id'])


class FollowIndex(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'posts/follow_index.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)


class ProfileFollow(LoginRequiredMixin, View):
    def get(self, request, username):
        user = request.user
        author = get_object_or_404(User, username=username)
        is_follower = Follow.objects.filter(user=user, author=author)
        if user != author and not is_follower.exists():
            Follow.objects.create(user=user, author=author)
        return redirect(request.META.get('HTTP_REFERER'))


class ProfileUnfollow(LoginRequiredMixin, View):
    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        is_follower = Follow.objects.filter(user=request.user, author=author)
        is_follower.delete()
        return redirect(request.META.get('HTTP_REFERER'))


class PostDelete(View):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        if post.author != request.user:
            return redirect(request.META.get('HTTP_REFERER'))
        post.delete()
        return redirect(request.META.get('HTTP_REFERER'))


class CommentDelete(View):
    def get(self, request, comment_id):
        """Функция удаления комментария."""
        comment = Comment.objects.get(id=comment_id)
        if comment.author != request.user:
            return redirect(request.META.get('HTTP_REFERER'))
        comment.delete()
        return redirect(request.META.get('HTTP_REFERER'))


class PostTextSearch(DataMixin, ListView):
    template_name = 'posts/search.html'

    def get_queryset(self):
        return Post.objects.filter(text__contains=self.get_object())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.get_object()
        return context

    def get_object(self):
        search_query = self.request.GET.get('search', )
        return search_query


class LikePost(LoginRequiredMixin, View):
    def get(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        is_liked = Like.objects.filter(user=user, post=post)
        if not is_liked.exists():
            Like.objects.create(user=user, post=post)
        return redirect(request.META.get('HTTP_REFERER'))


class UnlikePost(LoginRequiredMixin, View):
    def get(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        is_liked = Like.objects.filter(user=user, post=post)
        is_liked.delete()
        return redirect(request.META.get('HTTP_REFERER'))
