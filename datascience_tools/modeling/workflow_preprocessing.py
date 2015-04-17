import cabarrus
import numpy as np

def empirical_imputation(s, seed = None):
    """
    Given a Series object containing nans, returns a Series object
    where each of the nan rows has been replaced with a random draw
    from all possible non-nan values.
    """

    np.random.seed(seed)
    s_replaced = s.copy()
    empirical_distribution = s_replaced.dropna().apply(lambda v: v[0] if not(v, np.float64)
                                              else v).values # some values are packed as a list

    sample = np.random.choice(a=empirical_distribution, size=s_replaced.isnull().sum(), replace=True)
    s_replaced[s_replaced.isnull()] = sample

    return s_replaced


def preprocess_data(raw_data, partner_name, cohort_graduating_year, earliest_grade, model_grade,
	       impute=True, empirical_imputation_variables=[], mean_imputation_variables=[],
	       median_imputation_variables=[], mode_imputation_variables=[],
	       seed=None):
    """
    Applies preprocessing routines to raw_data. Returns data with columns normalized
    to education schema.

    Returns:
    ----------
    DataFrame
    """
    renamed_data = rename_cols_to_schema(raw_data, partner_name, cohort_graduating_year,
                                            earliest_grade)
    if partner_name == 'cabarrus':
        data = cabarrus.get_students_enrolled_in_grade_and_did_not_transfer_out(renamed_data, model_grade)

    if partner_name == 'mcps':
        #TODO
        pass

    if impute:
        imputed_data = impute_data(data, empirical_imputation_variables, mean_imputation_variables,
                    median_imputation_variables, mode_imputation_variables, seed)
        return imputed_data

    else:
        return data


def impute_data(data, empirical_imputation_variables=[],
	            mean_imputation_variables=[],
		        median_imputation_variables=[],
                mode_imputation_variables=[],
                seed=None):
    # Creating a copy so as to not modify input dataframe
    imputed_data = data.copy(deep=True)

    for col in empirical_imputation_variables:
        imputed_data[col] = empirical_imputation(imputed_data[col], seed=seed)

    for col in mean_imputation_variables:
        imputed_data[col].fillna(imputed_data[col].mean(), inplace=True)

    for col in median_imputation_variables:
        imputed_data[col].fillna(imputed_data[col].median(), inplace=True)

    for col in mode_imputation_variables:
        imputed_data[col].fillna(imputed_data[col].mode().iloc[0], inplace=True)

    return imputed_data


def rename_cols_to_schema(dataframe, partner_name, cohort_graduating_year, earliest_grade):
    """
    Given a specific cohort's data frame, applies the appropriate renaming convention to be inline with our internal data schema
    See: https://docs.google.com/a/uchicago.edu/spreadsheets/d/1vCiIKFhDakqLzmGO8d5-gmpaXg3hKDEyiUAgGQkwPHE/edit#gid=0

    Returns:
    ----------
    dataframe : pd.DataFrame
	    DataFrame with columns renamed appropriately

    Parameters:
    ----------
    dataframe: pd.DataFrame
	DataFrame to be renamed. NOTE: This should be a dataframe with data only for one cohort.
    partner_name: str
	The name of the district we're using interally to refer to the partner e.g., 'cabarrus'
	Used to figure out which is the appropriate function to call for renaming columns
    cohort_graduating_year: int
	The expected graduating year of the cohort e.g., 2014
    earliest_grade : int
	This is the earliest school grade we have data available for the cohort
    """

    # http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.rename.html
    if partner_name == 'cabarrus':
        dict_mapping = cabarrus.make_rename_col_dict(column_names=dataframe.columns,
                                cohort_graduating_year=cohort_graduating_year,
                                earliest_grade=earliest_grade)
    elif partner_name == 'mcps':
        # generate appropriate renaming dict
       dict_mapping = {}
    return dataframe.rename(columns=dict_mapping, inplace=False)
