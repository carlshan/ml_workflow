from workflow_diagnostics import get_diagnostics_dict
from workflow_util import upload_to_s3
from sklearn import preprocessing
import cPickle as pickle
import pandas as pd
import os

def run_model(training, testing, features, outcome, clf,
		clf_name, normalize=True, verbose=True):
    # NOTE: You should set the clf seed ahead of time

    if verbose:
        print 'Starting training of: {}'.format(clf_name)
        print '----------'
        print 'Num Features: {}'.format(len(features))
        print 'Shape of Training: {}'.format(training.shape)
        print 'Shape of Testing: {}'.format(testing.shape)
        print 'Outcome: {}'.format(outcome)


    X_train, y_train = training[features].values, training[outcome].values
    X_test = testing[features].values
    if normalize:
        X_train = preprocessing.StandardScaler().fit(X_train).transform(X_train)
        X_test = preprocessing.StandardScaler().fit(X_test).transform(X_test)

    fitted_clf = clf.fit(X_train, y_train)

    if verbose:
        print 'Finished Training'
        print '\n'
        print 'Starting Testing:'
        print '----------'
    predicted_probabilities = fitted_clf.predict_proba(X_test)

    if verbose:
        print 'Finished Testing...\n'

    return fitted_clf, predicted_probabilities

def run_and_output_model_to_s3(training, testing, features, outcome, clf, clf_name, s3_path,
			       verbose=True, **kwargs):

    fitted_clf, predicted_probs = run_model(training, testing, features, outcome, clf,
					    clf_name, verbose)
    #Pickling happens here
    os.mkdir('../results/temp/')
    filepath = os.path.join('../results/temp', clf_name + '.pkl')
    pickle.dump(fitted_clf, open(filepath, 'wb'))
    print 'Uploading to S3 at {}'.format(s3_path)
    upload_to_s3('../results/temp', clf_name + '.pkl', s3_path = s3_path)
    print 'Done uploading {} to s3 \n'.format(filepath)
    os.remove(filepath)
    os.rmdir('../results/temp/')

    # Putting the diagnostics dict into a dataframe and saving to results folder
    diagnostics_dict = get_diagnostics_dict(fitted_clf, testing, features, outcome, clf_name, **kwargs)
    results_df = pd.read_csv('../results/results.csv')
    results_df = results_df.append([diagnostics_dict])
    results_df.to_csv(path_or_buf='../results/results.csv', index=False)
    return diagnostics_dict
