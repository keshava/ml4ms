
'''
@author:     Zhengguang Zhao
@copyright:  Copyright 2016-2019, Zhengguang Zhao.
@license:    MIT
@contact:    zg.zhao@outlook.com

'''

# SVM
import numpy as np 
import pandas as pd 
import time 


import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from sklearn import svm
from sklearn.metrics import confusion_matrix
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

from utils.utils import accuracy
from utils.io import display_cm

class ClassifierSVM:

    def __init__(self):
        
        

        self.training_accuracy = None
        self.correct_class_labels = None
        self.feature_vector = None
        self.scaled_features = None

        self.clf = None

        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None      
       
        

    def set_data(self, training_data, class_labels):
        self.training_data = training_data
        self.class_labels = class_labels

        self._conditioning_data()


    def _conditioning_data(self):
        ## Conditioning the data set
        self.correct_class_labels = self.training_data['Class'].values

        self.feature_vector = self.training_data.drop(['FileName','Class','ClassLabels'], axis=1)
        self.feature_vector.describe()

        #feature_vectors.dropna(axis=0,how='any')   

        scaler = preprocessing.StandardScaler().fit(self.feature_vector)
        self.scaled_features = scaler.transform(self.feature_vector)
        print(np.isnan(self.scaled_features))

        # reformat features matrix to:  X : array-like, shape (n_samples, n_features)
    

    
    def split_dataset(self, features, test_size = 0.2, random_state=42):

        X_train, X_test, y_train, y_test = train_test_split(features, self.correct_class_labels, test_size=0.2, random_state=42)

        self.X_train = X_train.copy()
        self.y_train = y_train.copy()
        self.X_test = X_test.copy()
        self.y_test = y_test.copy()

    def visualize_binary_class(self, class1, class2,  h = 1, count = None):

        import matplotlib.pyplot as plt

        data = self.training_data.loc[:, [class1, class2]].values
        label = self.training_data['Class'].values

        scaler = preprocessing.StandardScaler().fit(data)
        scaled_features = scaler.transform(data)

        X_train, X_test, y_train, y_test = train_test_split(scaled_features, label, test_size=0.2, random_state=42)

        if count != None and len(label) > count:        
            X = X_train[:count,:].copy()
            y = y_train[:count].copy()
        
        else:
            X = X_train.copy()
            y = y_train.copy()

        # we create an instance of SVM and fit out data. We do not scale our
        # data since we want to plot the support vectors
        C = 1.0  # SVM regularization parameter
        svc = svm.SVC(kernel='linear', C=C).fit(X, y)
        rbf_svc = svm.SVC(kernel='rbf', gamma=0.7, C=C).fit(X, y)
        poly_svc = svm.SVC(kernel='poly', degree=3, C=C).fit(X, y)
        lin_svc = svm.LinearSVC(C=C).fit(X, y)

        # create a mesh to plot in
        
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                            np.arange(y_min, y_max, h))

        # title for the plots
        titles = ['SVC with linear kernel',
                'LinearSVC (linear kernel)',
                'SVC with RBF kernel',
                'SVC with polynomial (degree 3) kernel']


        for i, clf in enumerate((svc, lin_svc, rbf_svc, poly_svc)):
            # Plot the decision boundary. For that, we will assign a color to each
            # point in the mesh [x_min, m_max]x[y_min, y_max].
            plt.subplot(2, 2, i + 1)
            plt.subplots_adjust(wspace=0.4, hspace=0.4)

            Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

            # Put the result into a color plot
            Z = Z.reshape(xx.shape)
            plt.contourf(xx, yy, Z, cmap=plt.cm.Paired, alpha=0.5)

            # Plot also the training points
            plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.Paired)
            plt.xlabel(class1)
            plt.ylabel(class2)
            plt.xlim(xx.min(), xx.max())
            plt.ylim(yy.min(), yy.max())
            plt.xticks(())
            plt.yticks(())
            plt.title(titles[i])

        plt.show()

    def pca_2d(self):
        '''
        ## PCA analysis
        # 1. The PCA algorithm:
        # 2. takes as input a dataset with many features.
        # reduces that input to a smaller set of features (user-defined or algorithm-determined) 
        # by transforming the components of the feature set into what it considers as the main (principal) components.
        '''
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2).fit(self.feature_vector)
        pca_2d = pca.transform(self.feature_vector)

        return pca_2d

    def fit(self, kernel = 'rbf', random_state = 0):        
        ## Training the SVM classifier
        
        self.clf = svm.SVC(kernel= kernel, random_state = random_state)
        self.clf.fit(self.X_train, self.y_train)
        predicted_labels = self.clf.predict(self.X_test)

        
        print('\n') 
        conf = confusion_matrix(self.y_test, predicted_labels)
        display_cm(conf, self.class_labels, hide_zeros=True)
        print('\nClassification accuracy = %f' % accuracy(conf))

    def model_param_selection(self, C, gamma):
        ## Model parameter selection
        #model selection takes a few minutes, change this variable
        #to true to run the parameter loop    
        C_range = C
        gamma_range = gamma
        
        fig, axes = plt.subplots(3, 2, 
                            sharex='col', sharey='row',figsize=(10,10))
        plot_number = 0
        for outer_ind, gamma_value in enumerate(gamma_range):
            row = int(plot_number / 2)
            column = int(plot_number % 2)
            cv_errors = np.zeros(C_range.shape)
            train_errors = np.zeros(C_range.shape)
            for index, c_value in enumerate(C_range):
                
                clf = svm.SVC(C=c_value, gamma=gamma_value)
                clf.fit(self.X_train,self.y_train)
                
                train_conf = confusion_matrix(self.y_train, clf.predict(self.X_train))
                cv_conf = confusion_matrix(self.y_test, clf.predict(self.X_test))
            
                cv_errors[index] = accuracy(cv_conf)
                train_errors[index] = accuracy(train_conf)

            ax = axes[row, column]
            ax.set_title('Gamma = %g'%gamma_value)
            ax.semilogx(C_range, cv_errors, label='CV error')
            ax.semilogx(C_range, train_errors, label='Train error')
            plot_number += 1
            ax.set_ylim([0.2,1])
            
        ax.legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
        fig.text(0.5, 0.03, 'C value', ha='center',
                fontsize=14)
                
        fig.text(0.04, 0.5, 'Classification Accuracy', va='center', 
                rotation='vertical', fontsize=14)

        plt.show()

    def fit_with_selected_model_param(self, C, gamma, kernel = 'rbf', random_state = 0):

        self.clf = svm.SVC(C=10, gamma=1, kernel = kernel, random_state= random_state)        
        self.clf.fit(self.X_train, self.y_train)

        print('\n')
        cv_conf = confusion_matrix(self.y_test, self.clf.predict(self.X_test))
        display_cm(cv_conf, self.class_labels, 
            display_metrics=True, hide_zeros=True)
        print('\nOptimized signal classification accuracy = %.2f' % accuracy(cv_conf))

