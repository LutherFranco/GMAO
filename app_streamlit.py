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

            # 🔍 Recherche fiable : d'abord "Equipement", puis "Équipement" si jamais
            numero = row.get("Equipement") or row.get("Équipement")
            description = row.get("Description")

            if pd.notna(numero) and str(numero).strip():
                info = f"Numéro {numero}"
            elif pd.notna(description) and str(description).strip():
                info = f"Description : {description}"
            else:
                info = f"🔧 Équipement : {equipement}"

            lignes.append(f"- 🔴 **{info}** → {attribut}")

        st.markdown("\n".join(lignes))

# Optionnel : debug
if st.checkbox("🛠️ Afficher les colonnes disponibles (debug)"):
    st.write(df_detail.columns.tolist())
