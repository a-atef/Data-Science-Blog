import numpy as np
import pandas as pd
import tabulate
import re
from itertools import chain
import sqlite3
import os

# return dataframe without any rows or columns with missing values > threshold
def drop_missing(dataframe, row=False, threshold=0.2):
    """Drop columns or rows with missing values exceeding the threshold.
    
        Args:
            dataframe (Dataframe): a dataframe object 
            threshold (float): a value which will be used to drop columns or rows with NANs
            row (bool): if True, it will returns a dataframe without rows exceeding the threshold. 
            If False, it will return a dataframe without columns exceeding the threshold.
            
        Returns:
            Dataframe: a new dataframe without rows or columns with NANs exceeding the threshold 
        
    """
    if row:
        sum_axis = 1
        drop_axis = 0
        n = dataframe.shape[1]
    else:
        sum_axis = 0
        drop_axis = 1
        n = dataframe.shape[0]

    to_drop = dataframe.isnull().sum(axis=sum_axis) / n
    to_drop = to_drop[to_drop > threshold].index.tolist()
    return dataframe.drop(to_drop, axis=drop_axis)


# print a summary for the categorical and numerical features
def print_column_status(dataframe):
    """Print a nice formated table of each column name and its number of nulls.
    
        Args:
            dataframe (Dataframe): a dataframe object 
            
        Returns:
            None 
        
    """

    def column_status(dataframe, column_type):
        """Print a nice formated table for each type of columns and its number of nulls.
    
        Args:
            dataframe (Dataframe): a dataframe object 
            column_type (string): to return table for numeric columns use number. For other types, use object.
            
        Returns:
            None 
        
        """

        columns = dataframe.select_dtypes(include=[column_type]).isnull().sum(axis=0)
        columns = columns[columns > 0].sort_values(ascending=False)
        table = zip(columns.index.tolist(), columns.tolist())
        print(
            tabulate.tabulate(
                table,
                ["Column Name", "Number of Nulls"],
                "fancy_grid",
                numalign="center",
            )
        )

    # print status of numerical columns
    print("Numerical Columns status:\n")
    column_status(dataframe, "number")

    # print status of object columns
    print("\nCategroical Columns status:\n")
    column_status(dataframe, "object")


def money_to_numeric(series):
    """Return a monetary pandas series.
    
        Args:
            series (Series): a series object 
            
        Returns:
            Series: Clean numeric pandas series 
        
    """

    return series.apply(lambda x: x[1:].replace(",", ""))


def percentage_to_numeric(series):
    """Remove any laterals and return a numeric pandas data series.
    
        Args:
            series (Series): a series object 
            
        Returns:
            Series: Clean numeric pandas series 
        
    """

    return series.str.replace("%", "")


def columns_missing_list(dataframe, column_type):
    """Return a list of column names which include NANS.
    
        Args:
            dataframe (Dataframe): a dataframe object
            column_type (string): number or object
            
        Returns:
            list: list of column names which include NANs 
        
    """

    columns = dataframe.select_dtypes(include=[column_type]).isnull().sum(axis=0)
    columns = columns[columns > 0]
    return columns.index.tolist()


def handle_numeric(dataframe, method="median"):
    """Impute missing values in numeric columns using median or mean.
    
        Args:
            dataframe (Dataframe): a dataframe object
            method (string): median or mean
            
        Returns:
            Dataframe: return a Dataframe object where missing numerical fields are imputed   
        
    """

    if method == "median":
        func = np.median
    else:
        func = np.mean

    columns = columns_missing_list(dataframe, column_type="number")

    for column in columns:
        dataframe[column] = dataframe[column].fillna(func(dataframe[column].dropna()))

    return dataframe


def search_similar_zip(dataframe, column, zipcode):
    """Lookup the value for a missing record by searching for similar records in the dataframe with the same zipcode.
    
        Args:
            dataframe (Dataframe): a dataframe object
            column (string): column name
            zipcode (string): zipcode for the missing record 
            
        Returns:
            object: imputed value for the missing record  
    
    """

    try:
        value = (
            dataframe[column][dataframe["zipcode"] == zipcode].value_counts().index[0]
        )
        return value
    except (IndexError):
        return None


