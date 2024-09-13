import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib

# Load CSV data
path = 'games.csv'
column_names = ['name', 'desc_snippet', 'recent_reviews', 'all_reviews', 'release_date',
                'popular_tags', 'game_details', 'languages', 'genre', 'game_description',
                'mature_content', 'original_price', 'discount_price']   
df = pd.read_csv(path, names=column_names, encoding='ISO-8859-1', low_memory=True)

# Selecting only relevant columns
df1 = df[['name', 'desc_snippet', 'popular_tags', 'genre', 'original_price']]

# Delete missing values
df2 = pd.DataFrame(df1.dropna())

# Create TF-IDF matrix
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df2["desc_snippet"])

# Cosine similarity matrix
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Asking for user input via Streamlit
game = st.text_input("Please enter a game you like:").lower()

# Ensure all names in the dataset are lowercase
df2['name'] = df2['name'].str.lower()

# Token-based matching function
def find_similar_games(game, game_list):
    vectorizer = CountVectorizer().fit_transform([game] + game_list)
    vectors = vectorizer.toarray()
    cosine_similarities = cosine_similarity(vectors)
    similar_games_idx = cosine_similarities[0][1:].argsort()[::-1]
    return game_list[similar_games_idx[0]]

# Function using difflib to find the closest game name
def get_closest_match(game_name, game_list):
    matches = difflib.get_close_matches(game_name, game_list, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Create an index series for the 'name' column to map game names to their index in the dataframe
indices = pd.Series(df2.index, index=df2['name']).drop_duplicates()

# If the user has entered a game name, proceed with the recommendation
if game:
    # First, try difflib to find the closest game
    closest_game = get_closest_match(game, df2['name'].tolist())

    # Check if a difflib match was found
    if closest_game:
        st.write(f"The closest match found is: '{closest_game}'")

        game_index = indices[closest_game]

        # Calculate similarity scores for the closest game
        sim_scores = pd.DataFrame(cosine_sim[game_index], columns=["score"])

        # Get the top 10 similar games (excluding the input game itself)
        game_indices = sim_scores.sort_values("score", ascending=False)[1:11].index

        # Display the recommended games
        st.write(f"Since you searched for '{closest_game}', here are some similar games:")
        st.table(df2["name"].iloc[game_indices])

    else:
        # If no difflib match is found, use token-based matching
        st.write(f"No exact match for '{game}', trying to find similar games using token-based matching...")
        closest_game = find_similar_games(game, df2['name'].tolist())

        if closest_game:
            st.write(f"Did you mean '{closest_game}'?")

            game_index = indices[closest_game]

            # Calculate similarity scores for the closest game
            sim_scores = pd.DataFrame(cosine_sim[game_index], columns=["score"])

            # Get the top 10 similar games
            game_indices = sim_scores.sort_values("score", ascending=False)[1:11].index

            # Display the recommended games
            st.write(f"Since you searched for '{closest_game}', here are some similar games:")
            st.table(df2["name"].iloc[game_indices])
        else:
            st.write(f"Sorry, no similar game was found in the dataset.")

# Streamlit app
st.title("🎮Description Based Recommender🎮")
st.write("🔎 Find similar games for you based on their description 🔎")
