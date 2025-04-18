import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import datasets
from sklearn import svm

X, y = datasets.load_iris(return_X_y=True)
X.shape, y.shape

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)

X_train.shape, y_train.shape
X_test.shape, y_test.shape

clf = svm.SVC(kernel="linear", C=1).fit(X_train, y_train)
clf.score(X_test, y_test)

from sklearn.model_selection import cross_val_score

clf = svm.SVC(kernel="linear", C=1, random_state=42)
scores = cross_val_score(clf, X, y, cv=5)
scores

print(
    "%0.2f accuracy with a standard deviation of %0.2f" % (scores.mean(), scores.std())
)
