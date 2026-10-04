from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView

from .forms import StyledPasswordChangeForm, UserSettingsForm
from .roles import is_administrator


class AdministratorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_administrator(self.request.user)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'users/home.html'


class MyPreferencesView(LoginRequiredMixin, TemplateView):
    template_name = 'users/my_preferences.html'


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('my-preferences')

    def form_valid(self, form):
        messages.success(self.request, 'Contraseña actualizada correctamente.')
        return super().form_valid(form)


class UserListView(AdministratorRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    queryset = User.objects.prefetch_related('groups').order_by('username')


class UserSettingsView(AdministratorRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsForm
    template_name = 'users/user_settings.html'
    success_url = reverse_lazy('user-list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado correctamente.')
        return super().form_valid(form)
