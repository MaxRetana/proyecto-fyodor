ROLE_ADMINISTRATOR = 'Administrator'
ROLE_USER = 'User'
ROLES = (ROLE_ADMINISTRATOR, ROLE_USER)

# Names shown to the end user (Spanish)
ROLE_LABELS = {
    ROLE_ADMINISTRATOR: 'Administrador',
    ROLE_USER: 'Usuario',
}


def is_administrator(user):
    """An administrator is a superuser or a member of the Administrator group."""
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=ROLE_ADMINISTRATOR).exists()
    )