def get_mode_by_zip(dataframe, column):
    """Impute the missing values in a column using the mode. 
       The function group records with similar zipcode and find the mode for each group and use it impute 
       any missing values within that group.
    
        Args:
            dataframe (Dataframe): a dataframe object
            column (string): column name
            
        Returns:
            Dataframe: a clean Dataframe with imputed values for each categorical column 
        
    """

    # handle missing market
    for i, row in dataframe[dataframe[column].isna()][[column, "zipcode"]].iterrows():
        dataframe.loc[i, column] = search_similar_zip(dataframe, column, row[1])

    return dataframe


def get_mode(dataframe, column):
    """Impute the missing values in a column using the mode.
    
        Args:
            dataframe (Dataframe): a dataframe object
            column (string): column name
            
        Returns:
            Dataframe: a clean Dataframe with imputed values for each categorical column 
        
    """

    return dataframe[column].fillna(dataframe[column].value_counts()[0])


def handle_categorical(dataframe):
    """Impute missing values in the Categorical columns.
    
        Args:
            dataframe (Dataframe): a dataframe object
            
        Returns:
            Dataframe: a clean Dataframe with imputed values for each categorical column  
        
    """
    # drop rows with missing zipcodes
    dataframe = dataframe.drop(
        dataframe["zipcode"][dataframe["zipcode"].isna()].index.tolist(), axis=0
    )

    # drop "host_location", "neighbourhood" because of redundant information
    dataframe = dataframe.drop(["host_location", "neighbourhood"], axis=1)

    # filling summary rows with the keyword "missing"
    dataframe["summary"][dataframe["summary"].isna()] = "missing"

    # replace missing property types and host_response_time with the mode
    for column in ["property_type", "host_response_time"]:
        dataframe[column] = get_mode(dataframe, column)

    # handle missing values for market, host_neighbourhood, city
    for column in ["market", "host_neighbourhood", "city"]:
        dataframe = get_mode_by_zip(dataframe, column)

    # drop any rows with missing city
    dataframe = dataframe.drop(
        dataframe["host_neighbourhood"][
            dataframe["host_neighbourhood"].isna()
        ].index.tolist(),
        axis=0,
    )

    # drop any rows with missing host_neighbourhood
    dataframe = dataframe.drop(
        dataframe["city"][dataframe["city"].isna()].index.tolist(), axis=0
    )

    return dataframe


def handle_repetitive_data(dataframe):
    """Remove columns with redundant data. Also, remove duplicate rows.

    Args:
        dataframe (Dataframe): a dataframe object 

    Returns:
        Dataframe: a clean Dataframe with no redundant or duplicate rows.  

    """

    # experiance_offered column has one single value none - not useful
    # host_listings_count and  host_total_listings_count are the same drop the last
    # neighbourhood_group_cleansed similar to neighbourhood_cleansed so drop it
    # jurisdiction_names has one single value, drop it.
    columns_to_drop = [
        "experiences_offered",
        "host_listings_count",
        "neighbourhood_group_cleansed",
        "jurisdiction_names",
    ]
    for column in columns_to_drop:
        try:
            dataframe.drop(column, inplace=True, axis=1)
        except (KeyError):
            # columns already dropped because it has nulls more than the threshold
            pass

    # drop duplicate rows if any
    dataframe.drop_duplicates(inplace=True)
    return dataframe


def clean_data(dataframe):
    """Clean the dateframe by imputing missing values, removing duplicate rows, removing redundant columns
       and transform columns from an object datatype to numerical datatype  
    
        Args:
            dataframe (Dataframe): a dataframe object 
            
        Returns:
            Dataframe: a clean Dataframe ready for analysis. 
        
    """

    # remove , and $ from the price column
    money_to_numeric_cols = ["price", "extra_people"]
    perc_to_numeric_cols = ["host_response_rate", "host_acceptance_rate"]

    # convert money strings to ints
    for column in money_to_numeric_cols:
        try:
            dataframe[column] = pd.to_numeric(money_to_numeric(dataframe[column]))
        except (KeyError):
            # columns already dropped because it has nulls more than the threshold
            pass
    # convert percentage strings to numbers
    for column in perc_to_numeric_cols:
        try:
            dataframe[column] = pd.to_numeric(percentage_to_numeric(dataframe[column]))
        except (KeyError):
            # columns already dropped because it has nulls more than the threshold
            pass

    dataframe = handle_repetitive_data(dataframe)

    # fill missing values in numerical columns with median
    dataframe = handle_numeric(dataframe, method="median")

    dataframe = handle_categorical(dataframe)

    return dataframe


