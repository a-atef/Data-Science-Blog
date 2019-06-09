import pandas as pd


def read_data(csv_path, index_col, drop_columns, parse_date):
    """read in data from a csv file.
    
        Args:
            csv_path (string): path and name of a csv file
            index_col (string): name of column used as an index for each row
            drop_columns (list): columns to ignore while reading from the csv file
            parse_date (list): columns that should be parsed and converted to datetime
            
        Returns:
            dataframe: a pandas dataframe
        
    """

    # drop irrelevant columns from the data file
    if not len(drop_columns):
        drop_columns = [
            "listing_url",
            "description",
            "host_name",
            "name",
            "scrape_id",
            "last_scraped",
            "calendar_updated",
            "calendar_last_scraped",
            "country_code",
            "country",
            "notes",
            "thumbnail_url",
            "medium_url",
            "picture_url",
            "xl_picture_url",
            "host_id",
            "host_url",
            "host_thumbnail_url",
            "host_picture_url",
        ]

    # read boston data, make id column as index
    df = pd.read_csv(csv_path, index_col=index_col, parse_dates=parse_date)
    df.drop(drop_columns, axis=1, inplace=True)
    return df
