from data_loader import load_data, get_df
# %%

# --- Data Loading ---
data_store = load_data()
df = get_df(data_store, 'main_df')
movies_by_rating = get_df(data_store, 'movies_by_rating')
genre_analysis_df = get_df(data_store, 'genre_analysis_df')

# %%
print(df['genres'])
# %%
