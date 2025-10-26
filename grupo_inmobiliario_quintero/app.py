from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        nuevo_inmueble = {
            "tipo": request.form["tipo"],
            "municipio": request.form["municipio"],
            "habitaciones": int(request.form["habitaciones"]),
            "valor": int(request.form["valor"]),
            "imagen_url": request.form["imagen_url"]
        }
        INMUEBLES.append(nuevo_inmueble)  # ← debe estar dentro del if
        return redirect(url_for("admin"))

    return render_template("admin.html", inmuebles=INMUEBLES)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    inmueble = next((i for i in INMUEBLES if i["id"] == id), None)
    if not inmueble:
        return "Inmueble no encontrado", 404

    if request.method == "POST":
        inmueble["tipo"] = request.form["tipo"]
        inmueble["municipio"] = request.form["municipio"]
        inmueble["habitaciones"] = int(request.form["habitaciones"])
        inmueble["valor"] = int(request.form["valor"])
        inmueble["imagen_url"] = request.form["imagen_url"]
        return redirect(url_for("admin"))

    return render_template("editar.html", inmueble=inmueble)


if __name__ == "__main__":
    app.run(debug=True)