def print_null_columns(dataframe):
    """
    Prints the column name and percent null
    Parameters:
        dataframe : pd.DataFrame
    Returns:
        None
    """
    cols = dataframe.columns
    nrows = dataframe.shape[0]
    print 'Total rows: {}'.format(nrows)
    nrows = float(nrows)
    for i, col in enumerate(cols):
        n_null = dataframe[col].isnull().sum()
        percent_null = n_null/nrows * 100
        print '{}. {} - {:.2f}%'.format(i+1, col, percent_null)
