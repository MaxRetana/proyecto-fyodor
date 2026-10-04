from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import StyledPasswordChangeForm, UserCreateForm, UserSettingsForm
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
    search_fields = ('username', 'first_name', 'last_name', 'email')

    def get_queryset(self):
        queryset = super().get_queryset()
        # Every word must match at least one field, so "john doe" finds first + last name
        for term in self.request.GET.get('q', '').split():
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': term})
            queryset = queryset.filter(query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class UserSettingsView(AdministratorRequiredMixin, UpdateView):
    model = User
    form_class = UserSettingsForm
    template_name = 'users/user_settings.html'
    success_url = reverse_lazy('user-list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado correctamente.')
        return super().form_valid(form)


class UserCreateView(AdministratorRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'users/user_create.html'
    success_url = reverse_lazy('user-list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente.')
        return super().form_valid(form)
