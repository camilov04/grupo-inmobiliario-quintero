from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# ------------------ CONFIG ------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inmuebles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------ MODELO ------------------
class Inmueble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    descripcion_larga = db.Column(db.Text)

    tipo = db.Column(db.String(50), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)

    habitaciones = db.Column(db.Integer, nullable=True)
    banos = db.Column(db.Integer, nullable=True)

    precio = db.Column(db.Float, nullable=False)
    imagen_url = db.Column(db.String(255))

    def __repr__(self):
        return f"<Inmueble {self.titulo}>"

# ------------------ RUTAS PÚBLICAS ------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inmuebles")
def mostrar_inmuebles():
    query = Inmueble.query

    municipio = request.args.get("municipio")
    tipo = request.args.get("tipo")
    habitaciones = request.args.get("habitaciones")
    banos = request.args.get("banos")
    valor_min = request.args.get("valor_min")
    valor_max = request.args.get("valor_max")

    if municipio:
        query = query.filter(Inmueble.municipio.ilike(f"%{municipio}%"))
    if tipo:
        query = query.filter_by(tipo=tipo)
    if habitaciones:
        query = query.filter(Inmueble.habitaciones >= int(habitaciones))
    if banos:
        query = query.filter(Inmueble.banos >= int(banos))
    if valor_min:
        query = query.filter(Inmueble.precio >= float(valor_min))
    if valor_max:
        query = query.filter(Inmueble.precio <= float(valor_max))

    inmuebles = query.all()
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
    return render_template("admin.html", inmuebles=inmuebles)

# ------------------ AGREGAR INMUEBLE ------------------
@app.route("/agregar_inmueble", methods=["POST"])
@login_required
def agregar_inmueble():

    tipo = request.form.get("tipo")

    habitaciones = request.form.get("habitaciones")
    banos = request.form.get("banos")

    nuevo = Inmueble(
        titulo=request.form.get("titulo"),
        descripcion=request.form.get("descripcion"),
        descripcion_larga=request.form.get("descripcion_larga"),
        tipo=tipo,
        municipio=request.form.get("municipio"),

        habitaciones=int(habitaciones) if habitaciones else None,
        banos=int(banos) if banos else None,

        precio=float(request.form.get("precio")),
        imagen_url=request.form.get("imagen_url")
    )

    db.session.add(nuevo)
    db.session.commit()
    flash("Inmueble agregado correctamente.", "success")
    return redirect(url_for("panel_admin"))

# ------------------ EDITAR INMUEBLE ------------------
@app.route("/editar_inmueble/<int:id>", methods=["GET", "POST"])
@login_required
def editar_inmueble(id):
    inmueble = Inmueble.query.get_or_404(id)

    if request.method == "POST":

        habitaciones = request.form.get("habitaciones")
        banos = request.form.get("banos")

        inmueble.titulo = request.form.get("titulo")
        inmueble.descripcion = request.form.get("descripcion")
        inmueble.descripcion_larga = request.form.get("descripcion_larga")
        inmueble.tipo = request.form.get("tipo")
        inmueble.municipio = request.form.get("municipio")

        inmueble.habitaciones = int(habitaciones) if habitaciones else None
        inmueble.banos = int(banos) if banos else None

        inmueble.precio = float(request.form.get("precio"))
        inmueble.imagen_url = request.form.get("imagen_url")

        db.session.commit()
        flash("Inmueble actualizado correctamente.", "success")
        return redirect(url_for("panel_admin"))

    return render_template("editar.html", inmueble=inmueble)

# ------------------ ELIMINAR INMUEBLE ------------------
@app.route("/admin/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_inmueble(id):
    inmueble = Inmueble.query.get_or_404(id)
    db.session.delete(inmueble)
    db.session.commit()
    flash("Inmueble eliminado.", "info")
    return redirect(url_for("panel_admin"))

# ------------------ DETALLE INMUEBLE ------------------
@app.route("/inmueble/<int:inmueble_id>")
def detalle_inmueble(inmueble_id):
    inmueble = Inmueble.query.get_or_404(inmueble_id)
    return render_template("detalle_inmueble.html", inmueble=inmueble)

# ------------------ MAIN ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
