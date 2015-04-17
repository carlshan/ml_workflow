import pandas as pd
import time
import re
from util import upload_to_s3

# For naming cleaned files
TIME = time.localtime()
MONTH = TIME.tm_mon
DAY = TIME.tm_mday
YEAR = TIME.tm_year
CLEAN_SUFFIX = '_clean_{year}_{month}_{day}'.format(year=YEAR, month=MONTH, day=DAY)

# Change these when necessary
RAW_FILEPATH = '<<PATH>>'
CLEAN_FILEPATH = '<<PATH>>'

# S3
BUCKET_NAME = '<<NAME>>'
S3_CLEANED_DATA_DIR = '<<CLEANED>>'

def clean_cabarrus_suspension(susp_df):
    """
    Returns
    ---------
    Returns a cleaned suspension data frame with the following cleaning routines run

    Parameters
    ----------
    susp_df : pd.DataFrame
	suspension dataframe
    """

    def convert_to_reporting_year(date_string):
	"""
	Helper function to convert suspension column to Reporting Year format
	"""

	if pd.isnull(date_string): # do nothing if null
	    return date_string
	else:
	    converted_date = datetime.datetime.strptime(date_string, '%m/%d/%Y')
	    if converted_date.month <= 7: # if it happened during second semester
		return converted_date.year # reporting year happens at the end of a school year
	    else: # if it happened during first semester
		return converted_date.year + 1

    cleaned_susp_df = susp_df.copy(deep=True)
    # Warning: the below takes a few minutes to run
    cleaned_susp_df['Converted Reporting Year'] = cleaned_susp_df['Incident Date'].apply(convert_to_reporting_year)

    return cleaned_susp_df

def clean_cabarrus_post_sec(post_sec_df):
  """
  Returns
  ----------
  Returns a cleaned post secondary dataframe with the following cleaning
  routines run.

  Parameters
  ----------
  post_sec_df : pd.DataFrame
      dataframe of Cabarrus Clearinghouse data
  """
  # Start writing cleaning routines below
  # ----------
  cleaned_post_sec_df = post_sec_df.copy(deep=True)

  ## Removing '_' from the end of each value in 'YOUR_UNIQUE_IDENTIFIER'
  ## Note: Since Brian reuploaded this data on 10-1-2014 with External_Student_ID, this is no longer necessary
  # to_remove = re.compile('_')
  # cleaned_post_sec_df = post_sec_df.replace(to_replace={'YOUR_UNIQUE_IDENTIFIER':
  #                                                         {to_remove: ''}
  #                                                       },
  #                                                       inplace=False)
  # ## Converting each value in 'YOUR_UNIQUE_IDENTIFIER' to an int
  # cleaned_post_sec_df['YOUR_UNIQUE_IDENTIFIER'] = cleaned_post_sec_df['YOUR_UNIQUE_IDENTIFIER'].apply(int)

  # ----------
  # End cleaning routines

  return cleaned_post_sec_df


def clean_cabarrus_dropout(dropout_df):
    """
    Returns
    ----------
    Returns a cleaned dropout dataframe with the following cleaning routines performed

    Parameters
    ----------
    dropout_df : pd.DataFrame
        dataframe of Cabarrus dropout dataframe
    """
    # Starting writing cleaning routines below
    # ----------

    ## Removing funky the character from columns
    clean_dropout_df = dropout_df.copy(deep=True)
    clean_dropout_df['Gender'] = clean_dropout_df['Gender'].apply(lambda s: s.decode('latin-1').replace(u' \xa0', ''))
    clean_dropout_df['Age'] = clean_dropout_df['Age'].apply(lambda s: s.decode('latin-1').replace(u' \xa0', ''))
    clean_dropout_df['DO_year'] = clean_dropout_df['DO_year'].apply(lambda s: s.decode('latin-1').replace(u' \xa0', ''))
    clean_dropout_df['Ethnicity'] = clean_dropout_df['Ethnicity'].apply(lambda s: s.decode('latin-1').replace(u' \xa0', ''))
    # ---------
    # End cleaning routines

    return clean_dropout_df


def clean_files(raw_filepath, clean_filepath):
  """
  Runs all the clean routines
  """

  # Cleans Cabarrus post-secondary data
  print 'Starting Cabarrus post-secondary data cleaning...'
  post_sec_raw_filename = 'Cabarrus Grade results Clearing house-DETAIL 2008-2013 grads ExternalID'
  post_sec_clean_filename = post_sec_raw_filename + CLEAN_SUFFIX
  post_sec_raw_df = pd.read_csv(raw_filepath + post_sec_raw_filename + '.csv')
  cleaned_post_sec_df = clean_cabarrus_post_sec(post_sec_raw_df)
  cleaned_post_sec_df.to_csv(clean_filepath + post_sec_clean_filename + '.csv',
                             index=False)
  upload_to_s3(clean_filepath, post_sec_clean_filename + '.csv', BUCKET_NAME, S3_CLEANED_DATA_DIR)
  print 'Finished cleaning and saved to {}'.format(clean_filepath + post_sec_clean_filename + '.csv')

  # Cleans Cabarrus dropout data
  print 'Starting Cabarrus dropout data cleaning...'
  dropout_raw_filename = 'Dropout_Data_0708_1213_20141001'
  dropout_clean_filename = dropout_raw_filename + CLEAN_SUFFIX
  dropout_raw_df = pd.read_table(raw_filepath + dropout_raw_filename + '.txt')
  cleaned_dropout_df = clean_cabarrus_dropout(dropout_raw_df)
  cleaned_dropout_df.to_csv(clean_filepath + dropout_clean_filename + '.txt',
		  	    index=False)
  upload_to_s3(clean_filepath, dropout_clean_clean_filename + '.txt', BUCKET_NAME, S3_CLEANED_DATA_DIR)
  print 'Finished cleaning and saved to {}'.format(clean_filepath + dropout_clean_filename + '.txt')

  # Cleans Cabarrus suspension data
  print 'Starting Cabarrus suspension data cleaning...'
  suspension_raw_filename = 'Student_Suspension_Data_20141001'
  suspension_clean_filename = suspension_raw_filename + CLEAN_SUFFIX
  suspension_raw_df = pd.read_table(raw_filepath + suspension_raw_filename + 'txt')
  cleaned_suspension_df = clean_cabarrus_suspension(suspension_raw_df)
  df_to_s3(cleaned_suspension_df, clean_filepath, suspension_clean_filename, BUCKET_NAME, S3_CLEANED_DATA_DIR)
  return None


if __name__ == '__main__':
  print 'Starting cleaning...'
  start_time = time.time()
  clean_files(RAW_FILEPATH, CLEAN_FILEPATH)
  end_time = time.time()
  print 'Cleaning ended. {} seconds have elapsed'.format(end_time - start_time)
