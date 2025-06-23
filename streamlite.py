import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="🛡️ Évaluation des Risques", layout="wide")


st.title("Évaluation des Risques pour Événements Publics")
st.markdown("""
Entrez les détails de l’événement pour évaluer son **niveau de risque** et obtenir des **recommandations de sécurité** personnalisées.
""")

st.markdown(
    """
    <style>
    /* === Style général de la page === */
    .main {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #222222;
    }

    /* === Conteneur du formulaire === */
    form {
        background: #B0E0E6; /* blanc translucide */
        padding: 30px 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        max-width: 600px;
        margin: auto;
        transition: box-shadow 0.3s ease;
    }
    form:hover {
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }

    /* === Inputs & selects === */
    div.stTextInput > div > input,
    div.stSelectbox > div > div > div,
    div.stNumberInput > div > input {
        background-color: #f0f4ff !important;
        border: 2px solid #4a90e2 !important;
        border-radius: 9px !important;
        padding: 8px 9px !important;
        font-size: 1rem;
        color: #2c3e50 !important;  /* Texte sombre visible */
        font-weight: 600;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    div.stTextInput > div > input:focus,
    div.stSelectbox > div > div > div:hover,
    div.stNumberInput > div > input:focus {
        border-color: #2a65ca !important;
        box-shadow: 0 0 8px #2a65caaa !important;
        outline: none !important;
        color: #2c3e50 !important; /* Texte visible en focus */
    }

    /* === Bouton submit === */
    div.stButton > button {
        background-color: #4a90e2;
        color: white;
        font-weight: 700;
        border-radius: 20px;
        padding: 14px 36px;
        font-size: 1.1rem;
        border: none;
        box-shadow: 0 5px 15px rgba(74, 144, 226, 0.4);
        transition: background-color 0.4s ease, box-shadow 0.4s ease;
        width: 100%;
        cursor: pointer;
        margin-top: 20px;
    }
    div.stButton > button:hover {
        background-color: #2a65ca;
        box-shadow: 0 8px 25px rgba(42, 101, 202, 0.6);
        color: #e0eaff;
    }
    div.stButton > button:active {
        background-color: #1b3d82;
        box-shadow: 0 4px 12px rgba(27, 61, 130, 0.8);
    }

    /* === Titres === */
    h1, h2, h3, h4 {
        font-weight: 800 !important;
        color: #34495e;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 0 1px 2px #cbd5e0;
    }

    /* === Textes === */
    p, label, .css-1y4p8pa {
        font-size: 1rem;
        line-height: 1.6;
        color: #34495e;
    }

    /* === Dataframe style === */
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0 8px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .stDataFrame th {
        background-color: #4a90e2 !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 12px 15px !important;
        text-align: center !important;
    }
    .stDataFrame td {
        background-color: #f8fbff !important;
        padding: 12px 15px !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }

    /* === Scroll bar personnalisé === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f0f4ff;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #4a90e2;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #2a65ca;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

villes = {
    "Casablanca": {"lat": 33.5731, "lon": -7.5898, "criminalité": 4, "colère": 3},
    "Rabat": {"lat": 34.0209, "lon": -6.8417, "criminalité": 2, "colère": 2},
    "Fès": {"lat": 34.0331, "lon": -5.0003, "criminalité": 3, "colère": 3},
    "Marrakech": {"lat": 31.6295, "lon": -7.9811, "criminalité": 3, "colère": 4},
    "Tanger": {"lat": 35.7595, "lon": -5.8339, "criminalité": 2, "colère": 2},
    "Agadir": {"lat": 30.4278, "lon": -9.5981, "criminalité": 2, "colère": 1}
}

if "resultats" not in st.session_state:
    st.session_state.resultats = None
if "save" not in st.session_state:
    st.session_state.save = False

with st.form("evaluation_form"):
    col1, col2 = st.columns(2)
    with col1:
        participants = st.selectbox("👥 Nombre de participants", ["<100", "100-500", "500-5000", ">5000"])
        event_type = st.selectbox("🎉 Type d'événement", ["Festif", "Politique", "Religieux", "Sportif"])
        ville = st.selectbox("🏙️ Ville de l’événement", list(villes.keys()))
    with col2:
        time = st.selectbox("🕒 Moment", ["Jour", "Nuit"])
        history = st.selectbox("📈 Historique d'incidents dans la zone", ["Aucun", "Faible", "Moyen", "Élevé"])
        save = st.checkbox("💾 Enregistrer l’évaluation")
    submitted = st.form_submit_button("Évaluer")

if submitted:
    def get_score(participants, event_type, city, time, history):
        base = 0
        base += {"<100": 1, "100-500": 2, "500-5000": 3, ">5000": 4}[participants]
        base += {"Festif": 1, "Sportif": 2, "Religieux": 3, "Politique": 4}[event_type]
        base += {"Jour": 0, "Nuit": 2}[time]
        base += {"Aucun": 0, "Faible": 1, "Moyen": 2, "Élevé": 3}[history]
        ville_score = (villes[city]["criminalité"] + villes[city]["colère"]) / 2
        return base + ville_score

    score = get_score(participants, event_type, ville, time, history)

    st.session_state.resultats = {
        "participants": participants,
        "event_type": event_type,
        "ville": ville,
        "time": time,
        "history": history,
        "score": score,
        "save": save,
    }

if st.session_state.resultats:
    r = st.session_state.resultats

    st.markdown("---")
    st.subheader("🔢 Résultat de l’évaluation")
    st.markdown(f"**Score total :** `{r['score']:.1f} / 16+`")

    if r['score'] <= 5:
        st.success("🟢 Risque faible : surveillance minimale")
    elif r['score'] <= 10:
        st.warning("🟡 Risque modéré : mesures renforcées recommandées")
    else:
        st.error("🔴 Risque élevé : plan de sécurité renforcé obligatoire")

    def agents_securite(nb_participants):
        mapping = {
            "<100": "1 à 2 agents",
            "100-500": "12 à 20 agents",
            "500-5000": "50 à 250 agents",
            ">5000": "Plus de 400 agents"
        }
        return mapping.get(nb_participants, "À déterminer")

    st.subheader("📋 Recommandations de sécurité")
    recs = []
    recs.append(f"👮 Nombre recommandé d’agents de sécurité : **{agents_securite(r['participants'])}**")

    if r['score'] <= 5:
        recs.extend([
            "✔️ Pas de dispositif spécial requis",
            "✔️ Surveillance de routine"
        ])
    elif r['score'] <= 10:
        recs.extend([
            "✔️ Renforcer la sécurité privée",
            "✔️ Plan d’évacuation obligatoire",
            "✔️ Présence médicale recommandée"
        ])
    else:
        recs.extend([
            "✔️ Présence policière nécessaire",
            "✔️ Contrôle des accès rigoureux",
            "✔️ Dispositif d'évacuation complet",
            "✔️ Poste médical avancé sur place"
        ])

    for rec in recs:
        st.write(rec)

    if r["save"]:
        csv_file = "historique_risques.csv"
        data = {
            "Date": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "Ville": [r["ville"]],
            "Participants": [r["participants"]],
            "Type": [r["event_type"]],
            "Moment": [r["time"]],
            "Historique": [r["history"]],
            "Score": [r["score"]]
        }
        df_new = pd.DataFrame(data)
        try:
            if os.path.exists(csv_file):
                df_old = pd.read_csv(csv_file)
                df = pd.concat([df_old, df_new], ignore_index=True)
            else:
                df = df_new
            df.to_csv(csv_file, index=False)
            st.success("✅ Évaluation enregistrée avec succès.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la sauvegarde : {e}")

st.markdown("---")
st.subheader("🗺️ Carte des villes marocaines avec score moyen de risque")

lat_center = sum([v["lat"] for v in villes.values()]) / len(villes)
lon_center = sum([v["lon"] for v in villes.values()]) / len(villes)

m = folium.Map(location=[lat_center, lon_center], zoom_start=6)

for city, info in villes.items():
    ville_score = (info["criminalité"] + info["colère"]) / 2
    color = "green" if ville_score <= 2 else "orange" if ville_score <= 3 else "red"
    folium.CircleMarker(
        location=[info["lat"], info["lon"]],
        radius=12,
        popup=f"{city}: Score ville = {ville_score:.1f}",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7
    ).add_to(m)

col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st_folium(m, width=1100, height=700)

st.markdown("---")
st.subheader(" Historique des évaluations sauvegardées")

csv_file = "historique_risques.csv"
if os.path.exists(csv_file):
    try:
        df_hist = pd.read_csv(csv_file)
        st.dataframe(df_hist.sort_values(by="Date", ascending=False).reset_index(drop=True))

        st.subheader(" Distribution des scores")
        fig, ax = plt.subplots()
        ax.hist(df_hist["Score"], bins=range(0, 20), color='skyblue', edgecolor='black')
        ax.set_xlabel("Score de risque")
        ax.set_ylabel("Nombre d'événements")
        ax.set_title("Distribution des scores enregistrés")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Erreur de lecture de l'historique : {e}")
else:
    st.info("Aucune évaluation enregistrée pour le moment.")
