from flask import Flask, render_template, request, redirect, url_for, session
import os
import uuid
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from supabase import create_client


# ==================================================
# CARGAR VARIABLES DEL ARCHIVO .ENV
# ==================================================

load_dotenv()


# ==================================================
# CONEXIÓN CON SUPABASE
# ==================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("✅ Conexión con Supabase preparada")


# ==================================================
# CONFIGURACIÓN DE FLASK
# ==================================================

app = Flask(__name__)


# ==================================================
# CONFIGURACIÓN DE SESIÓN
# ==================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "clave-temporal-distrivariedades-cambiar-despues"
)


# ==================================================
# CONFIGURACIÓN DE IMÁGENES
# ==================================================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==================================================
# USUARIO ADMINISTRADOR
# ==================================================

USUARIO_ADMIN = "admin"

CONTRASENA_ADMIN = generate_password_hash(
    "123456"
)


# ==================================================
# PRODUCTOS DE PRUEBA
# ==================================================

productos_prueba = [

    {
        "id": 1,
        "nombre": "Crema hidratante",
        "categoria": "Cuidado de la piel",
        "precio": 25000,
        "stock": 10,
        "descripcion": "Crema hidratante para el cuidado diario de la piel.",
        "foto": ""
    },

    {
        "id": 2,
        "nombre": "Labial",
        "categoria": "Maquillaje",
        "precio": 15000,
        "stock": 8,
        "descripcion": "Labial para complementar tu maquillaje.",
        "foto": ""
    },

    {
        "id": 3,
        "nombre": "Shampoo",
        "categoria": "Cabello",
        "precio": 22000,
        "stock": 6,
        "descripcion": "Producto para el cuidado y limpieza del cabello.",
        "foto": ""
    }

]


# ==================================================
# LEER PRODUCTOS DESDE SUPABASE
# ==================================================

def obtener_productos():

    try:

        respuesta = (
            supabase
            .table("productos")
            .select("*")
            .order("id")
            .execute()
        )

        productos_supabase = respuesta.data

        if productos_supabase:

            print(
                f"✅ Productos cargados desde Supabase: "
                f"{len(productos_supabase)}"
            )

            return productos_supabase

        print(
            "ℹ️ La tabla productos está vacía. "
            "Usando productos de prueba."
        )

        return productos_prueba

    except Exception as error:

        print(
            "❌ Error leyendo productos desde Supabase:"
        )

        print(error)

        return productos_prueba


# ==================================================
# PROTECCIÓN DEL PANEL ADMIN
# ==================================================

def requiere_login(funcion):

    @wraps(funcion)
    def protegida(*args, **kwargs):

        if not session.get("admin_logueado"):

            return redirect(
                url_for("login")
            )

        return funcion(*args, **kwargs)

    return protegida


# ==================================================
# PÁGINA PRINCIPAL
# ==================================================

@app.route("/")
def inicio():

    productos = obtener_productos()

    return render_template(
        "tienda.html",
        productos=productos
    )


# ==================================================
# LOGIN
# ==================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        contrasena = request.form.get(
            "contrasena",
            ""
        )

        if (
            usuario == USUARIO_ADMIN
            and check_password_hash(
                CONTRASENA_ADMIN,
                contrasena
            )
        ):

            session["admin_logueado"] = True

            return redirect(
                url_for("admin")
            )

        return render_template(
            "login.html",
            error="Usuario o contraseña incorrectos."
        )

    return render_template(
        "login.html"
    )


# ==================================================
# CERRAR SESIÓN
# ==================================================

@app.route("/logout")
def logout():

    session.pop(
        "admin_logueado",
        None
    )

    return redirect(
        url_for("login")
    )


# ==================================================
# PANEL DE ADMINISTRACIÓN
# ==================================================

@app.route("/admin")
@requiere_login
def admin():

    productos = obtener_productos()

    return render_template(
        "admin.html",
        productos=productos
    )


# ==================================================
# AGREGAR PRODUCTO
# ==================================================

@app.route(
    "/agregar",
    methods=["POST"]
)
@requiere_login
def agregar():

    nombre = request.form.get(
        "nombre",
        ""
    ).strip()

    categoria = request.form.get(
        "categoria",
        ""
    ).strip()

    precio = request.form.get(
        "precio",
        "0"
    ).strip()

    stock = request.form.get(
        "stock",
        "0"
    ).strip()

    descripcion = request.form.get(
        "descripcion",
        ""
    ).strip()


    try:

        precio = float(precio)

        stock = int(stock)

    except ValueError:

        print(
            "❌ El precio o el stock no son válidos."
        )

        return redirect(
            url_for("admin")
        )


    # ==================================================
    # SUBIR IMAGEN A SUPABASE STORAGE
    # ==================================================

    archivo = request.files.get("foto")

    foto_url = ""


    if archivo and archivo.filename:

        try:

            nombre_original = secure_filename(
                archivo.filename
            )

            extension = os.path.splitext(
                nombre_original
            )[1].lower()


            nombre_unico = (
                str(uuid.uuid4())
                + extension
            )


            contenido = archivo.read()


            supabase.storage \
                .from_("productos") \
                .upload(
                    nombre_unico,
                    contenido,
                    {
                        "content-type": (
                            archivo.mimetype
                            or "application/octet-stream"
                        ),
                        "upsert": "false"
                    }
                )


            foto_url = (
                supabase.storage
                .from_("productos")
                .get_public_url(
                    nombre_unico
                )
            )


            print(
                "✅ Imagen subida correctamente a Supabase Storage."
            )

            print(
                "🔗 URL de imagen:",
                foto_url
            )


        except Exception as error:

            print(
                "❌ Error subiendo la imagen a Supabase:"
            )

            print(error)

            foto_url = ""


    # ==================================================
    # GUARDAR PRODUCTO EN SUPABASE
    # ==================================================

    nuevo_producto = {

        "nombre": nombre,

        "categoria": categoria,

        "precio": precio,

        "stock": stock,

        "descripcion": descripcion,

        "foto": foto_url

    }


    try:

        respuesta = (
            supabase
            .table("productos")
            .insert(nuevo_producto)
            .execute()
        )


        if respuesta.data:

            print(
                "✅ Producto guardado correctamente en Supabase."
            )

        else:

            print(
                "⚠️ Supabase no devolvió el producto."
            )


    except Exception as error:

        print(
            "❌ Error guardando producto en Supabase:"
        )

        print(error)


    return redirect(
        url_for("admin")
    )


# ==================================================
# EDITAR PRODUCTO
# ==================================================

@app.route(
    "/editar/<int:producto_id>",
    methods=["GET", "POST"]
)
@requiere_login
def editar(producto_id):

    productos = obtener_productos()

    producto = next(
        (
            p for p in productos
            if int(p["id"]) == producto_id
        ),
        None
    )


    if producto is None:

        return redirect(
            url_for("admin")
        )


    if request.method == "POST":

        print(
            "⚠️ Edición todavía no está conectada a Supabase."
        )

        return redirect(
            url_for("admin")
        )


    return render_template(
        "editar.html",
        producto=producto
    )


# ==================================================
# ELIMINAR PRODUCTO
# ==================================================

@app.route(
    "/eliminar/<int:producto_id>",
    methods=["POST"]
)
@requiere_login
def eliminar(producto_id):

    print(
        "⚠️ Eliminación todavía no está conectada a Supabase."
    )

    return redirect(
        url_for("admin")
    )


# ==================================================
# INICIAR SERVIDOR
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )