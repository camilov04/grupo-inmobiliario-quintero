from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

app.secret_key = "clave_super_secreta_cambiar_esto"

INMUEBLES = [
        {
            "municipio": "Medellín",
            "tipo": "Apartamento",
            "habitaciones": 3,
            "valor": 350000000,
            "imagen_url": "https://www.shutterstock.com/image-vector/simple-small-house-digital-illustration-600nw-2642400313.jpg"
        },
        {
            "municipio": "Envigado",
            "tipo": "Casa",
            "habitaciones": 4,
            "valor": 420000000,
            "imagen_url": "https://www.shutterstock.com/image-vector/simple-small-house-digital-illustration-600nw-2642400313.jpg"
        },
        {
            "municipio": "Bello",
            "tipo": "Apartamento",
            "habitaciones": 2,
            "valor": 280000000,
            "imagen_url": "https://www.shutterstock.com/image-vector/simple-small-house-digital-illustration-600nw-2642400313.jpg"
        }
    ]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inmuebles")
def mostrar_inmuebles():
    municipio = request.args.get("municipio", "")
    tipo = request.args.get("tipo", "")
    habitaciones = request.args.get("habitaciones", "")
    valor_min = request.args.get("valor_min", "")
    valor_max = request.args.get("valor_max", "")

    # Lista de inmuebles con imágenes (puedes editar o ampliar)
    

    # Filtros dinámicos
    resultados = INMUEBLES

    if municipio:
        resultados = [i for i in resultados if i["municipio"].lower() == municipio.lower()]
    if tipo:
        resultados = [i for i in resultados if i["tipo"].lower() == tipo.lower()]
    if habitaciones:
        resultados = [i for i in resultados if i["habitaciones"] == int(habitaciones)]
    if valor_min:
        resultados = [i for i in resultados if i["valor"] >= int(valor_min)]
    if valor_max:
        resultados = [i for i in resultados if i["valor"] <= int(valor_max)]

    return render_template("inmuebles.html", inmuebles=resultados)

@app.route("/admin")
def admin():
    if "usuario" not in session:
        flash("Por favor inicia sesión para continuar.", "warning")
        return redirect(url_for("login"))

    return render_template("admin.html", inmuebles=INMUEBLES)

@app.route('/agregar', methods=['POST'])
def agregar():
    nuevo = {
        "id": len(INMUEBLES),  # 👈 genera id automáticamente
        "titulo": request.form["titulo"],
        "descripcion": request.form["descripcion"],
        "precio": request.form["precio"],
        "imagen": request.form["imagen"]
    }
    INMUEBLES.append(nuevo)
    return redirect(url_for('admin'))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_inmueble(id):
    global INMUEBLES  # asegúrate de tener esto
    inmueble = INMUEBLES[id] if 0 <= id < len(INMUEBLES) else None

    if not inmueble:
        return "Inmueble no encontrado", 404

    if request.method == "POST":
        inmueble["tipo"] = request.form["tipo"]
        inmueble["municipio"] = request.form["municipio"]
        inmueble["habitaciones"] = int(request.form["habitaciones"])
        inmueble["valor"] = int(request.form["valor"])
        inmueble["imagen_url"] = request.form["imagen_url"]
        return redirect(url_for("admin"))

    return render_template("editar.html", inmueble=inmueble, id=id)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    del INMUEBLES[id]
    return redirect(url_for('admin'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contrasena = request.form["contrasena"]

        # 🔒 Usuario y contraseña fijos por ahora
        if usuario == "admin" and contrasena == "1234":
            session["usuario"] = usuario
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("admin"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)