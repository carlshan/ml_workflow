import sys
import boto
import os

BUCKET_NAME = "<<BUCKET>>"

def upload_to_s3(local_filepath, file_name, s3_path, bucket_name=BUCKET_NAME):
	"""
	Returns
	----------
	Uploads local file to appropriate s3 key, and prints status

	Parameters
	----------
	local_filepath : str
	    ex. 'my/local/path'
	file_name : str
	    ex. 'cleaned_data.csv' or 'model.pkl'
	bucket_name : str
	    ex. 'dsapp-edu-data'
	s3_path : str
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
	full_key_name = os.path.join(s3_path, file_name)
	k = bucket.new_key(full_key_name)
	full_filepath = os.path.join(local_filepath, file_name)
	k.set_contents_from_filename(full_filepath, cb=percent_cb, num_cb=10)

	return None


def df_to_S3(df, local_filepath, file_name, s3_path, bucket_name=BUCKET_NAME):
	#NOTE: Not used due to csv living locally in results
        """
        Returns
        ----------
        Uploads a df to s3 as a CSV file.

        Parameters
        ----------
        df : pd.DataFrame
	local_filepath : str
	    A folder where the csv can be stored locally. It may be deleted afterwards.
        file_name: str
            ex: 'stars.csv'
        bucket_name: str
        s3_path : full path for upload
            ex: '/test/'
        """
        full_filepath = os.path.join(local_filepath, file_name)
        df.to_csv(full_filepath, index=False)
        print "Uploading {} to S3".format(file_name)
        upload_to_s3(local_filepath, file_name, bucket_name, s3_path)
        print "Complete"
	print "File is at: s3://{}/{} \n".format(bucket_name, s3_path)

        return None
