import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diagnostic GMAO", page_icon="📊", layout="centered")

# === Chargement des données ===
try:
    df = pd.read_excel("résumé_attributs_manquants.xlsx", skiprows=1)
except Exception as e:
    st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
    st.stop()

# === Transformation des données en format long ===
data = []
for poste in df.columns:
    for ligne in df[poste].dropna():
        if "→" in str(ligne):
            identifiant, *attributs = ligne.split("→")
            identifiant = identifiant.strip()
            attributs_str = attributs[0].strip() if attributs else ""
            data.append({
                "Poste": poste,
                "Identifiant": identifiant,
                "Attributs manquants": attributs_str
            })

df_long = pd.DataFrame(data)

# === Calcul du taux de complétude ===
def calcul_completude(df_poste):
    total = len(df_poste)
    manquants = df_poste["Attributs manquants"].str.strip().replace("", pd.NA).dropna().count()
    taux = round(100 * (1 - manquants / total), 1)
    return taux

# === Interface utilisateur ===
st.title("📊 Diagnostic des attributs manquants")
st.markdown("Choisissez un poste pour voir les équipements incomplets.")

postes = sorted(df_long["Poste"].unique())
poste_choisi = st.selectbox("🔽 Sélectionnez un poste :", postes)

df_poste = df_long[df_long["Poste"] == poste_choisi]

# === Affichage du taux de complétude ===
taux = calcul_completude(df_poste)
st.metric("Taux de complétude", f"{taux}%", delta=None)
st.progress(taux / 100)

# === Affichage des attributs manquants ===
st.subheader("🧩 Équipements incomplets")

for _, ligne in df_poste.iterrows():
    identifiant = ligne["Identifiant"]
    attributs = ligne["Attributs manquants"]
    if attributs.strip():
        st.markdown(f"#### 🛠️ {identifiant}")
        for attribut in attributs.split(","):
            st.markdown(f"- ❌ **{attribut.strip()}**")
