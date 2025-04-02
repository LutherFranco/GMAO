import streamlit as st
import pandas as pd

# === Charger le fichier enrichi ===
try:
    df_detail = pd.read_excel("résumé_attributs_manquants_enrichi.xlsx")
except Exception as e:
    st.error(f"❌ Erreur de lecture du fichier Excel enrichi : {e}")
    st.stop()

# === Interface ===
st.title("📊 Diagnostic GMAO par poste")

# Liste déroulante des postes
postes = sorted(df_detail["Poste"].dropna().unique())
poste_choisi = st.selectbox("🔽 Sélectionnez un poste :", postes)

# Filtrer sur le poste choisi
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

            numero = row.get("Equipement")
            description = row.get("Description")

            if pd.notna(numero) and str(numero).strip():
                info = str(numero)
            elif pd.notna(description) and str(description).strip():
                info = str(description)
            else:
                info = "⛔ Info manquante"

            lignes.append(f"- 🔴 **{info}** → {attribut}")

        st.markdown("\n".join(lignes))

# Optionnel : debug
if st.checkbox("🛠️ Afficher les colonnes disponibles"):
    st.write(df_detail.columns.tolist())
