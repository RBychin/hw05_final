from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from .forms import CreationForm, UserUpdateForm
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class UserEditor(UpdateView):
    model = User
    template_name = 'users/user_edit.html'
    extra_context = {'is_edit': True}
    form_class = UserUpdateForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None,
                               instance=request.user
                               )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
        return redirect(
            'users:info_last'
        )

    def get_object(self, queryset=None):
        print(User.objects.get(username=self.request.user.username))
        user = User.objects.get(username=self.request.user.username)
        return user

