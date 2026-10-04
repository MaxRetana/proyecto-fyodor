# proyecto-fyodor

Proyecto web construido con [Django](https://www.djangoproject.com/) 5.2.

## Requisitos

- Python 3.10 o superior
- pip
- Git

## Instalación

```bash
git clone <url-del-repo>
cd proyecto-fyodor

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
```

## Levantar el servidor

```bash
source .venv/bin/activate
python manage.py runserver
```

Abrir http://127.0.0.1:8000.

## Comandos útiles

| Comando | Para qué sirve |
|---|---|
| `python manage.py startapp nombre` | Crear una app |
| `python manage.py makemigrations` | Generar migraciones tras cambiar modelos |
| `python manage.py migrate` | Aplicar migraciones |
| `python manage.py createsuperuser` | Crear usuario para `/admin` |
| `python manage.py test` | Correr las pruebas |

## Estructura

```text
proyecto-fyodor/
├── .github/        # Workflows de CI y plantillas de issues y PR
├── config/         # Configuración del proyecto (settings, urls, wsgi, asgi)
├── users/          # Login, roles, preferencias y administración de usuarios
├── manage.py
└── requirements.txt
```

## Usuarios y roles

- `/login/`, `/logout/`, `/password-change/`, `/my-preferences/` y `/` (inicio) requieren sesión.
- Roles (grupos creados por migración): `Administrator` y `User`. Los administradores (o superusuarios) acceden a `/users/` y `/settings/<id>/` para ver y editar a los demás usuarios.
- Para el primer acceso: `python manage.py createsuperuser`.

## Flujo de trabajo

Ramas de integración: `develop` → `test` → `main`. Los workflows de `.github/workflows/` crean y mergean los PR automáticos entre ellas al hacer push.

- Las ramas de trabajo salen de `develop` y siguen el formato `<tipo>/<numero-issue>-<descripcion>` (por ejemplo `feature/2-task-inicio-de-proyecto`).
- Los commits siguen [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/).
- Los PR usan la plantilla de `.github/PULL_REQUEST_TEMPLATE.md`.

## Configuración de CI

Los workflows necesitan el secret `GH_PAT` (token personal de GitHub) en *Settings → Secrets and variables → Actions*.
