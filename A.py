import streamlit as st
import pandas as pd
import difflib

# Load CSV data
path = 'games.csv'
column_names = ['name', 'desc_snippet', 'recent_reviews', 'all_reviews', 'release_date',
                'popular_tags', 'game_details', 'languages', 'genre', 'game_description',
                'mature_content', 'original_price', 'discount_price']
df = pd.read_csv(path, names=column_names, encoding='ISO-8859-1', low_memory=True)

# Selecting only relevant columns
df1 = df[['name', 'desc_snippet', 'original_price']]

# Delete missing values
df2 = pd.DataFrame(df1.dropna())

# Convert original_price to numeric (in case it’s a string)
df2['original_price'] = pd.to_numeric(df2['original_price'], errors='coerce')

# Streamlit app
st.title("🎮Price Based Game Recommender🎮")
st.write("🔎 Find games within a similar price range 🔎")

# Asking for user input via Streamlit
game = st.text_input("Please enter a game you like:").lower()

# Ensure all names in the dataset are lowercase
df2['name'] = df2['name'].str.lower()

# Function using difflib to find the closest game name
def get_closest_match(game_name, game_list):
    matches = difflib.get_close_matches(game_name, game_list, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Create an index series for the 'name' column to map game names to their index in the dataframe
indices = pd.Series(df2.index, index=df2['name']).drop_duplicates()

# Function to find similar games within a price range
def find_similar_games_by_price(game_price, price_range=5):
    similar_games = df2[(df2['original_price'] >= game_price - price_range) & 
                        (df2['original_price'] <= game_price + price_range)]
    return similar_games

# If the user has entered a game name, proceed with the recommendation
if game:
    # First, try difflib to find the closest game
    closest_game = get_closest_match(game, df2['name'].tolist())

    # Check if a difflib match was found
    if closest_game:
        st.write(f"The closest match found is: '{closest_game}'")

        game_index = indices[closest_game]
        game_price = df2.loc[game_index, 'original_price']

        # Find similar games based on price (±5 range)
        similar_games = find_similar_games_by_price(game_price)

        if not similar_games.empty:
            # Create a DataFrame with the similar games and their prices
            recommended_games = pd.DataFrame({
                "Game Name": similar_games['name'].values,
                "Price": similar_games['original_price'].values
            })

            # Reset the index to remove the original index numbers
            recommended_games = recommended_games.reset_index(drop=True)

            # Display the recommended games
            st.write(f"Since you searched for '{closest_game}' (Price: {game_price}), here are some games with a similar price range:")
            st.table(recommended_games)
        else:
            st.write(f"No similar games found in the price range around '{closest_game}'.")

    else:
        st.write(f"No exact match for '{game}', trying to find similar games using token-based matching...")
        st.write(f"Sorry, no similar game was found in the dataset.")
