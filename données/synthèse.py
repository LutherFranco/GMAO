import pandas as pd
import os

# === 1. PARAMÈTRES ===
dossier = "./données/"
colonnes_ignorer = ['Emplacement', 'ASDU', 'Nom Poste Reseau']
motifs_vides = ["", "VIDE"]

# === 2. Fichiers Excel à traiter ===
fichiers_excel = [f for f in os.listdir(dossier) if f.endswith(".xlsx") or f.endswith(".xlsm")]

# === 3. Stockage des attributs manquants ===
liste_manquants = []

for fichier in fichiers_excel:
    equipement = os.path.splitext(fichier)[0].strip().replace(" ", "_")
    chemin = os.path.join(dossier, fichier)

    # === 3.1 Ouverture sécurisée du fichier ===
    try:
        xl = pd.ExcelFile(chemin)
        if not xl.sheet_names:
            print(f"⛔ Aucun onglet dans {fichier} — fichier ignoré")
            continue
        feuille = xl.sheet_names[0]
        df = xl.parse(feuille)
        print(f"📄 Lecture : {fichier} (onglet : {feuille})")
    except Exception as e:
        print(f"⛔ Erreur lecture fichier {fichier} : {e}")
        continue

    if "Emplacement" not in df.columns:
        print(f"⛔ Colonne 'Emplacement' absente dans {fichier} — ignoré")
        continue

    # === 3.2 Nettoyage et détection de poste ===
    df.replace(motifs_vides, pd.NA, inplace=True)
    df["Poste"] = df["Emplacement"].astype(str).str[:5]

        # === 3.3 Colonnes à vérifier (vraiment) ===
    colonnes_a_verifier = [col for col in df.columns if col not in colonnes_ignorer + ["Poste"]]

    # === 3.4 Créer un DataFrame avec juste les colonnes utiles ===
    df_utiles = df[["Poste", "Emplacement"] + colonnes_a_verifier].copy()

    # === 3.5 Préfixage des colonnes à vérifier uniquement ===
    df_utiles.rename(columns={col: f"{equipement}_{col}" for col in colonnes_a_verifier}, inplace=True)


    for _, ligne in df_utiles.iterrows():
        poste = ligne["Poste"]
        for col in ligne.index:
            if col not in ["Emplacement", "Poste"] and pd.isna(ligne[col]):
                liste_manquants.append({
                    "Poste": poste,
                    "Attribut manquant": col,
                    "Équipement": equipement
                })



# === 4. Résultats consolidés ===
df_manquants = pd.DataFrame(liste_manquants)

if df_manquants.empty:
    print("✅ Aucun attribut manquant détecté.")
else:
    df_synthese = df_manquants.groupby("Poste").agg({
        "Attribut manquant": lambda x: ", ".join(sorted(set(x))),
        "Équipement": lambda x: ", ".join(sorted(set(x)))
    }).reset_index()

    # === 5. Export Excel ===
    with pd.ExcelWriter("résumé_attributs_manquants.xlsx", engine="openpyxl") as writer:
        df_manquants.to_excel(writer, sheet_name="Détail", index=False)
        df_synthese.to_excel(writer, sheet_name="Synthèse par poste", index=False)

    print("✅ Export terminé : résumé_attributs_manquants.xlsx")
