import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
from io import BytesIO
import unicodedata
from datetime import datetime
import zipfile

# === Utilitaire pour encoder les caractères en latin-1 ===
def to_latin1(text):
    return unicodedata.normalize('NFKD', str(text)).encode('latin-1', 'ignore').decode('latin-1')

# === Configuration de la page Streamlit ===
st.set_page_config(page_title="Diagnostic GMAO", page_icon="📊", layout="wide")

# === Style CSS personnalisé ===
st.markdown("""
    <style>
    .title { font-size: 36px; font-weight: bold; color: #003A70; margin-bottom: 10px; }
    .subtitle { font-size: 22px; color: #005AA7; margin-top: 25px; }
    .equipment-type { font-size: 20px; color: #0066CC; font-weight: bold; margin-top: 20px; }
    .equipment-id { font-size: 16px; font-weight: 600; margin-top: 10px; }
    .missing-attr { font-size: 15px; margin-left: 20px; }
    .label-completude { font-size: 18px; font-weight: bold; padding-top: 10px; }
    .signature { font-size: 11px; text-align: right; color: grey; padding-top: 50px; }
    </style>
""", unsafe_allow_html=True)

# === Chargement des données ===
try:
    df = pd.read_excel("résumé_attributs_manquants.xlsx")
except Exception as e:
    st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
    st.stop()

# === Dictionnaire du nombre d'attributs attendus par type ===
attributs_attendus = {
    "TRANSFOHT": 8, "DJHTA": 10, "DJHTB": 9, "SECHTB": 9,
    "BATT": 8, "REDR": 6, "CELA": 1, "CELD": 2, "PS": 2, "CT": 1
}

# === Transformation des données ===
data_complet = []
data_manquants = []
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
        else:
            identifiant = str(ligne).strip() if pd.notna(ligne) else None
            attributs_str = ""
        if identifiant:
            data_complet.append({"Poste": poste, "Type d'équipement": equipement_type, "Identifiant": identifiant, "Attributs manquants": attributs_str})
        if attributs_str:
            data_manquants.append({"Poste": poste, "Type d'équipement": equipement_type, "Identifiant": identifiant, "Attributs manquants": attributs_str})

df_complet = pd.DataFrame(data_complet)
df_manquants = pd.DataFrame(data_manquants)

# === Interface Streamlit ===
st.markdown('<div class="title">📊 Diagnostic des attributs manquants</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Choisissez un poste pour voir les équipements incomplets.</div>', unsafe_allow_html=True)

postes = sorted(df_complet["Poste"].dropna().unique())
poste_choisi = st.selectbox("🔽 Sélectionnez un poste :", postes)

df_poste_total = df_complet[df_complet["Poste"] == poste_choisi]
df_poste_manquants = df_manquants[df_manquants["Poste"] == poste_choisi]

nb_attributs_totaux = sum(attributs_attendus.get(l["Type d'équipement"], 0) for _, l in df_poste_total.iterrows())
nb_attributs_manquants = sum(len([x.strip() for x in l["Attributs manquants"].split(",") if x.strip()]) for _, l in df_poste_manquants.iterrows())

taux_completude = 100.0 if nb_attributs_totaux == 0 else round(100 * (1 - nb_attributs_manquants / nb_attributs_totaux), 1)
label = "🔴 Très mauvais" if taux_completude < 87.5 else "🟢 Excellent" if taux_completude > 97.5 else "🟡 Correct"

st.metric("Taux de complétude pondéré", f"{taux_completude}%")
st.markdown(f'<div class="label-completude">{label}</div>', unsafe_allow_html=True)
st.progress(taux_completude / 100)

# === Affichage des attributs manquants ===
st.markdown('<div class="subtitle">🧩 Équipements incomplets</div>', unsafe_allow_html=True)
for type_eq in sorted(df_poste_manquants["Type d'équipement"].unique()):
    st.markdown(f'<div class="equipment-type">🔌 {type_eq}</div>', unsafe_allow_html=True)
    df_type = df_poste_manquants[df_poste_manquants["Type d'équipement"] == type_eq]
    for _, ligne in df_type.iterrows():
        st.markdown(f'<div class="equipment-id">🛠️ {ligne["Identifiant"]}</div>', unsafe_allow_html=True)
        for attribut in ligne["Attributs manquants"].split(","):
            st.markdown(f'<div class="missing-attr">- ❌ <strong>{attribut.strip()}</strong></div>', unsafe_allow_html=True)

# === Génération PDF par poste ===
def export_pdf(poste, df_poste_manquants, taux, label):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=to_latin1(f"Diagnostic - Poste {poste}"), ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=to_latin1(f"Date : {datetime.today().strftime('%d/%m/%Y')}"), ln=True, align='R')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 10, txt=to_latin1(f"Taux de complétude : {taux}% ({label})"), ln=True)
    pdf.ln(5)
    for type_eq in sorted(df_poste_manquants["Type d'équipement"].unique()):
        pdf.set_font("Arial", style='B', size=11)
        pdf.cell(200, 10, txt=to_latin1(f"Type : {type_eq}"), ln=True)
        df_type = df_poste_manquants[df_poste_manquants["Type d'équipement"] == type_eq]
        for _, ligne in df_type.iterrows():
            pdf.set_font("Arial", style='', size=11)
            pdf.cell(200, 8, txt=to_latin1(f" - Equipement {ligne['Identifiant']}"), ln=True)
            for attribut in ligne["Attributs manquants"].split(","):
                pdf.cell(200, 6, txt=to_latin1(f"     - {attribut.strip()}"), ln=True)
        pdf.ln(2)
    return pdf

# === Export PDF poste sélectionné ===
if st.button("📄 Exporter en PDF"):
    pdf = export_pdf(poste_choisi, df_poste_manquants, taux_completude, label)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{poste_choisi}_diagnostic.pdf">📥 Télécharger le PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

# === Export ZIP global ===
if st.button("📦 Exporter tous les postes en ZIP"):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for poste in sorted(df_complet["Poste"].dropna().unique()):
            df_total = df_complet[df_complet["Poste"] == poste]
            df_m = df_manquants[df_manquants["Poste"] == poste]
            total_att = sum(attributs_attendus.get(l["Type d'équipement"], 0) for _, l in df_total.iterrows())
            manq_att = sum(len([x.strip() for x in l["Attributs manquants"].split(",") if x.strip()]) for _, l in df_m.iterrows())
            taux = 100.0 if total_att == 0 else round(100 * (1 - manq_att / total_att), 1)
            label = "🔴 Très mauvais" if taux < 87.5 else "🟢 Excellent" if taux > 97.5 else "🟡 Correct"
            pdf = export_pdf(poste, df_m, taux, label)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            zip_file.writestr(f"{poste}_diagnostic.pdf", pdf_bytes)
    zip_buffer.seek(0)
    zip_b64 = base64.b64encode(zip_buffer.read()).decode()
    href_zip = f'<a href="data:application/zip;base64,{zip_b64}" download="diagnostics_{datetime.today().strftime('%Y%m%d')}.zip">📥 Télécharger tous les PDF (ZIP)</a>'
    st.markdown(href_zip, unsafe_allow_html=True)

# === Signature ===
st.markdown('<div class="signature">created by Luther FRANCO RONDISSON</div>', unsafe_allow_html=True)
