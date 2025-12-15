Data management project 

Daria D'Alessandro 
Paulo Sergio Garcia Rodriguez 



For this projet we used the Netflix Prize database, which was too massive to use as a whole, so we took a random sample of 500.000 lines

Link to the entire netflix dataset: 
https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data/data?select=combined_data_4.txt

Link to the genre database for merging:
 https://github.com/tommasocarraro/netflix-prize-with-genres/blob/master/netflix_genres.csv

Link to the sample used for the analysis: 
https://github.com/Vamina/Project_NetflixPrize/blob/main/netflix_sampled_500k_proportional.csv


List of files in the folder: 
- netflix_data_manag.ipynb - data management - variable creation - final dataframe creation 
- sampling.py - data sampling 
- neflix_sampled_500k_proportional.csv  - sampled rating data 
- netflix_genres.csv - movie genres file
- movie_titles.csv - movie titles file 
- for the streamlit app : 
            - app.py - MAIN APP 
            - plotting_utils.py - plotting functions 
            - nexflix_article.py - scraping and wordcloud creation 
            - data_loader.py - load data 
r