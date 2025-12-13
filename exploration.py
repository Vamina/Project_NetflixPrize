import streamlit as st
from data_loader import load_data, get_df
from plotting_utils import plot_seaborn_histogram, plot_plotly_pie, plot_bar

st.set_page_config(
    page_title="Dataset Exploration",
    page_icon="📊",
    layout="wide"
)

# --- Data Loading ---
data_store = load_data()
df = get_df(data_store, 'main_df')
movies_by_rating = get_df(data_store, 'movies_by_rating')

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


st.header(" Metric Comparison (Count or Average)")

st.sidebar.header(" Metric Plot Controls")

METRIC_COLS = ['decade', 'activity_level', 'genre'] 
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
        title=f"{metric_type} by {metric_category_col.replace('_', ' ').title()}"
    )