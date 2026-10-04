from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User

from .roles import ROLE_LABELS, ROLES


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class RoleChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return ROLE_LABELS.get(obj.name, obj.name)


def apply_bootstrap_classes(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs['class'] = 'form-check-input'
        else:
            field.widget.attrs['class'] = 'form-control'


def role_field():
    return RoleChoiceField(
        queryset=Group.objects.filter(name__in=ROLES),
        label='Rol',
        empty_label=None,
    )


class UserCreateForm(UserCreationForm):
    role = role_field()
    skip_password_validation = forms.BooleanField(
        required=False,
        label='Omitir validación de contraseña (solo para usuarios de prueba)',
    )

    field_order = [
        'username', 'first_name', 'last_name', 'email', 'role',
        'skip_password_validation', 'password1', 'password2',
    ]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The bypass only exists in development
        if not settings.DEBUG:
            del self.fields['skip_password_validation']
        apply_bootstrap_classes(self)

    def validate_password_for_user(self, user, **kwargs):
        if self.cleaned_data.get('skip_password_validation'):
            return
        super().validate_password_for_user(user, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.add(self.cleaned_data['role'])
        return user


class UserSettingsForm(forms.ModelForm):
    role = role_field()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['role'].initial = self.instance.groups.filter(name__in=ROLES).first()
        apply_bootstrap_classes(self)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.remove(*user.groups.filter(name__in=ROLES))
            user.groups.add(self.cleaned_data['role'])
        return user
