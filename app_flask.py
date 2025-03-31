from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

# Charger le fichier Excel
def read_excel():
    df = pd.read_excel("data.xlsx")
    return df.to_dict(orient="records")

# Route pour obtenir les données
@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(read_excel())

# Route pour ajouter une ligne dans Excel
@app.route("/add", methods=["POST"])
def add_data():
    data = request.json
    df = pd.read_excel("data.xlsx")
    df = df.append(data, ignore_index=True)
    df.to_excel("data.xlsx", index=False)
    return jsonify({"message": "Données ajoutées !"})

if __name__ == "__main__":
    app.run(debug=True)
