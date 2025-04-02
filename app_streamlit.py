import streamlit as st
import pandas as pd

# === Charger les données ===
try:
    df_detail = pd.read_excel("résumé_attributs_manquants.xlsx", sheet_name="Détail")
    df_completude = pd.read_excel("résumé_attributs_manquants.xlsx", sheet_name="Complétude")
except Exception as e:
    st.error(f"Erreur de lecture du fichier Excel : {e}")
    st.stop()

# === Interface ===
st.title("📊 Diagnostic GMAO par poste")

# Liste déroulante des postes
postes = sorted(df_detail["Poste"].dropna().unique())
poste_choisi = st.selectbox("🔽 Sélectionnez un poste :", postes)

# Complétude visuelle
info_poste = df_completude[df_completude["Poste"] == poste_choisi]
if not info_poste.empty:
    taux = float(info_poste["Taux de complétude (%)"].values[0])
    niveau = info_poste["Niveau"].values[0]
    st.metric("Taux de complétude", f"{taux}%", delta=None)
    st.progress(taux / 100)
    st.markdown(f"**Niveau :** {niveau}")

# Attributs manquants
df_poste = df_detail[df_detail["Poste"] == poste_choisi]

if df_poste.empty:
    st.success("✅ Aucun attribut manquant pour ce poste.")
else:
    st.subheader("🧩 Attributs manquants par équipement")

    grouped = df_poste.groupby("Équipement")
    for equipement, groupe in grouped:
        st.markdown(f"### 🛠️ {equipement}")
        lignes = []

        for _, row in groupe.iterrows():
            attribut = row["Attribut manquant"]

            # Vérification manuelle des colonnes "Équipement" ou "Equipement" et "Description"
            numero = row.get("Équipement")
            if pd.isna(numero) or numero == "":
                numero = row.get("Equipement")
            if pd.isna(numero) or numero == "":
                numero = None

            description = row.get("Description")
            if pd.isna(description) or description == "":
                description = None

            if numero:
                info = f"Numéro {numero}"
            elif description:
                info = f"Description : {description}"
            else:
                info = "⛔ Info manquante"

            lignes.append(f"- **{info}** → {attribut}")

        st.markdown("\n".join(lignes))

# Optionnel : affichage des colonnes pour debug
if st.checkbox("🛠️ Afficher les colonnes disponibles (debug)"):
    st.write(df_detail.columns.tolist())
