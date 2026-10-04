from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from supabase import create_client

from config.settings import (
    SUPABASE_URL,
    SUPABASE_KEY
)

from services.productos import (
    obtener_productos,
    obtener_producto,
    crear_producto,
    actualizar_producto,
    eliminar_producto
)


# ==========================================================
# SUPABASE
# ==========================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==========================================================
# BLUEPRINT
# ==========================================================

admin = Blueprint(
    "admin",
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ==========================================================
# OBTENER ADMINISTRADOR
# ==========================================================

def obtener_administrador():

    respuesta = (
        supabase
        .table("administrador")
        .select("*")
        .limit(1)
        .execute()
    )

    if respuesta.data:

        return respuesta.data[0]

    return None


# ==========================================================
# PROTECCIÓN DEL PANEL
# ==========================================================

def requiere_login(funcion):

    @wraps(funcion)
    def protegida(*args, **kwargs):

        if not session.get("admin_logueado"):

            return redirect(
                url_for("admin.login")
            )

        return funcion(
            *args,
            **kwargs
        )

    return protegida


# ==========================================================
# LOGIN
# ==========================================================

@admin.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    administrador = obtener_administrador()


    # Si todavía no existe administrador,
    # enviamos a la configuración inicial.

    if administrador is None:

        return redirect(
            url_for("admin.configurar_admin")
        )


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
            usuario == administrador["usuario"]
            and check_password_hash(
                administrador["password"],
                contrasena
            )
        ):

            session["admin_logueado"] = True

            return redirect(
                url_for("admin.panel")
            )


        return render_template(
            "login.html",
            error="Usuario o contraseña incorrectos."
        )


    return render_template(
        "login.html"
    )


# ==========================================================
# CONFIGURAR ADMINISTRADOR
# ==========================================================

@admin.route(
    "/configurar-admin",
    methods=["GET", "POST"]
)
def configurar_admin():

    administrador = obtener_administrador()


    # Si ya existe una cuenta,
    # no permitimos crear otra.

    if administrador is not None:

        return redirect(
            url_for("admin.login")
        )


    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        telefono = request.form.get(
            "telefono",
            ""
        ).strip()

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        contrasena = request.form.get(
            "contrasena",
            ""
        )


        if (
            not nombre
            or not telefono
            or not usuario
            or not contrasena
        ):

            return render_template(
                "configurar_admin.html",
                error="Todos los campos son obligatorios."
            )


        password_hash = generate_password_hash(
            contrasena
        )


        datos = {
            "nombre": nombre,
            "telefono": telefono,
            "usuario": usuario,
            "password": password_hash
        }


        try:

            respuesta = (
                supabase
                .table("administrador")
                .insert(datos)
                .execute()
            )


            if respuesta.data:

                return redirect(
                    url_for("admin.login")
                )


            return render_template(
                "configurar_admin.html",
                error="No se pudo crear el administrador."
            )


        except Exception as error:

            print(
                "❌ Error creando administrador:"
            )

            print(error)


            return render_template(
                "configurar_admin.html",
                error="No se pudo crear el administrador."
            )


    return render_template(
        "configurar_admin.html"
    )


# ==========================================================
# CERRAR SESIÓN
# ==========================================================

@admin.route("/logout")
def logout():

    session.pop(
        "admin_logueado",
        None
    )

    return redirect(
        url_for("admin.login")
    )


# ==========================================================
# PANEL ADMINISTRADOR
# ==========================================================

@admin.route("/admin")
@requiere_login
def panel():

    productos = obtener_productos()

    return render_template(
        "admin.html",
        productos=productos
    )


# ==========================================================
# AGREGAR PRODUCTO
# ==========================================================

@admin.route(
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
            "❌ Precio o stock inválidos."
        )

        return redirect(
            url_for("admin.panel")
        )


    archivo = request.files.get(
        "foto"
    )


    crear_producto(
        nombre=nombre,
        categoria=categoria,
        precio=precio,
        stock=stock,
        descripcion=descripcion,
        archivo=archivo
    )


    return redirect(
        url_for("admin.panel")
    )


# ==========================================================
# EDITAR PRODUCTO
# ==========================================================

@admin.route(
    "/editar/<int:producto_id>",
    methods=["GET", "POST"]
)
@requiere_login
def editar(producto_id):

    producto = obtener_producto(
        producto_id
    )


    if producto is None:

        return redirect(
            url_for("admin.panel")
        )


    if request.method == "POST":

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

            return redirect(
                url_for(
                    "admin.editar",
                    producto_id=producto_id
                )
            )


        actualizar_producto(
            producto_id=producto_id,
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            stock=stock,
            descripcion=descripcion
        )


        return redirect(
            url_for("admin.panel")
        )


    return render_template(
        "editar.html",
        producto=producto
    )


