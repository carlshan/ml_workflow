import boto
import os
import sys
import pandas as pd
import datetime


def upload_to_s3(local_file_path, file_name, bucket_name, s3_directory):
	"""
	Returns
	----------
	Uploads local file to appropriate s3 key, and prints status

	Parameters
	----------
	local_file_path : str
	    ex. 'my/local/path'
	file_name : str
	    ex. 'cleaned_data.csv'
	bucket_name : str
	    ex. 'dsapp-edu-data'
	s3_directory : str
	    ex. 'NC-Cabarrus/cleaned_data'
	"""

	def percent_cb(complete, total):
	    """
	    Helper function that prints progress
	    """
	    sys.stdout.write('.')
	    sys.stdout.flush()

	conn = boto.connect_s3()
	bucket = conn.get_bucket(bucket_name)
	full_key_name = os.path.join(s3_directory, file_name)
	k = bucket.new_key(full_key_name)
	full_filepath = os.path.join(local_file_path, file_name)
	k.set_contents_from_filename(full_filepath, cb=percent_cb, num_cb=10)

	return None


def df_to_S3(df, clean_filepath, file_name, s3_bucket, s3_path):
        """
        Returns
        ----------
        Uploads a df to s3 as a CSV file.

        Parameters
        ----------
        df : pd.DataFrame
        file_name: str
            ex: 'stars.csv'
        s3_bucket : str
        s3_path : full path for upload
            ex: '/test/'
        """
        full_filepath = os.path.join(clean_filepath, file_name)
        df.to_csv(full_filepath, index=False)
        print "uploading Dataframe to S3"
        upload_to_s3(clean_filepath, file_name, s3_bucket, s3_path)
        print "Complete"

        return None


def merge_data_by_years(to_merge, data, reporting_year, how='left'):
    """
    Generalized version of merging each particular df
    """
    groups = to_merge.groupby(reporting_year).groups
    for group, rows in groups.iteritems():
        temp = to_merge.ix[rows].drop([reporting_year], axis=1)
        temp.rename(columns={col: col + '_' + str(group) for col in temp.columns},
                    inplace=True)  # appends school year to each col
        data = data.merge(temp, left_on='External_Student_ID',
                          right_on='External_Student_ID_' + str(group),
                          how=how)
        data.drop('External_Student_ID_' + str(group), axis=1, inplace=True)
    return data


def merge_yearly_gpa(cohort_df, yearly_gpa_df):
	years_in_data = set(yearly_gpa_df['ReportingYear'].unique())
	for year in years_in_data:
		yearly_df = yearly_gpa_df[yearly_gpa_df['ReportingYear'] == year]
		yearly_df.drop(['ReportingYear', 'SchoolYear'], axis=1, inplace=True)
		yearly_df.rename(columns={col: col + '_' + str(year)
					for col in yearly_df.columns},
					inplace=True)
		cohort_df = cohort_df.merge(yearly_df, left_on='External_Student_ID',
			right_on = 'External_Student_ID_' + str(year),
			how='left')
		cohort_df.drop('External_Student_ID_' + str(year), axis=1, inplace=True)
	return cohort_df


def merge_demographic_attendence(cohort_df, demog_attend_df):
	years_in_data = set(demog_attend_df['reporting_year'].unique())
	flagged_ids = set()
	for year in years_in_data:
		yearly_df = demog_attend_df[demog_attend_df['reporting_year'] == year]
		num_appearances = yearly_df['External_Student_ID'].value_counts()
		flagged_ids = flagged_ids.union(set(num_appearances[num_appearances > 1].index))  # flag collapsed students
		group_cols = ['External_Student_ID', 'ethnic', 'sex', 'swd', 'eds', 'lep']
		yearly_df = yearly_df.groupby(by=group_cols, as_index=False).sum() #collapse if appear multiple times
		yearly_df.rename(columns={col: col + '_' + str(year) for col in yearly_df.columns},
                    inplace=True)
		cohort_df = cohort_df.merge(yearly_df,
			left_on='External_Student_ID',
			right_on='External_Student_ID_' + str(year),
			how='left')
		cohort_df.drop('External_Student_ID_' + str(year), axis=1, inplace=True)
	return cohort_df, flagged_ids


def merge_address_history(cohort_df, add_hist_df):
	years_in_data = set(add_hist_df['ReportingYear'].unique())
	for year in years_in_data:
		yearly_df = add_hist_df[add_hist_df['ReportingYear'] == year]
		yearly_df.drop('ReportingYear',axis = 1, inplace = True)
        num_appearances = yearly_df['External_Student_ID'].value_counts()
        yearly_df.rename(columns={col: col + '_' + str(year) for col in yearly_df.columns}, inplace=True)
        cohort_df = cohort_df.merge(yearly_df, left_on='External_Student_ID',
                            right_on = 'External_Student_ID_' + str(year), how='left')
        cohort_df.drop('External_Student_ID_' + str(year), axis=1, inplace=True)
	return cohort_df

def make_rename_col_dict(cols, graduating_year):
    """
    Returns dictionary to rename columns respective to each graduating year
    e.g., 'GPA_2008' --> 'GPA_8th_grade' for students in class of 2012

    Returns
    ----------
    dict

    Parameters
    ----------
    cols : array
        list of all columns to rename
    graduating_year : int
        expected graduating year for a cohort
    """
    d = {col: col for col in cols}
    mappings = zip(range(8, 13), range(graduating_year-4, graduating_year+1))
    for grade, year in mappings:
        append = str(grade) + 'th_grade'
        temp = {col: col.replace(str(year), append) for col in cols if str(year) in col}
        d.update(temp)
    return d


# The dfSusp data, which is the last file in the list, needs to have
# a new column created with a converted reporting year
def convert_to_reporting_year(date_string):
    if pd.isnull(date_string):
        return date_string
    else:
        converted_date = datetime.datetime.strptime(date_string, '%m/%d/%Y')
        if converted_date.month <= 7: # if it happened during second semester
            return converted_date.year # reporting year happens at the end of a school year
        else: # if it happened during first semester
            return converted_date.year + 1

