from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# Configurar base de datos SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inmuebles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------ MODELO ------------------
class Inmueble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    habitaciones = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<Inmueble {self.titulo}>"

# ------------------ RUTAS PÚBLICAS ------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inmuebles")
def mostrar_inmuebles():
    inmuebles = Inmueble.query.all()
    return render_template("inmuebles.html", inmuebles=inmuebles)

# ------------------ LOGIN ------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            flash("Debes iniciar sesión para acceder al panel.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")

        # Usuario y contraseña fijos (puedes cambiarlos)
        if usuario == "admin" and contrasena == "1234":
            session["usuario"] = usuario
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("panel_admin"))
        else:
            flash("Usuario o contraseña incorrectos.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))

# ------------------ PANEL ADMIN ------------------
@app.route("/admin")
@login_required
def panel_admin():
    inmuebles = Inmueble.query.all()
    if "usuario" not in session:
        flash("Debes iniciar sesión para acceder al panel.", "error")
        return redirect(url_for("login"))

    inmuebles = Inmueble.query.all()
    return render_template("admin.html", inmuebles=inmuebles)

# ------------------ AGREGAR ------------------

@app.route("/admin/agregar", methods=["GET", "POST"])
@login_required
def agregar_inmueble():
    if request.method == "POST":
        nuevo = Inmueble(
            tipo=request.form["tipo"],
            municipio=request.form["municipio"],
            habitaciones=int(request.form["habitaciones"]),
            valor=int(request.form["valor"]),
            imagen=request.form["imagen"]
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("Inmueble agregado correctamente.", "success")
        return redirect(url_for("panel_admin"))

    return render_template("agregar.html")

# ------------------ EDITAR ------------------

@app.route("/admin/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_inmueble(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión para acceder al panel.", "error")
        return redirect(url_for("login"))

    inmueble = Inmueble.query.get_or_404(id)

    if request.method == "POST":
        inmueble.titulo = request.form["titulo"]
        inmueble.descripcion = request.form["descripcion"]
        inmueble.precio = request.form["precio"]
        inmueble.tipo = request.form["tipo"]
        inmueble.imagen = request.form["imagen"]

        db.session.commit()
        flash("Inmueble actualizado correctamente.", "success")
        return redirect(url_for("panel_admin"))

    return render_template("editar.html", inmueble=inmueble)

# ------------------ ELIMINAR ------------------

@app.route("/admin/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_inmueble(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión para acceder al panel.", "error")
        return redirect(url_for("login"))

    inmueble = Inmueble.query.get_or_404(id)
    db.session.delete(inmueble)
    db.session.commit()
    flash("Inmueble eliminado correctamente.", "info")
    return redirect(url_for("panel_admin"))

# ------------------ MAIN ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # crea las tablas si no existen
    app.run(debug=True)