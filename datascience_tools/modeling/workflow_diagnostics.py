import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
from sklearn.metrics import roc_curve, auc, precision_recall_curve
from math import floor


# TODO: Have better documentation
def plot_roc_curve(test_outcomes, probs, clf_name, plot_curve=True, **kwargs):
    """
    test_outcomes should be an array of true labels
    probs is an array of probabilities of belonging to class 1
    Plots FPR vs TPR
    Returns fpr, tpr, thresholds
    """
    if type(probs) == np.array and probs.ndim == 2:
        probs = [p[1] for p in probs]

    fpr, tpr, thresholds = roc_curve(test_outcomes, probs, pos_label=1)
    roc_auc = auc(fpr, tpr)

    if plot_curve:
        # Plot ROC curve
        plt.figure()
        plt.plot(fpr, tpr, label='ROC curve (area = %0.3f)' % roc_auc, **kwargs)
        plt.plot([0, 1], [0, 1], 'k--')  # random predictions curve
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel('False Positive Rate or (1 - Specificity)')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve - {}'.format(clf_name))
        plt.legend(loc="best")
    return roc_auc, fpr, tpr, thresholds


def plot_precision_recall_curve(test_outcomes, probs, clf_name, plot_curve=True, **kwargs):
    """
    test_outcomes is an array of true labels
    probs is an array of probabilities for each item belonging to class one
    Plots recall (x-axis) vs precision (y-axis)
    Returns precision, recall, thresholds
    """
    if type(probs) == np.array and probs.ndim == 2:
        probs = [p[1] for p in probs]

    precision, recall, thresholds = precision_recall_curve(test_outcomes, probs)
    pr_auc = auc(recall, precision)
    if plot_curve:
        plt.figure()
        plt.plot(recall, precision, label='Precision-Recall Curve (area = {:.2f}'.format(pr_auc), **kwargs)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Recall-Precision Curve - {}'.format(clf_name))
        plt.legend(loc='best')
    return pr_auc, precision, recall, thresholds

def plot_feature_importance(fitted_model, feature_cols, plot_importances=True):
    """
    Plots feature importances and standard deviations for ensemble methods like
    RF.
    Returns:
        importances: list
        std: list
    """
    importances = fitted_model.feature_importances_
    std = np.std([tree.feature_importances_ for tree in fitted_model.estimators_],
                 axis=0)
    indices = np.argsort(importances)[::-1]
    num_features = len(indices)

    l = []
    for rank, ind in zip(np.arange(num_features), indices):
        l.append('{}. {} - ({:.3f}, std: {:.3f}) \n'.format(rank + 1,
                                    feature_cols[ind],
                                    importances[ind],
                                    std[ind]))
        s = ''.join(l)

    print s

    if plot_importances:
        plt.figure()
        plt.title("Feature importances")
        plt.bar(range(num_features), importances[indices],
            color="r", yerr=std[indices], align="center")
        plt.xticks(range(num_features), np.array(feature_cols)[indices], rotation=270)
        plt.xlim([-1, num_features])
        plt.ylim([0, 0.5])
        plt.show()
    return importances, std


def plot_marginal_precision_curve(labels, predicted_probs, **kwargs):
    """Returns marginals (% true / total students with that prob) and plots it
    against predicted probabilities. A straight line is good."""
    df = pd.DataFrame(data={'outcome': labels, 'probs': predicted_probs})
    totals = [df[df['probs'] == p].shape[0] for p in predicted_probs]
    trues = [df[df['probs'] == p]['outcome'].sum() for p in predicted_probs]
    marginals = [float(true)/total for true, total in zip(trues, totals) if total != 0]
    plt.figure()
    plt.plot(predicted_probs, marginals, **kwargs)
    plt.title('Marginal Precision Curve')
    plt.xlabel('Predicted Probs')
    plt.ylabel('Actual Proportions')
    plt.show()
    return marginals


