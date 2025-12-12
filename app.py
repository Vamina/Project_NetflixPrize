import streamlit as st



def plot_bar(df, col_x, col_y, title=None):
    plt.figure()
    plt.bar(df[col_x], df[col_y])
    
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    
    if title:
        plt.title(title)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


plot_bar(df_view_decades, col_x="decade", col_y="rating", title="Rating per decade (movie release)")




plt.figure(figsize=(8, 5))
sns.histplot(
    data=df,
    x='rating',
    discrete= False,
    bins=5,           # Use the custom bins
    kde=False,           # Remove the misleading continuous curve
    stat='count',        # Show the raw count of ratings in each bin
    color='skyblue',
    edgecolor='black',
    alpha=0.7
)





# df grouped by customers - rating volume and rating average per customer 

customer_stats = df.groupby('customer_id').agg(
    num_ratings=('rating', 'count'),
    avg_rating=('rating', 'mean')
)


#minimum and maximum of ratings to consider for the analysis 
min_ratings = 1
max_ratings = 60

#  keep only customers who meet BOTH criteria: (>= 5) AND (<= 60)
customer_stats_doubly_filtered = customer_stats[
    (customer_stats['num_ratings'] >= min_ratings) & 
    (customer_stats['num_ratings'] <= max_ratings)
].copy()

plt.figure(figsize=(10, 6))

# Plot the scatterplot with a straight (linear) regression line
sns.regplot(
    data=customer_stats_doubly_filtered,
    x='num_ratings',
    y='avg_rating',
    logx = True,
    #order=1, # <--- Forces a straight linear line
    scatter_kws={'alpha':0.2, 's':15}, # Use higher transparency for better visibility
    line_kws={'color':'darkblue', 'linewidth': 3}
)







plt.title(f'Linear Fit: Rating Volume vs. Average Rating')
plt.xlabel('Number of Ratings Given by Customer')
plt.ylabel('Average Rating Given by Customer')

plt.xlim(min_ratings - 1, max_ratings + 1)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()



# Create a filtered DataFrame
customer_stats_filtered_60 = customer_stats[
    customer_stats['num_ratings'] <= custom_cutoff
].copy()


sns.histplot(
    data=customer_stats_filtered_60,
    x='num_ratings',
    bins=10,             # Use many bins to define the shape well
    kde=False, 
    log_scale=True,         # Keep kde=False as you requested
    color='darkorange',
    edgecolor='black',
    alpha=0.7
)




sns.barplot(
    # The X-axis is the calculated Weighted Rating
    x='weighted_rating',
    # The Y-axis is the Movie Title
    y='title',
    data=top_movies,
    palette='viridis' # A nice color palette for ranking
)



plt.title(f'Top 10 Best Rated Movies (Min Ratings: {m:.0f})', fontsize=16)
plt.xlabel('Weighted Rating Score (WR)', fontsize=12)
plt.ylabel('Movie Title', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.6)
plt.show()




# --- Plot Generation ---
plt.figure(figsize=(10, 6))

sns.barplot(
    # X-axis: The categorical variable (Decade)
    x='decade',
    # Y-axis: The numerical score (Weighted Rating)
    y='weighted_rating',
    data=plot_data,
    palette='viridis' 
)

# Add titles and formatting
plt.title('Decade Quality Ranked by Weighted Rating (WR)', fontsize=16)
plt.xlabel('Movie Release Decade', fontsize=12)
plt.ylabel('Weighted Rating Score (WR)', fontsize=12)

# Rotate x-labels to prevent overlap and make them readable
plt.xticks(rotation=45, ha='right') 
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.show()




plt.figure(figsize=(10, 6))

def barplot(data : pd.DataFrame):
  sns.barplot(
    # X-axis: Decade
    x='decade',
    # Y-axis: Total volume (Count of Ratings)
    y='rating_count',
    data=decade_stats,
    palette='rocket' 
  )

