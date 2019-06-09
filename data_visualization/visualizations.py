import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# show the distribution of missing values per column
def nans_distribution(title, dataframe, threshold=0.25, row=False):
    """Create a distribution of missing values per row or column for a dataframe.
    
        Args:
            title (string): the title of the distribution chart
            dataframe (Dataframe): a dataframe object 
            threshold (float): a value to divide the chart into two areas; columns or rows with NANs below the threshold 
            and others above this threhold  
            row (bool): if True, it will returns missings values per row. If False, it will return missing values 
            per column.
            
        Returns:
            figure: a matplotlib distribution figure of missing values per row or column
        
        """
    # set figure paramters for row and column charts
    if row:
        axis = 1
        n = dataframe.shape[1]
        xlabel = "% of Nulls/Row"
        ylabel = "Number of Rows"
        y = dataframe.shape[0] * 0.25
        xy_cor = y * 0.95
        dx1 = 0.2
        dx2 = 5
    else:
        axis = 0
        n = dataframe.shape[0]
        xlabel = "% of Nulls/Column"
        ylabel = "Number of Columns"
        y = dataframe.shape[1] * 0.5
        xy_cor = y * 0.95
        dx1 = 0.5
        dx2 = 20

    # create a distribution chart using the sns.distplot
    threshold = threshold * 100
    series = 100 * dataframe.isna().sum(axis=axis).sort_values() / n
    ax = sns.distplot(series.values, kde=False)
    sns.despine(right=True, top=True)  # remove right and top borders
    ax.figure.set_figwidth(15)
    ax.figure.set_figheight(7)

    # add a vertical line to seperate between rows or columns above and below the threshold
    plt.axvline(x=threshold, linestyle="--", color="darkred")
    plt.text(x=threshold + 0.2, y=y, s="Missing values more than {}%".format(threshold))
    plt.annotate(
        s="",
        xy=(threshold + dx1, xy_cor),
        xytext=(threshold + dx2, xy_cor),
        arrowprops=dict(arrowstyle="<-"),
    )

    # Add title and labels to the figure
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


def wordcloud_image(dataframe, column):
    """Word Cloud image for frquently used words in each column.
    
        Args:
            dataframe (Dataframe): a dataframe object
            column (string): column name
            
        Returns:
            None 
        
        """

    # Create stopword list:
    # to combine all summaries into one image
    text = " ".join(sentence for sentence in dataframe[column])
    print(
        "There are {} words in the combination of all reviews or summaries.".format(
            len(text)
        )
    )
    stopwords = set(STOPWORDS)

    # Generate a word cloud image
    wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(text)

    # Display the generated image:
    # the matplotlib way:
    plt.figure(figsize=[10, 5])
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    df = pd.DataFrame.from_dict(wordcloud.words_, orient="index")
    df.reset_index(inplace=True)
    df.columns = ["Word", "Counts"]

    return df
