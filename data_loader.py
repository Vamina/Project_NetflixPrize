import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    """
    Loads all DataFrames from CSV files, performs necessary type conversions,
    and caches the result.
    """
    data_dict = {}
    
    files_to_load = {
        'main_df': 'main_df.csv',
        'movies_by_rating': 'movies_by_rating.csv',
        
    }
    
    load_successful = True
    
    for key, filename in files_to_load.items():
        file_path = os.path.join('data', filename)
        try:
            df = pd.read_csv(file_path)
            
            # --- CRITICAL CSV TYPE CONVERSION & ORDERED CATEGORICALS ---
            if key == 'main_df':
                
                # Date, Year, and Rating Conversions
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce') 
                    df.rename(columns={'date': 'rating_date'}, inplace=True)
                
                if 'year' in df.columns:
                    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64') 
                                
                if 'rating' in df.columns:
                    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype('Int64')
                
                # Define and apply ORDERED CATEGORICAL TYPES (Activity Level, Rating Category)
                if 'activity_level' in df.columns:
                    level_order = ['Low', 'Medium', 'High']
                    df['activity_level'] = pd.Categorical(df['activity_level'], categories=level_order, ordered=True)

                if 'rating_category' in df.columns:
                    category_order = ['Low', 'Neutral', 'High']
                    df['rating_category'] = pd.Categorical(df['rating_category'], categories=category_order, ordered=True)
                
            
            data_dict[key] = df
            
        except FileNotFoundError:
            st.error(f"Error: File '{file_path}' not found. Did you run your Jupyter export script?")
            load_successful = False
            break
            
    if not load_successful:
        return None
    
    if 'main_df' in data_dict:
        df = data_dict['main_df']
    
    # Check for required columns BEFORE starting the analysis
        if 'rating' not in df.columns or 'genres' not in df.columns:
            st.warning("Skipping genre analysis: 'rating' or 'genres' column not found.")
            data_dict['genre_analysis_df'] = pd.DataFrame()
            return data_dict # Return early to prevent indexing errors

        # 1. Select columns and handle NaNs
        # We need both 'rating' and 'genres' to be present and non-null
        df_genre_analysis = df[['rating', 'genres']].copy().dropna(subset=['rating', 'genres'])
        
        # Check if any data remains after dropna
        if df_genre_analysis.empty:
            st.warning("Genre analysis: No rows remaining after dropping NaNs in 'rating'/'genres'.")
            data_dict['genre_analysis_df'] = pd.DataFrame()
            return data_dict

        # 2. Split + Explode: Prepare genres for grouping
        

        df_genre_analysis['genres'] = df_genre_analysis['genres'].str.strip()
        df_genre_analysis['genres'] = df_genre_analysis['genres'].str.split("|")
        
        # Explode the list into new rows
        df_genre_analysis = df_genre_analysis.explode("genres")
        
        # CRUCIAL POST-EXPLODE CLEANING: Strip and Capitalize for perfect grouping
        df_genre_analysis['genres'] = df_genre_analysis['genres'].str.strip()
        df_genre_analysis['genres'] = df_genre_analysis['genres'].str.capitalize()
        
        # 3. Groupby + Aggregate (Mean and Count)
        # The grouping logic here is correct and relies on the clean 'genres' column
        df_genre_analysis = (
            df_genre_analysis
            .groupby("genres")["rating"]
            .agg(['mean', 'count']) 
            .reset_index()
        )

        # 4. Rename columns
        df_genre_analysis = df_genre_analysis.rename(
            columns={"mean": "rating_avg", "count": "rating_count"}
        )
        
        # 5. Sort + reset index
        df_genre_analysis = (
            df_genre_analysis
            .sort_values(by="rating_avg", ascending=False)
            .reset_index(drop=True)
        )
        
        # Add the result to the data dictionary
        data_dict['genre_analysis_df'] = df_genre_analysis
        
        # OPTIONAL DEBUG: The debug print block must also follow the same indentation
        if 'genre_analysis_df' in data_dict:
            print("\n--- Genre Analysis Data Check ---")
            print("Columns:", data_dict['genre_analysis_df'].columns.tolist())
            print("Head:", data_dict['genre_analysis_df'].head())
            print("Average Rating Unique Values:", data_dict['genre_analysis_df']['rating_avg'].unique())
            print("-----------------------------------")
    
    return data_dict

def get_df(data_dict, key):
 
    if data_dict:
        # Return empty DataFrame if key not found, or if loading failed
        return data_dict.get(key, pd.DataFrame()) 
    return pd.DataFrame() # Return empty DataFrame if loading failed