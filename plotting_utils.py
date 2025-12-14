import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from article_netflix import get_wordcloud_figure_from_url 

# --- Matplotlib/Seaborn Functions ---

def plot_seaborn_histogram(df, x_col, bins, title):
    

    a4_dims = (6,4)  
    fig, ax = plt.subplots(figsize=a4_dims)

    # 2. Seaborn Plotting Logic
    sns.histplot(
        data=df,
        x=x_col,
        discrete=False,
        bins=bins,
        lw=2,
        kde=False,
        stat='count',
        color='orange',
        edgecolor='red',
        alpha=0.7,
        ax=ax # IMPORTANT: Pass the axis object to seaborn
    )
    
    # 3. Formatting
    ax.set_title(title, fontsize = 10)
    ax.set_xlabel(x_col.replace('_', ' ').title(), fontsize = 10)
    ax.set_ylabel('Count', fontsize = 10)
    plt.tight_layout()
    
    
    # 4. Streamlit Display
    st.pyplot(fig, use_container_width=True)
    plt.close(fig) # Close the figure to free memory



#PIE CHARTS 
def plot_plotly_pie(df, category_col, title):

    # 1. Calculate counts
    category_counts = df[category_col].value_counts().reset_index()
    category_counts.columns = [category_col, 'Count']

    
    # 2. RE-APPLY SORTING METADATA and SORT DATAFRAME
    original_col = df[category_col] 
    
    if pd.api.types.is_categorical_dtype(original_col) and original_col.cat.ordered:
        
        custom_order = list(original_col.cat.categories)
        
        category_counts[category_col] = pd.Categorical(
            category_counts[category_col], 
            categories=custom_order, 
            ordered=True
        )
        
        # Sort the rows by the custom order for plotting
        category_counts = category_counts.sort_values(by=category_col)

    
    # 3. Create the Plotly Figure 
    fig = px.pie(
        category_counts,
        names=category_col,
        values='Count',
        title=title,
        color_discrete_sequence=px.colors.sequential.Agsunset,
        template='plotly_white'
    )
    
    # 4. Apply Layout Updates (Legend and Size)
    final_layout = {
        'height': 650, 
        'uniformtext_minsize': 12, 
        'uniformtext_mode': 'hide',
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    }

    fig.update_layout(final_layout)
        
    # 5. Apply Trace Updates (CRITICAL FIX HERE)
    fig.update_traces(
        textfont_size=14, 
        hoverinfo='label+percent+value', 
        textinfo='percent', 
        marker=dict(line=dict(color='black', width=1.5)),
        # THIS FORCES PLOTLY TO USE THE DATA ORDER, NOT FREQUENCY/ALPHABETICAL
        sort=False 
    )
    
    st.plotly_chart(fig, use_container_width=True)



# BAR PLOTS 







def plot_bar(df, category_col, metric_type, title, genre_analysis_df=None):
    """
    Generates a single bar chart for either Count or Average Rating 
    for a selected category.
    """
    
    # Define column names based on the metric type selected by the user
    if metric_type == 'Average Rating':
        metric_col_name = 'rating_avg'
        y_axis_label = 'Average Rating'
    else: # Default is 'Total Ratings (Count)'
        metric_col_name = 'rating_count'
        y_axis_label = 'Total Ratings (Count)'

    # --------------------------------------------------
    if category_col == 'genres':
        
        if genre_analysis_df is None:
            # Fallback for safety, though it shouldn't happen if coded correctly
            st.error("Genre analysis data is missing!")
            return
            
        # Use the already calculated DataFrame, just select and rename columns
        metric_df = genre_analysis_df.copy()


    else: 
    # 1. Data Aggregation: Calculate Count and Average Rating
        metric_df = df.groupby(category_col).agg(
         rating_count=('rating', 'count'),
            rating_avg=('rating', 'mean')
        ).reset_index()

    # Sort the results by the selected metric (descending)
    metric_df = metric_df.sort_values(by=metric_col_name, ascending=False)
    
    # Limit to top N categories for cleaner viewing
    N_LIMIT = 20  
    metric_df = metric_df.head(N_LIMIT)
    
    # Ensure the category column is a string for plotting stability
    metric_df[category_col] = metric_df[category_col].astype(str)

    
    # 2. Create the Plotly Bar Chart using Plotly Express (simpler API)
    fig = px.bar(
        metric_df,
        x=category_col, 
        y=metric_col_name,
        title=title,
        color=metric_col_name, # Use the metric for coloring depth
        color_continuous_scale=px.colors.sequential.Sunsetdark,
        template='plotly_white'
    )

    # 3. Formatting and Layout
    fig.update_layout(
        height=500,
        xaxis={'categoryorder': 'total descending', 'title': category_col.replace('_', ' ').title()},
        yaxis={'title': y_axis_label}
    )
    
    # Optional: Set the Y-axis range for Average Rating to be fixed (1-5)
    if metric_type == 'Average Rating':
        fig.update_yaxes(range=[1, 5])
        
    # 4. Streamlit Display
    st.plotly_chart(fig, use_container_width=True)






