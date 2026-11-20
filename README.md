# Aboneros — Etapa 1: base del proyecto

Una instalación = una empresa. Cada empresa corre su propio servidor y su propia base
de datos; las apps móviles se enlazan a la URL de su servidor.

## Puesta en marcha (Windows / PowerShell)

```powershell
cd C:\Users\andre\OneDrive\Desktop\abonero
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # luego edita .env (clave secreta y contraseña de BD)
```

Crear base de datos y usuario en PostgreSQL (psql como superusuario `postgres`):

```sql
CREATE USER aboneros WITH PASSWORD 'Andres.Rod71@' CREATEDB;
CREATE DATABASE aboneros OWNER aboneros;
```

Después:

```powershell
python manage.py migrate
python manage.py init_business --name "Nombre de tu empresa"
python manage.py createsuperuser
python manage.py test
python manage.py runserver
```

Abre http://127.0.0.1:8000/admin/

Después de crear el superusuario, entra al admin y asígnale la empresa (campo "Empresa").

## Estructura

- `config/` — settings, urls.
- `apps/businesses/` — Business, Branch, comando `init_business`.
- `apps/accounts/` — User personalizado, roles, EmployeeProfile, permisos DRF.
