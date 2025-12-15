import streamlit as st
from data_loader import load_data, get_df
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
from plotting_utils import (
    plot_plotly_histogram, 
    plot_plotly_pie, 
    plot_plotly_bar, 
    plot_plotly_bar_ranking,
    plot_genre_rating_heatmap, 
    plot_animated_rating_evolution, 
    plot_stacked_activity_rating_count,
    load_wordcloud_figure)

st.set_page_config(
    page_title="Neflix dataset app",
    page_icon="📊",
    layout="wide"
)

# Data loading - load the data (that are contained in a dict) and define dfs 
data_store = load_data()
df = get_df(data_store, 'main_df')
movies_by_rating = get_df(data_store, 'movies_by_rating')
genre_analysis_df = get_df(data_store, 'genre_analysis_df')


# Title and presentation text 

st.title("The Netflix Prize Dataset Exploration")


st.markdown("This app presents a subset of the Netflix Prize dataset. The Netflix dataset was originally released by Netflix for a competition aimed at improving their movie recommendation algorithm. It contains over over 100 million ratings from nearly 480,189 anonymous users across 17,770 movies. For this exploration, 500.000 lines of the original dataset were randomly sampled, and information as film title and genre have been added. ")



### PART 1 PRESENTATION OF THE DATASET 

#Title 

st.header("The dataset", divider = "yellow")
st.markdown("This view explains the columns and data types of the primary DataFrame (`df`) used across the application.")


# subtitle 
st.subheader("DataFrame Columns and Data Types")

# Display data info 
column_info = pd.DataFrame({
    'Column Name': df.columns,
    'Data Type': df.dtypes.astype(str)
})

st.dataframe(
    column_info, 
    hide_index=True, 
    use_container_width=True,
    column_config={
        "Column Name": st.column_config.TextColumn(width="large"),
        "Data Type": st.column_config.TextColumn(width="small"),
    }
)

st.markdown(f"**Total Columns:** {df.shape[1]}")

st.markdown("---")

# Display the first 10 rows of the data 
st.subheader("Sample Data (First 10 Rows)")
st.caption("A small preview of the data content.")

# Display the first 10 rows of the actual data
st.dataframe(
    df.head(10), 
    use_container_width=True
)

if df.empty or movies_by_rating.empty:
    st.error("DataFrames for exploration are empty. Please check your data export and loading.")
    st.stop() # Stop the app execution if data is missing




## PART 2 VISUALIZATION

#title

st.header("Data visualization", divider = "yellow")

# SIDEBAR HEADER 

st.sidebar.header("Plot controls ")


#PLOTS NOW 



# ----------------------------------------------------
# Histogram with Interactive Menu 
# ----------------------------------------------------

st.subheader("Numerical distribution - Histogram")


# Sidebar controls for histo
st.sidebar.subheader("Histogram Controls")

HISTOGRAM_COLS = ['rating', 'year', 'rating_date']




available_cols = [col for col in HISTOGRAM_COLS if col in df.columns]


# Selectbox: 

# Determine the default index
try:
    default_index = available_cols.index('rating')
except ValueError:
    default_index = 0

