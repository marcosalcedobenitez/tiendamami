import os
import uuid
from io import BytesIO

from PIL import Image
from werkzeug.utils import secure_filename
from supabase import create_client

from config.settings import (
    SUPABASE_URL,
    SUPABASE_KEY,
    STORAGE_BUCKET
)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


print("✅ Conexión con Supabase preparada")


def obtener_productos():

    try:

        respuesta = (
            supabase
            .table("productos")
            .select("*")
            .order("id")
            .execute()
        )

        productos = respuesta.data

        if productos:

            print(
                f"✅ Productos cargados desde Supabase: "
                f"{len(productos)}"
            )

            return productos

        print(
            "ℹ️ La tabla productos está vacía."
        )

        return []

    except Exception as error:

        print(
            "❌ Error leyendo productos desde Supabase:"
        )

        print(error)

        return []


def obtener_producto(producto_id):

    productos = obtener_productos()

    producto = next(
        (
            producto
            for producto in productos
            if int(producto["id"]) == int(producto_id)
        ),
        None
    )

    return producto


def optimizar_imagen(archivo):

    if not archivo or not archivo.filename:
        return None

    try:

        imagen = Image.open(archivo)

        if imagen.mode in ("RGBA", "LA", "P"):

            fondo = Image.new(
                "RGB",
                imagen.size,
                "white"
            )

            if imagen.mode == "P":
                imagen = imagen.convert("RGBA")

            fondo.paste(
                imagen,
                mask=(
                    imagen.getchannel("A")
                    if imagen.mode == "RGBA"
                    else None
                )
            )

            imagen = fondo

        else:

            imagen = imagen.convert("RGB")

        max_ancho = 1200
        max_alto = 1200

        imagen.thumbnail(
            (max_ancho, max_alto),
            Image.Resampling.LANCZOS
        )

        memoria = BytesIO()

        imagen.save(
            memoria,
            format="WEBP",
            quality=82,
            optimize=True,
            method=6
        )

        memoria.seek(0)

        print(
            "✅ Imagen optimizada correctamente."
        )

        return memoria.read()

    except Exception as error:

        print(
            "❌ Error optimizando imagen:"
        )

        print(error)

        return None


def subir_imagen(archivo):

    if not archivo or not archivo.filename:
        return ""

    try:

        nombre_original = secure_filename(
            archivo.filename
        )

        extension = os.path.splitext(
            nombre_original
        )[1].lower()

        extensiones_permitidas = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        }

        if extension not in extensiones_permitidas:

            print(
                "❌ Formato de imagen no permitido."
            )

            return ""

        contenido = optimizar_imagen(
            archivo
        )

        if not contenido:
            return ""

        nombre_unico = (
            str(uuid.uuid4())
            + ".webp"
        )

        (
            supabase.storage
            .from_(STORAGE_BUCKET)
            .upload(
                nombre_unico,
                contenido,
                {
                    "content-type": "image/webp",
                    "upsert": "false"
                }
            )
        )

        foto_url = (
            supabase.storage
            .from_(STORAGE_BUCKET)
            .get_public_url(
                nombre_unico
            )
        )

        print(
            "✅ Imagen subida y optimizada correctamente."
        )

        return foto_url

    except Exception as error:

        print(
            "❌ Error subiendo imagen:"
        )

        print(error)

        return ""


def crear_producto(
    nombre,
    categoria,
    precio,
    agotado,
    descripcion,
    archivo
):

    foto_url = subir_imagen(
        archivo
    )

    # 1 = disponible
    # 0 = agotado
    stock = 0 if agotado else 1

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
                "✅ Producto guardado correctamente."
            )

            return respuesta.data[0]

        print(
            "⚠️ Supabase no devolvió el producto."
        )

        return None

    except Exception as error:

        print(
            "❌ Error guardando producto:"
        )

        print(error)

        return None


def actualizar_producto(
    producto_id,
    nombre,
    categoria,
    precio,
    agotado,
    descripcion
):

    # 1 = disponible
    # 0 = agotado
    stock = 0 if agotado else 1

    datos = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
        "descripcion": descripcion
    }

    try:

        respuesta = (
            supabase
            .table("productos")
            .update(datos)
            .eq(
                "id",
                producto_id
            )
            .execute()
        )

        if respuesta.data:

            print(
                "✅ Producto actualizado correctamente."
            )

            return respuesta.data[0]

        return None

    except Exception as error:

        print(
            "❌ Error actualizando producto:"
        )

        print(error)

        return None


def cambiar_estado_producto(
    producto_id,
    agotado
):

    # 1 = disponible
    # 0 = agotado
    stock = 0 if agotado else 1

    datos = {
        "stock": stock
    }

    try:

        respuesta = (
            supabase
            .table("productos")
            .update(datos)
            .eq(
                "id",
                producto_id
            )
            .execute()
        )

        if respuesta.data:

            if agotado:

                print(
                    "🔴 Producto marcado como agotado."
                )

            else:

                print(
                    "🟢 Producto marcado como disponible."
                )

            return respuesta.data[0]

        print(
            "⚠️ No se pudo cambiar el estado del producto."
        )

        return None

    except Exception as error:

        print(
            "❌ Error cambiando estado del producto:"
        )

        print(error)

        return None


def eliminar_producto(producto_id):

    try:

        respuesta = (
            supabase
            .table("productos")
            .delete()
            .eq(
                "id",
                producto_id
            )
            .execute()
        )

        print(
            "✅ Producto eliminado correctamente."
        )

        return True

    except Exception as error:

        print(
            "❌ Error eliminando producto:"
        )

        print(error)

        return False