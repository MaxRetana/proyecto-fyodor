from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from .roles import ROLE_ADMINISTRATOR, ROLE_USER

PASSWORD = 'safe-password-123'


class UsersBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user('admin', password=PASSWORD)
        cls.admin.groups.add(Group.objects.get(name=ROLE_ADMINISTRATOR))
        cls.regular = User.objects.create_user('regular', password=PASSWORD)
        cls.regular.groups.add(Group.objects.get(name=ROLE_USER))


class RolesTests(TestCase):
    def test_migration_creates_groups(self):
        self.assertTrue(Group.objects.filter(name=ROLE_ADMINISTRATOR).exists())
        self.assertTrue(Group.objects.filter(name=ROLE_USER).exists())


class LoginTests(UsersBaseTestCase):
    def test_valid_login_redirects_to_home(self):
        response = self.client.post(reverse('login'), {'username': 'regular', 'password': PASSWORD})
        self.assertRedirects(response, reverse('home'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {'username': 'regular', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_views_require_login(self):
        for name in ('home', 'my-preferences', 'password-change', 'user-list', 'user-create'):
            url = reverse(name)
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_logout(self):
        self.client.force_login(self.regular)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class UserViewsTests(UsersBaseTestCase):
    def test_home_and_preferences(self):
        self.client.force_login(self.regular)
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        response = self.client.get(reverse('my-preferences'))
        self.assertContains(response, 'regular')
        self.assertContains(response, 'Usuario')

    def test_password_change(self):
        self.client.force_login(self.regular)
        response = self.client.post(reverse('password-change'), {
            'old_password': PASSWORD,
            'new_password1': 'another-password-456',
            'new_password2': 'another-password-456',
        })
        self.assertRedirects(response, reverse('my-preferences'))
        self.regular.refresh_from_db()
        self.assertTrue(self.regular.check_password('another-password-456'))


class AdministratorViewsTests(UsersBaseTestCase):
    def test_regular_user_is_denied(self):
        self.client.force_login(self.regular)
        self.assertEqual(self.client.get(reverse('user-list')).status_code, 403)
        self.assertEqual(self.client.get(reverse('user-settings', args=[self.admin.pk])).status_code, 403)

    def test_administrator_lists_users(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('user-list'))
        self.assertContains(response, 'regular')

    def test_administrator_edits_user_and_role(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user-settings', args=[self.regular.pk]), {
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'n@example.com',
            'is_active': 'on',
            'role': Group.objects.get(name=ROLE_ADMINISTRATOR).pk,
        })
        self.assertRedirects(response, reverse('user-list'))
        self.regular.refresh_from_db()
        self.assertEqual(self.regular.first_name, 'New')
        self.assertEqual([g.name for g in self.regular.groups.all()], [ROLE_ADMINISTRATOR])

    def test_administrator_creates_user_with_role(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user-create'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
            'role': Group.objects.get(name=ROLE_USER).pk,
        })
        self.assertRedirects(response, reverse('user-list'))
        created = User.objects.get(username='newuser')
        self.assertTrue(created.check_password(PASSWORD))
        self.assertEqual([g.name for g in created.groups.all()], [ROLE_USER])

    def _create_with_weak_password(self, **extra):
        self.client.force_login(self.admin)
        return self.client.post(reverse('user-create'), {
            'username': 'weak',
            'password1': '123',
            'password2': '123',
            'role': Group.objects.get(name=ROLE_USER).pk,
            **extra,
        })

    @override_settings(DEBUG=True)
    def test_weak_password_is_rejected_by_default(self):
        response = self._create_with_weak_password()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='weak').exists())

    @override_settings(DEBUG=True)
    def test_skip_password_validation_allows_weak_password(self):
        response = self._create_with_weak_password(skip_password_validation='on')
        self.assertRedirects(response, reverse('user-list'))
        self.assertTrue(User.objects.get(username='weak').check_password('123'))

    @override_settings(DEBUG=False)
    def test_skip_password_validation_is_ignored_outside_debug(self):
        response = self._create_with_weak_password(skip_password_validation='on')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='weak').exists())

    def test_regular_user_cannot_create_user(self):
        self.client.force_login(self.regular)
        self.assertEqual(self.client.get(reverse('user-create')).status_code, 403)


class BreadcrumbTests(UsersBaseTestCase):
    def test_breadcrumb_links_back_to_parents(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('user-settings', args=[self.regular.pk]))
        self.assertContains(response, 'breadcrumb-item')
        self.assertContains(response, f'href="{reverse("user-list")}">Usuarios</a>')
        self.assertContains(response, f'href="{reverse("home")}">Inicio</a>')

    def test_login_has_no_breadcrumb_items(self):
        response = self.client.get(reverse('login'))
        self.assertNotContains(response, 'breadcrumb-item')