histogram_x_col = st.sidebar.selectbox(
    "Select X-axis Column:", 
    options=available_cols, 
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


# histogram parameters 
histogram_bins = st.sidebar.slider(
    "Number of Bins:", 
    min_value=5, 
    max_value=50, 
    value=10, 
    step=5,
    key='hist_bins'
)

# Call the plotly plot 
with st.container():
    plot_plotly_histogram(
        df=df, 
        x_col=histogram_x_col, 
        bins=histogram_bins,
        title=f"Distribution of {histogram_x_col.title()} (Bins: {histogram_bins})"
    )


st.markdown("---")



# ----------------------------------------------------
# Pie chart 
# ----------------------------------------------------
st.subheader("Categorical Distribution - Pie Chart")

# Sidebar control for pie chart 
st.sidebar.subheader("Pie Chart Controls")

# Define columns for pie chart 
PIECHART_COLS = ['decade', 'rating_category', 'activity_level']


available_pie_cols = [col for col in PIECHART_COLS if col in df.columns]

#Selectbox 
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

# Call the plotly plot 
with st.container():
    plot_plotly_pie(
        df=df,
        category_col=pie_category_col,
        title=f"Distribution by {pie_category_col.replace('_', ' ').title()}"
    )


st.markdown("---")

# --------------------------------------
# Bar plot with options 
# -----------------------------------

st.subheader(" Metric Comparison (Count or Average)")

st.sidebar.subheader(" Metric Plot Controls")

METRIC_COLS = ['decade', 'activity_level', 'genres'] 
available_metric_cols = [col for col in METRIC_COLS if col in df.columns]

if not available_metric_cols:
    st.warning("No suitable columns found for Metric Comparison.")
    st.stop()


# Metric Type Selection
metric_type = st.sidebar.radio(
    "Select Metric to Visualize:",
    options=['Total Ratings (Count)', 'Average Rating'],
    key='metric_radio'
)

# Category Selection
metric_category_col = st.sidebar.selectbox(
    "Select Category to Group By:", 
    options=available_metric_cols,
    index=0,
    key='metric_category_select'
)

# Call the plotly plot 
with st.container():
    plot_plotly_bar(
        df=df,
        category_col=metric_category_col,
        metric_type=metric_type,
        title=f"{metric_type} by {metric_category_col.replace('_', ' ').title()}",
        genre_analysis_df=genre_analysis_df
    )

st.markdown("---")




# ----------------------------------------------------
#Stacked Count of Ratings by Activity Level
# ----------------------------------------------------

st.subheader("Ratings by customer activity level")

if not df.empty:
    with st.container():
        plot_stacked_activity_rating_count(
            df=df, 
            title="Total Ratings Count by Activity Level and Rating Category"
        )
else:
    st.warning("Main DataFrame is required for this stacked bar chart.")



st.markdown("---")

# ----------------------------------------------------
# Correlation heatmap, rating and genres 
# ----------------------------------------------------

st.subheader("Feature Correlation Heatmap")

st.info("The heatmap below shows the correlation between the movie rating, and the presence of each genre. Since a movie can have multiple genres, multi-hot encoding is used.")

with st.container():
    plot_genre_rating_heatmap(
        df=df, 
        title="Correlation Matrix: Rating and Genres"
    )

st.markdown("---")


# ----------------------------------------------------
# Movie Ranking by weighted rating 
# ----------------------------------------------------

st.subheader("Title Ranking by weighted rating ")
st.sidebar.subheader("Ranking Plot Controls")


# Data Preparation: 
ranking_df = movies_by_rating.copy()

ranking_df = ranking_df.sort_values(by='weighted_rating', ascending=False)


#  Filter the data to the top n ranked entries
ranking_base = ranking_df.head(20)


# Sidebar 
num_to_display = st.sidebar.slider(
    "Select number of top movies to visualize:",
    min_value=1,
    max_value=20,
    value=10, # Default to showing the top 15
    step=1
)

# Filtering based on slide value 
final_ranking_df = ranking_base.head(num_to_display)

# Call the plotly plot 
with st.container():
    plot_plotly_bar_ranking(
        df=final_ranking_df,
        x_col='weighted_rating',  # X-axis is now the Weighted Rating
        y_col='title', 
        title=f"Top {num_to_display} Titles by Weighted Rating",
        ascending_order=False # Highest rated movie (highest bar) goes to the top
    )


st.markdown("---")


# ------------------------------------
# Animated plot bar 
# -----------------------------------

st.subheader("Animated Rating Evolution of Top 10 Movies")
st.info("Watch the yearly average rating change for the Top 10 highest-rated movies (by Weighted Rating).")
# check  required dataframes 
if not df.empty and not movies_by_rating.empty:
    # call plot 
    with st.container():
        plot_animated_rating_evolution(
            # df_main is the full history of all ratings
            df_main=df, 
            
            # movies_by_rating is the stats DF used to determine the top 10 movies
            movies_by_rating=movies_by_rating
        )
else:
    st.warning("Cannot display animated chart: Both main data (df) and movie statistics (movies_by_rating) are required.")

st.markdown("---")

# ------------------------
# WORDCLOUD 
# -------------


st.title("Word Cloud Visualization of a related article ")

FIXED_ARTICLE_URL = "https://www.theguardian.com/media/2025/aug/28/bland-easy-to-follow-for-fans-of-everything-what-has-the-netflix-algorithm-done-to-our-films"




# Input Widget: this is a read-only input box that shows the article we used 
st.text_input(
    "Source Article URL:", 
    value=FIXED_ARTICLE_URL,
    disabled=True, # Makes the box read-only
    label_visibility="visible"
)

st.header("Generated Word Cloud")


try:
    #  Call the function using the FIXED_ARTICLE_URL
    with st.spinner('Scraping and generating Word Cloud...'):
        figure = load_wordcloud_figure(FIXED_ARTICLE_URL)
    
    #  Display the result
    if figure:
        st.pyplot(figure)
        plt.close(figure)
        
    else:
        # Fallback for scraping failure
        st.error("Error: Could not find article content or generate the figure for the fixed URL.")

except Exception as e:
    st.error(f"An unexpected error occurred during processing: {e}")


st.markdown("---")