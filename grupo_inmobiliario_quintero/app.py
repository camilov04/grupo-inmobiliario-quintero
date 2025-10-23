from flask import Flask, render_template, request

app = Flask(__name__)

# Ejemplo de inmuebles disponibles
INMUEBLES = [
    {"municipio": "Medellín", "tipo": "Apartamento", "habitaciones": 3, "valor": 250000000},
    {"municipio": "Envigado", "tipo": "Casa", "habitaciones": 4, "valor": 450000000},
    {"municipio": "Bello", "tipo": "Apartamento", "habitaciones": 2, "valor": 180000000},
    {"municipio": "Itagüí", "tipo": "Casa", "habitaciones": 3, "valor": 300000000},
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inmuebles")
def inmuebles():
    municipio = request.args.get("municipio", "")
    tipo = request.args.get("tipo", "")
    habitaciones = request.args.get("habitaciones", "")
    valor_min = request.args.get("valor_min", "")
    valor_max = request.args.get("valor_max", "")

    resultados = INMUEBLES

    # Filtros
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

if __name__ == "__main__":
    app.run(debug=True)