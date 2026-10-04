from django import forms
from django.contrib.auth.forms import PasswordChangeForm
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


class UserSettingsForm(forms.ModelForm):
    role = RoleChoiceField(
        queryset=Group.objects.filter(name__in=ROLES),
        label='Rol',
        empty_label=None,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['role'].initial = self.instance.groups.filter(name__in=ROLES).first()
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.remove(*user.groups.filter(name__in=ROLES))
            user.groups.add(self.cleaned_data['role'])
        return user
