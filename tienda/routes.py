from flask import Blueprint, render_template, Response, request

from services.productos import obtener_productos, obtener_producto


tienda = Blueprint(
    "tienda",
    __name__,
    template_folder="templates",
    static_folder="static"
)


# ==========================================================
# TIENDA
# ==========================================================

@tienda.route("/")
def inicio():

    productos = obtener_productos()

    return render_template(
        "tienda.html",
        productos=productos
    )


# ==========================================================
# VER PRODUCTO
# ==========================================================

@tienda.route("/producto/<int:producto_id>")
def ver_producto(producto_id):

    producto = obtener_producto(producto_id)

    if not producto:

        return render_template(
            "404.html"
        ), 404

    return render_template(
        "producto.html",
        producto=producto
    )


# ==========================================================
# AVISO LEGAL
# ==========================================================

@tienda.route("/aviso-legal")
def aviso_legal():

    return render_template(
        "aviso_legal.html"
    )


# ==========================================================
# POLÍTICA DE PRIVACIDAD
# ==========================================================

@tienda.route("/privacidad")
def privacidad():

    return render_template(
        "privacidad.html"
    )


# ==========================================================
# POLÍTICA DE COOKIES
# ==========================================================

@tienda.route("/cookies")
def cookies():

    return render_template(
        "cookies.html"
    )


# ==========================================================
# SITEMAP
# ==========================================================

@tienda.route("/sitemap.xml")
def sitemap():

    base_url = request.url_root.rstrip("/")

    productos = obtener_productos()

    rutas = [
        "/",
        "/aviso-legal",
        "/privacidad",
        "/cookies"
    ]

    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

    for ruta in rutas:

        sitemap_xml += f"""
    <url>
        <loc>{base_url}{ruta}</loc>
    </url>
"""

    for producto in productos:

        sitemap_xml += f"""
    <url>
        <loc>{base_url}/producto/{producto["id"]}</loc>
    </url>
"""

    sitemap_xml += """
</urlset>
"""

    return Response(
        sitemap_xml,
        mimetype="application/xml"
    )