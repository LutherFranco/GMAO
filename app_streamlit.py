import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diagnostic GMAO", page_icon="📊", layout="centered")

# === Chargement des données ===
try:
    df = pd.read_excel("échantillon.xlsx")
except Exception as e:
    st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
    st.stop()

# === Traitement du fichier en structure exploitable ===
data = []
colonnes = df.columns

for i in range(0, len(colonnes), 3):
    equipement_type = colonnes[i]
    poste_col = colonnes[i + 1] if i + 1 < len(colonnes) else None

    if poste_col is None:
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

# === Taux de complétude ===
total = df_poste.shape[0]
manquants = df_poste["Attributs manquants"].str.strip().replace("", pd.NA).dropna().count()
taux = round(100 * (1 - manquants / total), 1) if total > 0 else 100.0

st.metric("Taux de complétude", f"{taux}%", delta=None)
st.progress(taux / 100)

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
