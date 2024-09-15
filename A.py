import streamlit as st
import pandas as pd
import re

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

# Function to clean the price data (removing non-numeric characters)
def clean_price(price):
    # Use regex to remove any non-numeric characters except periods
    price = re.sub(r'[^\d.]', '', str(price))
    try:
        return float(price)
    except ValueError:
        return None

# Apply the price cleaning function to the 'original_price' column
df2['original_price'] = df2['original_price'].apply(clean_price)

# Drop any rows where the price could not be converted to a valid float
df2 = df2.dropna(subset=['original_price'])

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
            "Price": similar_games['original_price'].apply(lambda x: f"{x:.2f}").values  # Format to 2 decimal places
        })

        # Reset the index to start from 1 instead of 0
        recommended_games.index = range(1, len(recommended_games) + 1)

        # Display the recommended games
        st.write(f"Here are some games with a price similar to {game_price}:")
        st.table(recommended_games.head(10))
    else:
        st.write(f"No similar games found within ±5 price range of {game_price}.")