def plot_plotly_vertical_bar(df, x_col, y_col, title, order=None):
  
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        orientation='v', # Explicitly vertical (default, but good for clarity)
        title=title,
        color=y_col, 
        color_continuous_scale=px.colors.sequential.Rocket,
    )
    
    # Ensure X-axis (Decades) is ordered chronologically
    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': order if order else df[x_col].unique()},
        title_x=0.5,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_plotly_bar_ranking(df, x_col, y_col, title, ascending_order=True):

    fig = px.bar(
        df,
        x=x_col,
        y=y_col, 
        orientation='h',  # <--- THIS MAKES IT HORIZONTAL
        title=title,
        color=x_col, # Color bars based on the numerical value
        color_continuous_scale=px.colors.sequential.Viridis,
    )
    
    # Invert the axis if descending order is desired for visual ranking (highest bar at top)
    if not ascending_order:
        # 'total ascending' means the smallest value is at the bottom, 
        # which puts the highest bar (highest rank) at the top of the chart.
        fig.update_layout(
            yaxis={'categoryorder':'total ascending'}
        )
    else:
        fig.update_layout(
            yaxis={'categoryorder':'total descending'}
        )

    fig.update_layout(
        title={
            'text': title,    
            'x': 0.5,          
            'font': dict(
                size=18,       
            )
        },
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        height=700,
        yaxis=dict( tickfont=dict(size=16) )
    )


    st.plotly_chart(fig, use_container_width=True)


# HEATMAP 

def plot_genre_rating_heatmap(df, title):
    """
    Generates a full correlation matrix heatmap showing the relationship 
    between 'rating' and all multi-hot encoded genres ONLY.
    
    Args:
        df (pd.DataFrame): The main DataFrame containing 'rating' and 'genres'.
        title (str): The title for the heatmap.
    """
    
    # Check for required columns
    required_cols = ['rating', 'genres']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Cannot create Heatmap: Missing one or more required columns ({required_cols}).")
        return
        
    # 1. Prepare Data (Multi-hot Encoding)
    # ------------------------------------------------------------------
    # STRICTLY select only 'rating' and 'genres'
    df_encoded = df[required_cols].copy().dropna(subset=required_cols)
    
    if df_encoded.empty:
        st.warning("No data remains for Heatmap after dropping rows with missing ratings/genres.")
        return
        
    df_encoded['genres'] = df_encoded['genres'].str.split("|")

    # Explode and create multi-hot encoded genre columns
    df_genre_dummies = (
        df_encoded["genres"]
        .explode()
        .str.strip() 
        .str.get_dummies()
        .groupby(level=0)
        .sum()
    )

    # Join the multi-hot encoded genre columns and drop the original 'genres' column
    # The resulting DataFrame contains 'rating' and all the individual genre columns
    df_final_matrix_data = df_encoded.drop(columns='genres').join(df_genre_dummies)
    
    # 2. Correlation Calculation
    # ------------------------------------------------------------------
    
    # Select final numeric columns (includes 'rating' and all new genre columns)
    df_corr_data = df_final_matrix_data.select_dtypes(include=[np.number])
    
    # Calculate the correlation matrix
    df_corr_matrix = df_corr_data.corr()

    # 3. Plotting (Using Matplotlib and Seaborn)
    # ------------------------------------------------------------------
    
    # Capture the figure object
    fig, ax = plt.subplots(figsize=(14, 8)) 
    
    sns.heatmap(df_corr_matrix,
                cmap="coolwarm",
                annot=False, 
                fmt=".2f",
                vmin=-1,
                vmax=1,
                ax=ax) 

    ax.set_title(title, fontsize=16)
    ax.set_xlabel("Features", fontsize=12)
    ax.set_ylabel("Features", fontsize=12)
    plt.tight_layout()
    
    # 4. Display in Streamlit
    st.pyplot(fig)
    plt.close(fig)







