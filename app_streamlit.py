import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diagnostic GMAO", page_icon="📊", layout="wide")

# === Logo ENEDIS ===
st.image("https://upload.wikimedia.org/wikipedia/fr/thumb/f/f7/Enedis_logo.svg/1280px-Enedis_logo.svg.png", width=200)

st.markdown("""
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #003A70;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 22px;
        color: #005AA7;
        margin-top: 25px;
    }
    .equipment-type {
        font-size: 20px;
        color: #0066CC;
        font-weight: bold;
        margin-top: 20px;
    }
    .equipment-id {
        font-size: 16px;
        font-weight: 600;
        margin-top: 10px;
    }
    .missing-attr {
        font-size: 15px;
        margin-left: 20px;
    }
    </style>
""", unsafe_allow_html=True)

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
        continue

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

final_df = pd.DataFrame(data)

# === Interface utilisateur ===
st.markdown('<div class="title">📊 Diagnostic des attributs manquants</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Choisissez un poste pour voir les équipements incomplets.</div>', unsafe_allow_html=True)

# === Sélecteur de poste ===
postes = sorted(final_df["Poste"].dropna().unique())
poste_choisi = st.selectbox("🔽 Sélectionnez un poste :", postes)

df_poste = final_df[final_df["Poste"] == poste_choisi]

# === Taux de complétude pondéré ===
total_attributs = 0
manquants_total = 0

for _, ligne in df_poste.iterrows():
    type_eq = ligne["Type d'équipement"]
    nb_attributs_type = attributs_attendus.get(type_eq, 0)
    total_attributs += nb_attributs_type
    nb_attributs_manquants = len([a.strip() for a in ligne["Attributs manquants"].split(",") if a.strip()])
    manquants_total += nb_attributs_manquants

taux_pondere = round(100 * (1 - manquants_total / total_attributs), 1) if total_attributs > 0 else 100.0

st.metric("Taux de complétude pondéré", f"{taux_pondere}%", delta=None)
st.progress(taux_pondere / 100)

# === Affichage lisible des équipements incomplets ===
st.markdown('<div class="subtitle">🧩 Équipements incomplets</div>', unsafe_allow_html=True)

for type_eq in sorted(df_poste["Type d'équipement"].unique()):
    st.markdown(f'<div class="equipment-type">🧪 {type_eq}</div>', unsafe_allow_html=True)
    df_type = df_poste[df_poste["Type d'équipement"] == type_eq]
    for _, ligne in df_type.iterrows():
        identifiant = ligne["Identifiant"]
        attributs = ligne["Attributs manquants"]
        st.markdown(f'<div class="equipment-id">🛠️ {identifiant}</div>', unsafe_allow_html=True)
        for attribut in attributs.split(","):
            st.markdown(f'<div class="missing-attr">- ❌ <strong>{attribut.strip()}</strong></div>', unsafe_allow_html=True)
