# Exploratory Data Analysis of Airbnb Data

by: Ahmed A. Youssef

## Data Source

The data was obtained from [insideairbnb website](http://insideairbnb.com/get-the-data.html)

## Libraries Dependency
- re
- itertools
- numpy
- pandas
- seaborn
- matplotli
- PIL
- wordcloud
- tabulate
- sqlite3

## Project Motivation

EDA analysis for Airbnb data of two USA cities; Boston and Seattle.

Four business questions were analyzed:
- _host description and reviewers comments_: 
    - How do hosts like to describe their listings? 
    - How do visitors like to express their stay experience?
- _Identity Verifications_:  
    - How hosts verify their identity?
- _Customer Acquisition_:
    - What is the difference in the rate of customer acquisition between Boston and Seattle?
- _Relationship between price, beds, bedrooms and baths_:
    - Is there a relationship between the price and the number of beds or bedrooms or baths?

## Project Files

- ```read_data```: a module for reading the original Airbnb data.
- ```clean_data```: an ETL module that will; 1) extract the data, 2) preprocess it to the correct data type, 3) store it to SQLite or csv files.
- ```data_visualization```: a module for creating visualizations for; 1) the missing data per row or column and 2) word cloud of the most frequently used words for a selected column ["summary", "comments"]. 

## Analysis Workflow

The original data of each city are saved in separate folders; ```data files\cityname-airbnb-opendata```. The data was preprocessed through the following steps:

- Dropping Columns with redundant data.
- Dropping columns containing personal information on hosts or reviews like first name, last name...etc. 
- Removing rows or columns with NANs exceeding a certain threshold.
- Transforming columns to the correct format; date columns are parsed as date time and monetary columns are parsed as numeric.
- Imputing missing values for numerical and categorical features.

For more information on how each step of the preprocessing pipeline was performed, please check the jupyter notebook [Airbnb Notebook Analysis.ipynb]

After cleaning both datasets, the clean data was transferred to the following formats:
- SQLite database: The database has three tables
    - listings: contains data on listings or rental units available on Airbnb for each host.
    - amenities: contains data on the amenities offered by each host for their rental units.
    - verifications: contains data on the verification tools used by each host to verify their identity.

Each city has a separate SQLite database which contains the clean and transformed data with the following name: cityname.db

- csv format: The clean data was extracted to the following csv files:
    - listings.csv: contains data on listings or rental units available on Airbnb for each host.
    - amenties.csv: contains data on the amenities offered by each host for their rental units.
    - reviews.csv: contains data on the reviews made by visitors on each rental unit.
    - verifications.csv: contains data on the verification tools used by each host to verify their identity.
    - wc_reviews: contains the bag of words for reviews made by visitors.
    - wc_summary: contains the bag of words for summaries written by hosts to describe their units.

Each city has a new folder [cityname] which contains all the newly created csv files.

These two formats should allow anyone to load the clean data in the way they prefer.

After that, I have performed EDA analysis. I have done some exploration inside the notebook but the final EDA analysis was compiled as a tableau story. A tableau story was created to answer each one of the business questions highlighted above. The tableau story is accessed through the following [link](https://public.tableau.com/views/AirbnbRentalsOverviewofBostonandSeattle/Airbnb?:embed=y&:display_count=yes&:origin=viz_share_link).


## Results

- **For Verifications tools: reviews, phone and emails are the top three tools in both cities.**
<img src="img\Top verification tools.png"
     alt="Top verification tools used by hosts"
     height="60%" width="60%"
     style="margin: 10px;" />
<br>
- **For Amenities: wireless internet and heating are the top two amentities offered by hosts in both cities.**
<br>
<img src="img\Top Amenities.png"
     alt="Top Amenities offered by hosts"
     height="60%" width="60%"
     style="margin: 10px;" />
<br>
- **Customer Acquisition: there was a spike in the number of new customers starting from April 2013 in both cities. However, Airbnb enjoys a customer base in Seattle larger than Boston.**
<br>
<img src="img\Customer Acquisition.png"
     alt="Customer Acquisition Patterns in Boston and Seattle"
     height="60%" width="60%"
     style="margin: 10px;" />
<br>
**Seattle**
- **Reviewers expressed their stay experience using keywords that focus on; location, amenities and host hospitality.**
<br>
<img src="img\Seattle Reviews Word Cloud.png"
     alt="Most frequent keywords used by visitors in Seattle"
    height="60%" width="60%"
     style="margin: 10px;" />
<br>
- **Hosts focused on location proximity to downtown, amenities, unit size and close tourist attractions.**
<br> 
<img src="img\Seattle Summary Word Cloud.png"
     alt="Most frequent keywords used by hosts in Seattle"
     height="60%" width="60%"
     style="margin: 10px;" />
<br>
**Boston**
- **Reviewers from Seattle expressed their stay experience using keywords that is similar to reviewers from Seattle.** 
<br>
<img src="img\Boston Reviews Word Cloud.png"
     alt="Most frequent keywords used by visitors in Boston"
     height="60%" width="60%"
     style="margin: 10px;" />
<br>
- **Hosts from boston focused on; location proximity to downtown, amenities, unit size and close tourist attractions.**   
<br>
<img src="img\Boston Summary Word Cloud.png"
     alt="Most frequent keywords used by hosts in Boston"
     height="60%" width="60%"
     style="margin: 10px;" />
<br>