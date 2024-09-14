import streamlit as st
import pandas as pd

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

# Asking for user input via Streamlit (Expecting a number for price)
game_price_input = st.text_input("Please enter a price you like:")

# Ensure input is a valid number
try:
    game_price = float(game_price_input) if game_price_input else None
except ValueError:
    game_price = None
    st.write("Please enter a valid numeric price.")

# Function to find similar games within a price range
def find_similar_games_by_price(price, price_range=5):
    similar_games = df2[(df2['original_price'] >= price - price_range) & 
                        (df2['original_price'] <= price + price_range)]
    return similar_games

# If the user has entered a valid price, proceed with the recommendation
if game_price is not None:
    # Find similar games based on the input price (±5 range)
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
        st.write(f"Here are some games with a price similar to {game_price}:")
        st.table(recommended_games)
    else:
        st.write(f"No similar games found within ±5 price range of {game_price}.")
