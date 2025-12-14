import streamlit as st
from data_loader import load_data, get_df
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from plotting_utils import (
    plot_seaborn_histogram, 
    plot_plotly_pie, 
    plot_bar, 
    plot_plotly_bar_ranking,
    plot_genre_rating_heatmap, 
    plot_animated_rating_evolution, 
    plot_stacked_activity_rating_count,
    load_wordcloud_figure)

st.set_page_config(
    page_title="Dataset Exploration",
    page_icon="📊",
    layout="wide"
)

# --- Data Loading ---
data_store = load_data()
df = get_df(data_store, 'main_df')
movies_by_rating = get_df(data_store, 'movies_by_rating')
genre_analysis_df = get_df(data_store, 'genre_analysis_df')

st.title("The Netflix Prize Dataset Exploration")

if df.empty or movies_by_rating.empty:
    st.error("DataFrames for exploration are empty. Please check your data export and loading.")
    st.stop() # Stop the app execution if data is missing

# ----------------------------------------------------
# SECTION 1: Histogram with Interactive Menu 
# ----------------------------------------------------
st.header("Variable distribution - histogram")

# --- Sidebar Controls for Section 1 ---
st.sidebar.header("Histogram Controls")

HISTOGRAM_COLS = ['rating', 'year', 'rating_date']




available_cols = [col for col in HISTOGRAM_COLS if col in df.columns]


# Determine the default index
try:
    default_index = available_cols.index('rating')
except ValueError:
    default_index = 0

histogram_x_col = st.sidebar.selectbox(
    "Select X-axis Column:", 
    options=available_cols, # Use the limited, filtered list
    index=default_index,
    key='hist_x_col'
)

# Identify numerical columns for the x-axis
numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
try:
    default_index = numeric_cols.index('rating')
except ValueError:
    # Fallback to the first column if 'rating' is not found
    default_index = 0



histogram_bins = st.sidebar.slider(
    "Number of Bins:", 
    min_value=5, 
    max_value=50, 
    value=10, 
    step=5,
    key='hist_bins'
)

# --- Visualization ---
with st.container():
    plot_seaborn_histogram(
        df=df, 
        x_col=histogram_x_col, 
        bins=histogram_bins,
        title=f"Distribution of {histogram_x_col.title()} (Bins: {histogram_bins})"
    )


st.markdown("---")



# ----------------------------------------------------
# SECTION 2: Categorical Distribution 
# ----------------------------------------------------
st.header("Categorical Distribution - Pie Chart")

# --- Sidebar Controls for Section 3 ---
st.sidebar.header("Pie Chart Controls")

# Define columns for pie chart 
PIECHART_COLS = ['decade', 'rating_category', 'activity_level', 'genres']


available_pie_cols = [col for col in PIECHART_COLS if col in df.columns]

# Set the default selection to 'decade' if available, otherwise the first available column
try:
    default_pie_index = available_pie_cols.index('rating_category')
except ValueError:
    default_pie_index = 0

pie_category_col = st.sidebar.selectbox(
    "Select Category Column:", 
    options=available_pie_cols, # <--- CORRECTED: Using the filtered list
    index=default_pie_index,
    key='pie_category'
)

# --- Visualization ---
with st.container():
    # Call the plotting function
    plot_plotly_pie(
        df=df,
        category_col=pie_category_col,
        title=f"Distribution by {pie_category_col.replace('_', ' ').title()}"
    )

#BAR PLOTS 

st.header(" Metric Comparison (Count or Average)")

st.sidebar.header(" Metric Plot Controls")

METRIC_COLS = ['decade', 'activity_level', 'genres'] 
available_metric_cols = [col for col in METRIC_COLS if col in df.columns]

if not available_metric_cols:
    st.warning("No suitable columns found for Metric Comparison.")
    st.stop()


# 4a. Metric Type Selection
metric_type = st.sidebar.radio(
    "Select Metric to Visualize:",
    options=['Total Ratings (Count)', 'Average Rating'],
    key='metric_radio'
)

# 4b. Category Selection
metric_category_col = st.sidebar.selectbox(
    "Select Category to Group By:", 
    options=available_metric_cols,
    index=0,
    key='metric_category_select'
)

