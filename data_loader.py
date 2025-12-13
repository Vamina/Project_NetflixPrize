import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    """
    Loads all DataFrames from CSV files and caches the result.
    
    NOTE: Because CSV doesn't preserve data types, you might need to add
    explicit type conversions (e.g., to_datetime, astype) here if your 
    Streamlit app throws errors.
    """
    data_dict = {}
    
    # List of files to load (names must match the saved files)
    files_to_load = {
        'main_df': 'main_df.csv',
        'movies_by_rating': 'movies_by_rating.csv',
        
    }
    
    load_successful = True
    
    for key, filename in files_to_load.items():
        file_path = os.path.join('data', filename)
        try:
            df = pd.read_csv(file_path)
            
            # --- CRITICAL CSV TYPE CONVERSION ---
            if key == 'main_df':
                # Convert 'date' column to datetime objects
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce') 
                
                # Ensure 'year' is treated as an integer (if it exists)
                if 'year' in df.columns:
                    # Coerce errors to NaN then convert to integer for proper plotting
                    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64') 
                
                # Rename 'date' to 'rating_date' for clarity in the UI
                if 'date' in df.columns:
                    df.rename(columns={'date': 'rating_date'}, inplace=True)
            
            if 'rating' in df.columns:
                df['rating'] = pd.to_numeric(df['rating'], errors='coerce').astype('Int64')
            
            # 3. Define and apply ORDERED CATEGORICAL TYPES
                
                # ACTIVITY LEVEL: Low, Medium, High
                if 'activity_level' in df.columns:
                    level_order = ['Low', 'Medium', 'High']
                    df['activity_level'] = pd.Categorical(
                        df['activity_level'], 
                        categories=level_order, 
                        ordered=True
                    )

                # RATING CATEGORY: Low, Neutral, High
                if 'rating_category' in df.columns:
                    category_order = ['Low', 'Neutral', 'High']
                    df['rating_category'] = pd.Categorical(
                        df['rating_category'],
                        categories=category_order,
                        ordered=True
                    )
            
            data_dict[key] = df
            
        except FileNotFoundError:
            st.error(f"Error: File '{file_path}' not found. Did you run your Jupyter export script?")
            load_successful = False
            break
            
    if not load_successful:
        return None
        
    return data_dict

def get_df(data_dict, key):
  
    if data_dict:
        return data_dict.get(key, pd.DataFrame()) # Return empty DataFrame if key not found
    return pd.DataFrame() # Return empty DataFrame if loading failed