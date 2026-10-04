import os
from dotenv import load_dotenv


# ==================================================
# CARGAR VARIABLES DEL .ENV
# ==================================================

load_dotenv()


# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "Falta SECRET_KEY en el archivo .env"
    )


# ==================================================
# SUPABASE
# ==================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")

SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:

    raise RuntimeError(
        "Faltan SUPABASE_URL o SUPABASE_KEY "
        "en el archivo .env"
    )


# ==================================================
# SEGURIDAD DE SESIONES
# ==================================================

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_SECURE = True


# ==================================================
# STORAGE
# ==================================================

STORAGE_BUCKET = "productos"