# convert each row of the host_verifications column from a string to a list of verifications or available amenities
def split_by_pattern(string, pattern):
    """Remove the pattern from the string and return a list of used verification or available amenities.
    
        Args:
            string (string): a string object
            pattern (string): a regex pattern to be removed from the string
            
        Returns:
            list: a list of verification or available amenities    
        
    """
    return re.sub(pattern=pattern, repl="", string=string).split(",")


def get_df_from_column(dataframe, column, pattern):
    """Return a dataframe for specific column after parsing it and remvoing a specific pattern.
    
        Args:
            dataframe (Dataframe): a dataframe object
            column (string): column name
            pattern (string): a regex pattern to be removed from each string in the desired column
            
        Returns:
            Dataframe: dataframe of verification methods or available amenities
        
        """
    df_column = dataframe[column].apply(lambda x: split_by_pattern(x, pattern))
    df_column = pd.DataFrame(df_column)

    values_set = sorted(set(list(chain.from_iterable(df_column[column].tolist()))))

    for value in values_set:
        df_column[value] = df_column[column].apply(lambda x: int(value in x))

    df_column["number_of_{}".format(column)] = df_column[column].apply(len)

    if column == "amenities":
        column_to_drop = [
            "",
            "translation missing: en.hosting_amenity_49",
            "translation missing: en.hosting_amenity_50",
        ]
        try:
            df_column.drop(column_to_drop, axis=1, inplace=True)
        except KeyError:
            df_column.drop(column_to_drop[0], axis=1, inplace=True)
    return df_column


def align_dataframes(df1, df2):
    """print a nice formated table of each column name and its number of nulls.
    
        Args:
            dataframe (Dataframe): a dataframe object 
            
        Returns:
            None 
        
        """

    columns_diff = set(df2.columns.tolist()).difference(set(df1.columns.tolist()))
    df2.drop(columns_diff, axis=1, inplace=True)
    return df2


def generate_db(
    db_name, df_list, table_names=["listings", "verifications", "amenities"]
):
    """Generate a database for each dataframe of the city

    Args:
        db_name (string): database name
        df_list (list): list of dataframes
        table_names (list): list of table names

    Returns:
        SQL Database: return a SQL Database with three tables; listings, verifications, amenities

    """
    # connect to the database
    # the database file will be db_name.db
    # note that sqlite3 will create this database file if it does not exist already
    conn = sqlite3.connect(r"{}.db".format(db_name))
    for i, df in enumerate(df_list):
        if i:
            df = df.copy()
            df = df.drop(df.columns[0], axis=1)
            df = df.reset_index()
            df.to_sql(table_names[i], con=conn, if_exists="replace", index=False)
        else:
            df.to_sql(table_names[i], con=conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

# run this cell to create a folder for each city with csv files for each dataframe
def generate_csv(
    file_path,
    df_list,
    csv_names=[
        "listings",
        "verifications",
        "amenities",
        "reviews",
        "wc_summary",
        "wc_reviews",
    ],
):
    """Create a folder for each city and save a csv file for each dataframe of this city

    Args:
        file_path (string): folder name name
        df_list (list): list of dataframes
        csv_names (list): list of csv names

    Returns:
        csv file: return three csv files; listings, verifications, amenities, "reviews", "wc_summary", "wc_reviews"

    """

    if file_path not in os.listdir("data files"):
        os.makedirs(r"data files\{}".format(file_path))

    for i, df in enumerate(df_list):
        df.to_csv(path_or_buf=r"data files\{}\{}.csv".format(file_path, csv_names[i]))

    os.chdir(".")

