import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def plot_grouped_bar_metrics(df, category_col, title):
    """
    Generates a grouped bar chart showing both count and average rating 
    for a selected category.
    """
    
    # 1. Data Aggregation: Calculate Count and Average Rating
    metric_df = df.groupby(category_col).agg(
        rating_count=('rating', 'count'),
        rating_avg=('rating', 'mean')
    ).reset_index()

    if df.empty:
        st.warning("Cannot generate plot: The DataFrame is empty due to applied filters.")
        return # Stop execution if empty
    

    # Sort the results by rating count (volume) in descending order
    metric_df = metric_df.sort_values(by='rating_count', ascending=False)
    
    # Optional: Limit to top N categories for cleaner viewing (e.g., top 15)
    metric_df = metric_df.head(15)

    # 2. Create the Dual-Metric Bar Chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar 1: Rating Count (Volume)
    fig.add_trace(
        go.Bar(
            x=metric_df[category_col], 
            y=metric_df['rating_count'], 
            name='Total Ratings (Count)', 
            marker_color='orange'
        ),
        secondary_y=False,
    )


    # Line/Point 2: Average Rating
    fig.add_trace(
        go.Scatter(
            x=metric_df[category_col], 
            y=metric_df['rating_avg'], 
            name='Average Rating', 
            mode='lines+markers', 
            marker=dict(size=10, color='red'),
            line=dict(dash='dot', color='red')
        ),
        secondary_y=True,
    )




import plotly.express as px
import streamlit as st

def plot_bar(df, category_col, metric_type, title):
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
    """
    Generates a vertical Plotly bar chart, ideal for counts/volumes per category (e.g., decades).
    """
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
        title_x=0.5,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title(),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)



def plot_animated_rating_evolution(df_main, top_movies_df):
    """
    Generates an animated bar chart showing the yearly average rating evolution 
    for a selected group of movies (e.g., the top 10).
    """
    
    #define the movies that have higher rating count than the threshold 
    eligible_movies = movie_stats[movie_stats['rating_count'] >= m].copy()

# 2. Sort by the Weighted Rating (WR) and take the first 10 movies 
    top_movies = eligible_movies.sort_values(by='weighted_rating', ascending=False).head(10)    
    popular_movie_ids = top_movies_df['movie_id'].tolist() 
    df_top_movies = df_main[df_main['movie_id'].isin(popular_movie_ids)].copy()

    # Ensure rating_year is present
    # We must handle the case where 'date' might be a string if not converted in data_loader.
    if 'date' in df_top_movies.columns:
        df_top_movies['date'] = pd.to_datetime(df_top_movies['date'])
        df_top_movies['rating_year'] = df_top_movies['date'].dt.year 
    else:
        st.warning("Cannot create animated chart: 'date' column missing or invalid.")
        return None

    # 2. Aggregate Data by Movie and Year (Average Rating Evolution)
    movie_ratings_by_year = df_top_movies.groupby(['title', 'rating_year']).agg(
        yearly_count=('rating', 'count'), 
        yearly_avg_rating=('rating', 'mean') 
    ).reset_index()

    # 3. Fill Missing Years (Crucial for smooth animation)
    all_years_titles = pd.MultiIndex.from_product(
        [movie_ratings_by_year['title'].unique(), movie_ratings_by_year['rating_year'].unique()],
        names=['title', 'rating_year']
    ).to_frame(index=False)

    plot_data = pd.merge( # Renamed to plot_data for consistency with your snippet
        all_years_titles,
        movie_ratings_by_year,
        on=['title', 'rating_year'],
        how='left'
    ).fillna(
        {'yearly_count': 0, 'yearly_avg_rating': None} # Set avg_rating to None/NaN so bars disappear correctly
    )

    # Get the list of unique years in numerical order to set the animation order
    year_order = sorted(plot_data['rating_year'].unique())

    # --- Plotly Figure Creation ---
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

    # --- Apply Layout Fixes (Crucial for Chronological Animation) ---
    fig.update_layout(
        xaxis={'categoryorder': 'total descending', 'showticklabels': False}, 
        height=600,
        width=1000,
        
        # Specify the chronological order for the animation frame using sliders
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