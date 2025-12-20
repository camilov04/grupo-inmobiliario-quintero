from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inmuebles.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= MODELO =================
class Inmueble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    descripcion_larga = db.Column(db.Text)

    tipo = db.Column(db.String(50), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)

    habitaciones = db.Column(db.Integer)
    banos = db.Column(db.Integer)
    area = db.Column(db.Integer)

    parqueadero = db.Column(db.Boolean, default=False)

    precio = db.Column(db.Float, nullable=False)
    imagen_url = db.Column(db.String(255))

# ================= LOGIN =================
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrap

# ================= PUBLIC =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inmuebles")
def mostrar_inmuebles():
    query = Inmueble.query

    tipo = request.args.get("tipo")
    municipio = request.args.get("municipio")
    parqueadero = request.args.get("parqueadero")

    if tipo:
        query = query.filter_by(tipo=tipo)
    if municipio:
        query = query.filter(Inmueble.municipio.ilike(f"%{municipio}%"))
    if parqueadero:
        query = query.filter_by(parqueadero=True)

    inmuebles = query.all()
    return render_template("inmuebles.html", inmuebles=inmuebles)

@app.route("/inmueble/<int:inmueble_id>")
def detalle_inmueble(inmueble_id):
    inmueble = Inmueble.query.get_or_404(inmueble_id)
    return render_template("detalle_inmueble.html", inmueble=inmueble)

# ================= AUTH =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form["usuario"] == "admin" and request.form["contrasena"] == "1234":
            session["usuario"] = "admin"
            return redirect(url_for("panel_admin"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= ADMIN =================
@app.route("/admin")
@login_required
def panel_admin():
    inmuebles = Inmueble.query.all()
    return render_template("admin.html", inmuebles=inmuebles)

@app.route("/agregar_inmueble", methods=["POST"])
@login_required
def agregar_inmueble():
    nuevo = Inmueble(
        titulo=request.form["titulo"],
        descripcion=request.form["descripcion"],
        descripcion_larga=request.form["descripcion_larga"],
        tipo=request.form["tipo"],
        municipio=request.form["municipio"],
        habitaciones=request.form.get("habitaciones") or None,
        banos=request.form.get("banos") or None,
        area=request.form.get("area") or None,
        parqueadero=True if request.form.get("parqueadero") else False,
        precio=request.form["precio"],
        imagen_url=request.form["imagen_url"]
    )
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for("panel_admin"))

@app.route("/editar_inmueble/<int:id>", methods=["GET","POST"])
@login_required
def editar_inmueble(id):
    inmueble = Inmueble.query.get_or_404(id)

    if request.method == "POST":
        inmueble.titulo = request.form["titulo"]
        inmueble.descripcion = request.form["descripcion"]
        inmueble.descripcion_larga = request.form["descripcion_larga"]
        inmueble.tipo = request.form["tipo"]
        inmueble.municipio = request.form["municipio"]
        inmueble.habitaciones = request.form.get("habitaciones") or None
        inmueble.banos = request.form.get("banos") or None
        inmueble.area = request.form.get("area") or None
        inmueble.parqueadero = True if request.form.get("parqueadero") else False
        inmueble.precio = request.form["precio"]
        inmueble.imagen_url = request.form["imagen_url"]

        db.session.commit()
        return redirect(url_for("panel_admin"))

    return render_template("editar.html", inmueble=inmueble)

@app.route("/admin/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_inmueble(id):
    inmueble = Inmueble.query.get_or_404(id)
    db.session.delete(inmueble)
    db.session.commit()
    return redirect(url_for("panel_admin"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
