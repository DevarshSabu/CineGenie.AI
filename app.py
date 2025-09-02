import pandas as pd
import re
import streamlit as st
import spacy
from fuzzywuzzy import fuzz, process   # ✅ required for fuzzy matching

# ================================
# Load Dataset
# ================================
df = pd.read_excel("final dataset movie.xlsx")   # <-- replace with your dataset path

# Normalize column names
df.columns = [col.strip().capitalize() for col in df.columns]

# Ensure essential columns exist
required_cols = ["Movie name", "Rating", "Language", "Actor", "Genre"]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Dataset missing required column: {col}")

# ================================
# Load NLP Model
# ================================
nlp = spacy.load("en_core_web_sm")

# ================================
# Helper Functions
# ================================
def extract_keywords(user_query):
    """Extract possible actor, genre, language, rating from query."""
    doc = nlp(user_query.lower())
    query_tokens = [token.text for token in doc if not token.is_stop]

    actor, genre, language, rating = None, None, None, None

    # Actors
    all_actors = df["Actor"].dropna().astype(str).unique().tolist()
    best_actor, score = process.extractOne(user_query, all_actors)
    if score > 80:
        actor = best_actor

    # Genres
    all_genres = df["Genre"].dropna().astype(str).unique().tolist()
    best_genre, score = process.extractOne(user_query, all_genres)
    if score > 80:
        genre = best_genre

    # Languages
    all_languages = df["Language"].dropna().astype(str).unique().tolist()
    best_lang, score = process.extractOne(user_query, all_languages)
    if score > 80:
        language = best_lang

    # Ratings (find numbers like 8.5, 7 etc.)
    rating_match = re.findall(r"\d+(\.\d+)?", user_query)
    if rating_match:
        try:
            rating = float(rating_match[0])
        except:
            pass

    return actor, genre, language, rating


def search_movies(user_query):
    """Filter movies from dataset based on extracted keywords."""
    actor, genre, language, rating = extract_keywords(user_query)
    filtered = df.copy()

    if actor:
        filtered = filtered[filtered["Actor"].str.contains(actor, case=False, na=False)]
    if genre:
        filtered = filtered[filtered["Genre"].str.contains(genre, case=False, na=False)]
    if language:
        filtered = filtered[filtered["Language"].str.contains(language, case=False, na=False)]
    if rating:
        filtered = filtered[filtered["Rating"] >= rating]

    if filtered.empty:
        return f"No movies found for: {user_query}"
    else:
        sorted_filtered = filtered.sort_values(by="Rating", ascending=False).reset_index(drop=True)
        sorted_filtered.insert(0, "Sl. No.", range(1, len(sorted_filtered) + 1))  # 👈 Adds Sl. No. column
        return sorted_filtered[["Movie name", "Actor", "Genre", "Language", "Rating"]]
    
    
# ================================
# Streamlit UI
# ================================

import streamlit as st

st.markdown("""
    <style>
        /* ✅ Import MILKER font — replace with actual hosted URL if available */
        @font-face {
            font-family: 'MILKER';
            src: url('https://your-font-host.com/milker.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
        }

        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

/* 🌌 Blurred Background Image */
body::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('https://i.pinimg.com/1200x/87/9e/f2/879ef2322e55c5de5011d3bb762bf45a.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: blur(2px); /* ✅ This applies the blur */
    z-index: -1; /* Push behind content */
}

        /* 🧊 Overlay to control opacity */
        .stApp {
            background-color: rgba(0, 0, 0, .8); /* 80% opacity black overlay */
        }

/* 🧊 Frosted Glass Effect for DataFrame */
[data-testid="stDataFrame"] {
    background-color: rgba(255, 255, 255, 0.1); /* Transparent white */
    backdrop-filter: blur(6px); /* Apply blur */
    -webkit-backdrop-filter: blur(6px); /* Safari support */
    border-radius: 12px;
    padding: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2); /* Soft border */
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2); /* Optional depth */
}

        .centered-text {
            text-align: center;
            font-family: 'Poppins', sans-serif;
            color: white;
        }

        h1.centered-text {
            font-family: 'MILKER', sans-serif;
            font-size: 3em;
            margin-top: 20px;
            margin-bottom: -30px;
            color: white;
        }

        p.centered-text {
            font-size: 1em;
            margin-top: 0px;
            margin-bottom: -20px;
        }

        input[type="text"] {
            font-family: 'Poppins', sans-serif;
            color: white !important;
        }
        
        

        label[data-testid="stTextInputLabel"] {
            display: none !important; /* 🚫 Hide the label completely */
        }

        ::placeholder {
            font-style: italic;
            font-weight: 300;
            font-size: .9em;
            color: #dddddd;
            font-family: 'Poppins', sans-serif;
            opacity: 40%;
        }
    </style>
""", unsafe_allow_html=True)

# 🎬 Title and instructions with styling
st.markdown("<h1 class='centered-text'>CineGenie.AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered-text'><em>summon the genie, for the world of cinematic magic</em></p>", unsafe_allow_html=True)

# 📝 Input box with styled placeholder (no label)
user_query = st.text_input("", placeholder="e.g. Malayalam action movie with Mohanlal")

# 🔍 Results
if user_query:
    results = search_movies(user_query)
    if isinstance(results, str):
        st.warning(results)
    else:
        st.dataframe(results.reset_index(drop=True)) 
        