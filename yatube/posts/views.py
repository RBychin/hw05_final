from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    FormView,
    # DeleteView,
    View
)

P_COUNT = 10  # количество постов для пагинатора


class DataMixin:
    """Поключает пагинатор"""
    model = Post
    paginate_by = P_COUNT


class FollowMixin:
    """Формирует контекст с количеством и списком подписчиков"""
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['count_follow'] = Follow.objects.filter(
                user=self.request.user).count()
            context['count'] = Post.objects.filter(
                author__following__user=self.request.user
            ).count()
        return context

    def follows(self, **kwargs):
        follow = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        user = post.author
        follow['follows'] = Follow.objects.filter(
            user=user)
        return follow


class PostIndex(DataMixin, ListView):
    """Главная страница."""
    template_name = 'posts/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = Post.objects.all().count()
        return context

    def get_queryset(self):
        return Post.objects.select_related('author', 'group')


class PostGroup(DataMixin, ListView):
    """Страница с постами группы."""
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        return Post.objects.filter(
            group__slug=self.kwargs['slug']
        ).select_related('author', 'group')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = group = Group.objects.get(slug=self.kwargs['slug'])
        context['count'] = Post.objects.filter(group=group).count()
        return context


class PostProfile(DataMixin, ListView):
    """Страница с постами пользователя."""
    template_name = 'posts/profile.html'

    def get_queryset(self):
        super().get_queryset()
        return Post.objects.filter(
            author__username=self.kwargs['username']
        ).select_related('author', 'group')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        author = User.objects.get(
            username=self.kwargs['username'])
        context['author'] = author
        context['count'] = Post.objects.filter(author=author).count()
        if self.request.user.is_authenticated:
            following = Follow.objects.filter(
                user=self.request.user, author=author
            ).exists()
        else:
            following = False
        context['following'] = following
        return context


class PostDetail(FollowMixin, DetailView):
    """Страница поста."""
    model = Post
    template_name = 'posts/post_detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = CommentForm(self.request.POST or None)
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        count = post.author.posts.all().count
        comments = post.comments.all()
        author = post.author
        context['count'] = Post.objects.filter(author=author).count()
        if self.request.user.is_authenticated:
            following = Follow.objects.filter(
                user=self.request.user, author=author
            ).exists()
        else:
            following = False

        context.update({
            'count': count,
            'form': form,
            'comments': comments,
            'post': post,
            'following': following,
        })
        follows = self.follows()
        context = {**context, **follows}
        return context


@method_decorator(login_required, name='dispatch')
class PostCreate(CreateView):
    """Страница создания поста."""
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return redirect('posts:profile', self.request.user)


@method_decorator(login_required, name='dispatch')
class PostEdit(UpdateView):
    """Страница редактирования поста."""
    form_class = PostForm
    template_name = 'posts/create_post.html'
    extra_context = {'is_edit': True}

    def get(self, request, **kwargs):
        post = Post.objects.get(pk=self.kwargs['post_id'])
        if post.author == self.request.user:
            return UpdateView.get(self, self.request, self.kwargs)
        else:
            return redirect(
                'posts:post_detail', self.kwargs['post_id']
            )

    def get_object(self, queryset=None):
        post = Post.objects.get(pk=self.kwargs['post_id'])
        return post

    def get_success_url(self):
        return reverse_lazy(
            'posts:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


@method_decorator(login_required, name='dispatch')
class PostCommentAdd(FormView):
    """Форма добавления комментария."""
    form_class = CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = Post.objects.get(pk=self.kwargs['post_id'])
        comment.save()
        return redirect('posts:post_detail', post_id=self.kwargs['post_id'])


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


@method_decorator(login_required, name='dispatch')
class FollowIndex(DataMixin, FollowMixin, ListView):
    template_name = 'posts/follow_index.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(author__following__user=self.request.user)


@method_decorator(login_required, name='dispatch')
class ProfileFollow(View):
    def get(self, request, username):
        user = self.request.user
        author = User.objects.get(username=username)
        is_follower = Follow.objects.filter(user=user, author=author)
        if user != author and not is_follower.exists():
            Follow.objects.create(user=user, author=author)
        # return redirect(request.META.get('HTTP_REFERER'))
        return redirect(reverse(
            'posts:profile',
            args=(self.kwargs.get('username'),)
        ))


@method_decorator(login_required, name='dispatch')
class ProfileUnfollow(View):
    def get(self, request, username):
        author = get_object_or_404(User, username=username)
        is_follower = Follow.objects.filter(user=request.user, author=author)
        if is_follower.exists():
            is_follower.delete()
        return redirect(reverse(
            'posts:profile',
            args=(self.kwargs.get('username'),)
        ))