# ==========================================================
# ELIMINAR PRODUCTO
# ==========================================================

@admin.route(
    "/eliminar/<int:producto_id>",
    methods=["POST"]
)
@requiere_login
def eliminar(producto_id):

    eliminar_producto(
        producto_id
    )

    return redirect(
        url_for("admin.panel")
    )


# ==========================================================
# CONFIGURACIÓN DEL ADMINISTRADOR
# ==========================================================

@admin.route(
    "/configuracion",
    methods=["GET", "POST"]
)
@requiere_login
def configuracion():

    administrador = obtener_administrador()


    if administrador is None:

        return redirect(
            url_for("admin.configurar_admin")
        )


    # ======================================================
    # GUARDAR CAMBIOS
    # ======================================================

    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        telefono = request.form.get(
            "telefono",
            ""
        ).strip()

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()


        # --------------------------------------------------
        # CONTRASEÑAS
        # --------------------------------------------------

        contrasena_actual = request.form.get(
            "contrasena_actual",
            ""
        )

        nueva_contrasena = request.form.get(
            "nueva_contrasena",
            ""
        )

        confirmar_contrasena = request.form.get(
            "confirmar_contrasena",
            ""
        )


        # --------------------------------------------------
        # VALIDAR DATOS BÁSICOS
        # --------------------------------------------------

        if (
            not nombre
            or not telefono
            or not usuario
        ):

            return render_template(
                "configuracion.html",
                administrador=administrador,
                error=(
                    "Nombre, teléfono y usuario "
                    "son obligatorios."
                )
            )


        # --------------------------------------------------
        # COMPROBAR SI QUIERE CAMBIAR CONTRASEÑA
        # --------------------------------------------------

        password_hash = administrador["password"]


        if nueva_contrasena:

            # ----------------------------------------------
            # CONTRASEÑA ACTUAL
            # ----------------------------------------------

            if not contrasena_actual:

                return render_template(
                    "configuracion.html",
                    administrador=administrador,
                    error=(
                        "Debes escribir tu contraseña actual "
                        "para poder cambiarla."
                    )
                )


            # ----------------------------------------------
            # COMPROBAR CONTRASEÑA ACTUAL
            # ----------------------------------------------

            if not check_password_hash(
                administrador["password"],
                contrasena_actual
            ):

                return render_template(
                    "configuracion.html",
                    administrador=administrador,
                    error=(
                        "La contraseña actual es incorrecta."
                    )
                )


            # ----------------------------------------------
            # CONFIRMAR NUEVA CONTRASEÑA
            # ----------------------------------------------

            if not confirmar_contrasena:

                return render_template(
                    "configuracion.html",
                    administrador=administrador,
                    error=(
                        "Debes confirmar la nueva contraseña."
                    )
                )


            # ----------------------------------------------
            # COMPROBAR CONTRASEÑAS
            # ----------------------------------------------

            if (
                nueva_contrasena
                != confirmar_contrasena
            ):

                return render_template(
                    "configuracion.html",
                    administrador=administrador,
                    error=(
                        "Las nuevas contraseñas "
                        "no coinciden."
                    )
                )


            # ----------------------------------------------
            # GENERAR NUEVO HASH
            # ----------------------------------------------

            password_hash = generate_password_hash(
                nueva_contrasena
            )


        # ==================================================
        # ACTUALIZAR EN SUPABASE
        # ==================================================

        datos = {
            "nombre": nombre,
            "telefono": telefono,
            "usuario": usuario,
            "password": password_hash
        }


        try:

            respuesta = (
                supabase
                .table("administrador")
                .update(datos)
                .eq(
                    "id",
                    administrador["id"]
                )
                .execute()
            )


            if respuesta.data:

                nuevo_admin = respuesta.data[0]

                return render_template(
                    "configuracion.html",
                    administrador=nuevo_admin,
                    exito=(
                        "Los datos fueron actualizados "
                        "correctamente."
                    )
                )


            return render_template(
                "configuracion.html",
                administrador=administrador,
                error=(
                    "No se pudieron actualizar "
                    "los datos."
                )
            )


        except Exception as error:

            print(
                "❌ Error actualizando administrador:"
            )

            print(error)


            return render_template(
                "configuracion.html",
                administrador=administrador,
                error=(
                    "No se pudieron actualizar "
                    "los datos."
                )
            )


    # ======================================================
    # MOSTRAR CONFIGURACIÓN
    # ======================================================

    return render_template(
        "configuracion.html",
        administrador=administrador
    )