# Add titles and formatting
  plt.title('Number of Ratings Per {x}', fontsize=16)
  plt.xlabel('Movie Release Decade', fontsize=12)
  plt.ylabel('Total Number of Ratings', fontsize=12)
  plt.xticks(rotation=45, ha='right') 
  plt.grid(axis='y', linestyle='--', alpha=0.6)
  plt.show()





  def create_interactive_pie_chart(
    data: pd.DataFrame, 
    category_col: str,
    title : str
):
    """
    Generates an interactive pie chart using Plotly Express with custom styling 
    and pastel colors based on a chosen categorical column.

    Args:
        data (pd.DataFrame): The DataFrame containing the category column.
        category_col (str): The column name to use for slicing the pie chart.
    """
    
    # 1. Prepare Data: Calculate the counts for the chosen category
    # This ensures each slice represents a count of the variable
    category_counts = data[category_col].value_counts().reset_index()
    category_counts.columns = [category_col, 'Count']
    
    # 2. Create the initial Plotly Pie Chart (using the 'pastel' template)
    fig = px.pie(
        category_counts,
        names=category_col, 
        values='Count',
        title=title,
        color_discrete_sequence=px.colors.sequential.Agsunset, # A palette with pastel-like, warm colors
        template='plotly_white'
    )
    
    # 3. Apply Custom Styling (based on your requirements)
    
    # Define a custom 'pull' array. We will dynamically assign a pull 
    # value (e.g., 0.1) to the largest slice for emphasis.
    num_slices = len(category_counts)
    
    # Find the index of the largest slice
    largest_index = category_counts['Count'].idxmax()
    
    # Create the pull array: 0.1 for the largest slice, 0 for all others
    pull_array = [0.1 if i == largest_index else 0 for i in range(num_slices)]
    
    
    fig.update_traces(
        # Hover information: show label (category) and percent
        hoverinfo='label+percent+value', 
        
        # Text displayed on the slice: show label and percent
        textinfo='label+percent', 
        textfont_size=16, # Slightly smaller text size for better fit
        
        # Explode the largest slice
        pull=pull_array, 
        
        # Line/Border styling
        marker=dict(line=dict(color='black', width=1.5))
    )


    # --- Adjust Figure Size Here ---
    fig.update_layout(
        height=700, # Set the height of the plot (in pixels)
        width=750,  # Set the width of the plot (in pixels)
        font=dict(size=14) # Adjust overall font size
    )
    
    # 4. Show the figure
    fig.show()




create_interactive_pie_chart(df, 'decade', 'Distribution of movies per decade'
)






# 1. Extract IDs and Filter Main Data
popular_movie_ids = top_movies['movie_id'].tolist() 
df_top_movies = df[df['movie_id'].isin(popular_movie_ids)].copy()

# Ensure rating_year is present and data is sorted
df_top_movies['date'] = pd.to_datetime(df_top_movies['date'])
df_top_movies['rating_year'] = df_top_movies['date'].dt.year 

# 2. Aggregate Data by Movie and Year (Average Rating Evolution)
movie_ratings_by_year = df_top_movies.groupby(['title', 'rating_year']).agg(
    yearly_count=('rating', 'count'), 
    yearly_avg_rating=('rating', 'mean') 
).reset_index()

# 3. Fill Missing Years (Crucial for smooth animation—a movie should not disappear)
all_years_titles = pd.MultiIndex.from_product(
    [movie_ratings_by_year['title'].unique(), movie_ratings_by_year['rating_year'].unique()],
    names=['title', 'rating_year']
).to_frame(index=False)

# Merge back: Note that we leave 'yearly_avg_rating' as NaN where data is missing
# (This causes the bar to disappear, which is correct for raw yearly average)
movie_ratings_by_year_filled = pd.merge(
    all_years_titles,
    movie_ratings_by_year,
    on=['title', 'rating_year'],
    how='left'
).fillna(
    {'yearly_count': 0} # We still fill the count with 0, even if not plotting it
)


# Get the list of unique years in numerical order to set the animation order
year_order = sorted(plot_data['rating_year'].unique())

fig = px.bar(
    plot_data,
    x='title',
    y='yearly_avg_rating', 
    color='title',
    animation_frame="rating_year",          
    animation_group="title",                
    range_y=[1, 5.2], 
    labels={'yearly_avg_rating': 'Average Rating in Year', 'title': 'Movie Title'},
    title='Evolution of Average Rating for Top 10 Movies by Year'
)

# 1. FIX: Force the animation frames to follow the year_order list
fig.update_layout(
    xaxis={'categoryorder': 'total descending', 'showticklabels': False}, 
    height=600,
    width=1000,
    
    # 2. ADD: Specify the chronological order for the animation frame
    # We convert the list of numeric years to strings because animation_frame values are often treated as strings.
    # This guarantees the animation sequence is 1990, 1991, 1992, etc.
    updatemenus=[
        {
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}]
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }
    ],
    # CRITICAL: This line ensures the sequence is chronological
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

fig.show()