# --- Visualization ---
with st.container():
    plot_bar(
        df=df,
        category_col=metric_category_col,
        metric_type=metric_type,
        title=f"{metric_type} by {metric_category_col.replace('_', ' ').title()}",
        genre_analysis_df=genre_analysis_df
    )


# ----------------------------------------------------
#Stacked Count of Ratings by Activity Level
# ----------------------------------------------------
st.header("Ratings by customer activity level")
st.markdown("This chart visualizes how many ratings fall into each Rating Category (Low, Neutral, High) across different Activity Levels (Low, Medium, High).")

if not df.empty:
    with st.container():
        plot_stacked_activity_rating_count(
            df=df, 
            title="Total Ratings Count by Activity Level and Rating Category"
        )
else:
    st.warning("Main DataFrame is required for this stacked bar chart.")




# ----------------------------------------------------
# Correlation heatmap, rating and genres 
# ----------------------------------------------------
st.header("Feature Correlation Heatmap")

st.info("The heatmap below shows the correlation between the movie rating, and the presence of each genre. Since a movie can have multiple genres, multi-hot encoding is used.")

with st.container():
    plot_genre_rating_heatmap(
        df=df, # Pass your main DataFrame
        title="Correlation Matrix: Rating and Genres"
    )


# ----------------------------------------------------
# Movie Ranking by weighted rating 
# ----------------------------------------------------
st.header("Title Ranking by weighted rating ")
st.sidebar.header("Ranking Plot Controls")


# 1. Data Preparation: 
ranking_df = movies_by_rating.copy()

# Ensure the ranking is performed on a full dataset first before slicing
ranking_df = ranking_df.sort_values(by='weighted_rating', ascending=False)


# 2. Base Limit (Top 20): Filter the data to the top 20 ranked entries
ranking_base = ranking_df.head(20)


# 3. Sidebar Slider for Visualization Count
num_to_display = st.sidebar.slider(
    "Select number of top movies to visualize:",
    min_value=1,
    max_value=20,
    value=10, # Default to showing the top 15
    step=1
)

# 4. Final Filtering based on Slider
final_ranking_df = ranking_base.head(num_to_display)

# 5. Visualization: Call your ranking function
with st.container():
    plot_plotly_bar_ranking(
        df=final_ranking_df,
        x_col='weighted_rating',  # X-axis is now the Weighted Rating
        y_col='title', 
        title=f"Top {num_to_display} Titles by Weighted Rating",
        ascending_order=False # Highest rated movie (highest bar) goes to the top
    )




st.header("Animated Rating Evolution of Top 10 Movies")
st.info("Watch the yearly average rating change for the Top 10 highest-rated movies (by Weighted Rating).")

# CRITICAL CHECK: Ensure both required DataFrames are present before calling the plot
if not df.empty and not movies_by_rating.empty:
    with st.container():
        plot_animated_rating_evolution(
            # df_main is the full history of all ratings
            df_main=df, 
            
            # movies_by_rating is the stats DF used to determine the top 10 movies
            movies_by_rating=movies_by_rating
        )
else:
    st.warning("Cannot display animated chart: Both main data (df) and movie statistics (movies_by_rating) are required.")



# WORDCLOUD 
st.title("Word Cloud Visualization")


FIXED_ARTICLE_URL = "https://www.theguardian.com/media/2025/aug/28/bland-easy-to-follow-for-fans-of-everything-what-has-the-netflix-algorithm-done-to-our-films"




# 1. Input Widget: this is a read-only input box that shows the article we used 
st.text_input(
    "Source Article URL:", 
    value=FIXED_ARTICLE_URL,
    disabled=True, # Makes the box read-only
    label_visibility="visible"
)

st.header("Generated Word Cloud")

# --- Start Automatic Figure Generation/Display ---
try:
    # 3. Call the function using the FIXED_ARTICLE_URL
    with st.spinner('Scraping and generating Word Cloud...'):
        figure = load_wordcloud_figure(FIXED_ARTICLE_URL)
    
    # 4. Display the result
    if figure:
        st.pyplot(figure)
        plt.close(figure)
        
    else:
        # Fallback for scraping failure
        st.error("Error: Could not find article content or generate the figure for the fixed URL.")

except Exception as e:
    st.error(f"An unexpected error occurred during processing: {e}")