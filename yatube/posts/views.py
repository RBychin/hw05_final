from django.shortcuts import get_object_or_404, redirect
from .models import Post, Group, User, Follow
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
            'form': CommentForm(self.request.POST or None),
            'comments': post.comments.all().select_related('author', 'post'),
            'post': post,
            'count': Post.objects.filter(author=post.author).count()
        }
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    """Страница создания поста."""
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return redirect('posts:profile', self.request.user)


class PostEdit(LoginRequiredMixin, UpdateView):
    """Страница редактирования поста."""
    form_class = PostForm
    template_name = 'posts/create_post.html'
    extra_context = {'is_edit': True}

    def get(self, request, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'posts:post_detail', kwargs.get('post_id')
            )
        return super().get(request, **kwargs)

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = self.form_class(request.POST or None,
                               files=request.FILES or None,
                               instance=post
                               )
        if form.is_valid() and request.user == post.author:
            obj = form.save(commit=False)
            obj.author = self.request.user
            obj.save()
        return redirect(
            'posts:post_detail', kwargs.get('post_id')
        )

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
        return redirect(reverse(
            'posts:profile',
            args=(username,)
        ))


class ProfileUnfollow(LoginRequiredMixin, View):
    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        is_follower = Follow.objects.filter(user=request.user, author=author)
        is_follower.delete()
        return redirect(reverse(
            'posts:profile',
            args=(username,)
        ))