def plot_animated_rating_evolution(df_main, movies_by_rating):

    
    
    N_TOP = 10 
    
    # Check for required columns before proceeding
    if 'weighted_rating' not in movies_by_rating.columns or 'movie_id' not in movies_by_rating.columns:
        st.error("Cannot create animated chart: 'weighted_rating' or 'movie_id' missing from movie statistics.")
        return None
        
    # Sort by Weighted Rating (WR) and take the top N
    df_top_movies_stats = (
        movies_by_rating
        .sort_values(by='weighted_rating', ascending=False)
        .head(N_TOP)
    )
    
    popular_movie_ids = df_top_movies_stats['movie_id'].tolist()
    
    # --- 2. Filter the Main DataFrame for the history of these movies ---
    df_history = df_main[df_main['movie_id'].isin(popular_movie_ids)].copy()

    # --- 3. Ensure Date Information is Usable ---
    
    # We use 'rating_date' as established in your data_loader for consistency
    if 'rating_date' in df_history.columns:
        # Since 'rating_date' should already be datetime from load_data, 
        # we only need to extract the year.
        df_history['rating_year'] = df_history['rating_date'].dt.year 
    else:
        st.warning("Cannot create animated chart: 'rating_date' column missing or invalid.")
        return None

    # --- 4. Aggregate Data by Movie and Year (Average Rating Evolution) ---
    movie_ratings_by_year = df_history.groupby(['title', 'rating_year']).agg(
        yearly_count=('rating', 'count'), 
        yearly_avg_rating=('rating', 'mean') 
    ).reset_index()

    # --- 5. Fill Missing Years (Crucial for smooth animation) ---
    # Creates a full timeline for every movie to avoid jerky animation
    all_years_titles = pd.MultiIndex.from_product(
        [movie_ratings_by_year['title'].unique(), movie_ratings_by_year['rating_year'].unique()],
        names=['title', 'rating_year']
    ).to_frame(index=False)

    plot_data = pd.merge(
        all_years_titles,
        movie_ratings_by_year,
        on=['title', 'rating_year'],
        how='left'
    )

    # Get the list of unique years in numerical order to set the animation order
    year_order = sorted(plot_data['rating_year'].unique())

    # --- 6. Plotly Figure Creation ---
    fig = px.bar(
        plot_data,
        x='title',
        y='yearly_avg_rating', 
        color='title',
        animation_frame="rating_year", 
        animation_group="title", 
        range_y=[1, 5.2], 
        labels={'yearly_avg_rating': 'Average Rating in Year', 'title': 'Movie Title'},
        title='Evolution of Average Rating for Top Movies by Year'
    )

    # --- 7. Apply Layout Fixes (Crucial for Chronological Animation) ---
    fig.update_layout(
        xaxis={'categoryorder': 'total descending', 'showticklabels': False}, 
        height=600,
        width=1000,
        sliders=[
            {
                'steps': [
                    {
                        'args': [[year], {'frame': {'duration': 500, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                        'label': str(year),
                        'method': 'animate'
                    } for year in year_order
                ],
                'transition': {'duration': 0},
                'x': 0.1,
                'len': 0.9,
                'y': 0,
                'pad': {'b': 10, 't': 50},
                'active': 0
            }
        ]
    )
    
    # Display the chart via Streamlit
    st.plotly_chart(fig, use_container_width=True)




def plot_stacked_activity_rating_count(df, title):

    # 1. Check for required columns
    required_cols = ['activity_level', 'rating_category']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Cannot create Stacked Bar Chart: Missing one or more required columns ({required_cols}).")
        return

    # 2. Aggregate Data
    # Calculate the count of ratings for each combination of Activity Level and Rating Category
    plot_data = (
        df.groupby(required_cols)
        .size() # Counts the number of rows (ratings) in each group
        .reset_index(name='rating_count')
    )
    
    activity_order = ['Low', 'Medium', 'High']
    category_order = ['Low', 'Neutral', 'High']
    
    # 3. Create the Plotly Stacked Bar Chart
    fig = px.bar(
        plot_data,
        x='activity_level',
        y='rating_count',
        color='rating_category',
        title=title,
        
        # Ensure the categories are sorted correctly (Low, Medium, High)
        category_orders={
            'activity_level': activity_order,
            'rating_category': category_order
        },
        
        # Set the color mapping explicitly to ensure the stack order is intuitive
        color_discrete_map={
            'Low': '#EF553B',      # Reddish for Low Rating Category
            'Neutral': '#FECB52',  # Yellowish for Neutral Rating Category
            'High': '#00CC96'     # Greenish for High Rating Category
        },
        labels={
            'activity_level': 'User Activity Level',
            'rating_count': 'Total Count of Ratings',
            'rating_category': 'Rating Category'
        }
    )
    
    # 4. Final Formatting
    fig.update_layout(
        xaxis_title="User Activity Level",
        yaxis_title="Total Count of Ratings",
        legend_title="Rating Category"
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)




#WORDCLOUD 

@st.cache_data
def load_wordcloud_figure(url):
    return get_wordcloud_figure_from_url(url)