def precision_at_top_x(fitted_clf, X_test, y_test, clf_name='', top_n=[], top_p=[], print_results=True):
    """
    Prints and returns precicion at Top X and Top X%, given a model, test data, and known outcomes
    fitted_clf is the classifier
    X_test is a matrix of values pertaining to test dataset
    y_test is a column of values pertaining to outcomes in test dataset
    clf_name is a string describing the classifier
    top_n is a list of numbers for computing precision
    top_p is a list of percentiles

    Dependencies: math.floor
    """
    #Initialize ouptputs
    TopX_n =[]
    TopX_p =[]
    #Compute predictions based on model
    predicted_probs = fitted_clf.predict_proba(X_test)
    predicted_probs = [p[1] for p in predicted_probs]

    # Computing and print topX results
    for n in top_n:
	# .iloc is needed for proper indexing.
        TopX_n.append((pd.Series(y_test).iloc[np.argsort(predicted_probs)[::-1][:n]].value_counts(normalize=True)[1]*100).round(2))

    if all([i>0 and i<1 for i in top_p]): #if input as descimals, change to integers
        top_p = top_p * 100

    for p in top_p:
        nrows = X_test.shape[0]
        n = floor( (p/100.0) * nrows)
        TopX_p.append((pd.Series(y_test).iloc[np.argsort(predicted_probs)[::-1][:n]].value_counts(normalize=True)[1]*100).round(2))

    if print_results:
        print "Precision at Top X Results for " + clf_name
        print "----------------"
        TopX_n_df = pd.DataFrame(columns=[str(x) for x in top_n],
                                 index=['% Dropout'])
        TopX_n_df.iloc[0] = TopX_n
        print TopX_n_df
        print '\n'
        print "Precision at Top X% Results for " + clf_name
        print "----------------"
        TopX_p_df = pd.DataFrame(columns=[str(p) + '%' for p in top_p], index=['% Dropout:'])
        TopX_p_df.iloc[0] = TopX_p
        print TopX_p_df

	print '\n'

    return (predicted_probs, TopX_n, TopX_p)

def get_diagnostics_dict(fitted_clf, testing_data, feature_cols, outcome_col, clf_name,
                    get_feature_importances=True, print_importances=True, get_pr=True, plot_pr=True,
                    get_roc=True, plot_roc=True, get_precision_at_top_x=True,
                    top_n=[30,50,100,200], top_p=[5,10,20,30,50], print_results=True):
    results_dict = dict()
    X_test, y_test = testing_data[feature_cols].values, testing_data[outcome_col].values
    predicted_probs = fitted_clf.predict_proba(X_test)
    now = datetime.datetime.now()
    results_dict['outcome'] = outcome_col
    results_dict['number of rows tested on'] = testing_data.shape[0]
    results_dict['number of features'] = len(feature_cols)
    results_dict['model name'] = clf_name
    results_dict['timestamp'] = now.__str__()

    if get_precision_at_top_x:
        pred_probs, TopX_n, TopX_p = precision_at_top_x(fitted_clf, X_test, y_test, clf_name,
                                                    top_n = top_n, top_p = top_p,
                                                        print_results = print_results)

        results_dict['top x students'] = top_n
        results_dict['top p% students'] = top_p
        results_dict['% outcome on top x students'] = TopX_n
        results_dict['% outcome on top p% students'] = TopX_p

    if get_pr:
        pr_auc, precision, recall, pr_thresholds = plot_precision_recall_curve(y_test,
                                                                              predicted_probs,
                                                                              clf_name,
                                                                              plot_pr)
        results_dict['PR AUC'] = round(pr_auc, 3)

    if get_roc:
        roc_auc, tpr, fpr, roc_thresholds = plot_roc_curve(y_test,
                                                          predicted_probs,
                                                          clf_name, plot_roc)
        results_dict['ROC AUC'] = round(roc_auc, 3)

    if get_feature_importances:
        feature_cols, importances, indices, std, s = plot_feature_importance(fitted_clf, feature_cols, print_importances)
        results_dict['ranked features'] = s

    if print_importances:
        print("Feature Importances:")
        print '----------'
        print s

    return results_dict
