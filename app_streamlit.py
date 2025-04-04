import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diagnostic GMAO", page_icon="📊", layout="centered")

# === Chargement des données ===
try:
    df = pd.read_excel("résumé_attributs_manquants.xlsx")
except Exception as e:
    st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
    st.stop()

# === Dictionnaire du nombre total d'attributs attendus par type d'équipement ===
attributs_attendus = {
    "TRANSFOHT": 8,
    "DJHTA": 10,
    "DJHTB": 9,
    "SECHTB": 9,
    "BATT": 8,
    "REDR": 6,
    "CELA": 1,
    "CELD": 2,
    "PS": 2,
    "CT": 1
}

# === Traitement du fichier en structure exploitable ===
data = []
colonnes = df.columns

for i in range(0, len(colonnes), 4):
    equipement_type = colonnes[i]
    poste_col = colonnes[i + 2] if i + 2 < len(colonnes) else None

    if poste_col is None or "Poste" not in poste_col:
        continue  # Sauter si pas de colonne poste correspondante

    for index, row in df.iterrows():
        ligne = row[equipement_type]
        poste = row[poste_col]

        if pd.notna(ligne) and "→" in str(ligne):
            identifiant, *attributs = ligne.split("→")
            identifiant = identifiant.strip()
            attributs_str = attributs[0].strip() if attributs else ""

            if attributs_str:
                data.append({
                    "Poste": poste,
                    "Type d'équipement": equipement_type,
                    "Identifiant": identifiant,
                    "Attributs manquants": attributs_str
                })

# Transformation en DataFrame
final_df = pd.DataFrame(data)

# === Interface utilisateur ===
st.title("📊 Diagnostic des attributs manquants")
st.markdown("Choisissez un poste pour voir les équipements incomplets.")

# === Sélecteur de poste ===
postes = sorted(final_df["Poste"].dropna().unique())
poste_choisi = st.selectbox("🔽 Sélectionnez un poste :", postes)

# === Filtrage du DataFrame selon le poste choisi ===
df_poste = final_df[final_df["Poste"] == poste_choisi]

# === Taux de complétude pondéré par attributs ===
total_attributs = 0
manquants_total = 0

for _, ligne in df_poste.iterrows():
    type_eq = ligne["Type d'équipement"]
    nb_attributs_type = attributs_attendus.get(type_eq, 0)
    total_attributs += nb_attributs_type
    nb_attributs_manquants = len([a.strip() for a in ligne["Attributs manquants"].split(",") if a.strip()])
    manquants_total += nb_attributs_manquants

if total_attributs > 0:
    taux_pondere = round(100 * (1 - manquants_total / total_attributs), 1)
else:
    taux_pondere = 100.0

st.metric("Taux de complétude pondéré", f"{taux_pondere}%", delta=None)
st.progress(taux_pondere / 100)

# === Affichage des équipements incomplets triés par type d'équipement ===
st.subheader("🧩 Équipements incomplets")

for type_eq in sorted(df_poste["Type d'équipement"].unique()):
    st.markdown(f"### 🧪 {type_eq}")
    df_type = df_poste[df_poste["Type d'équipement"] == type_eq]
    for _, ligne in df_type.iterrows():
        identifiant = ligne["Identifiant"]
        attributs = ligne["Attributs manquants"]
        st.markdown(f"#### 🛠️ {identifiant}")
        for attribut in attributs.split(","):
            st.markdown(f"- ❌ **{attribut.strip()}**")
