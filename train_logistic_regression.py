# -*- coding: utf-8 -*-
"""train logistic regression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ts4yZk2gtirMzxPnk8XKji5XIjw0HyA-
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchtext.data as data
import torchtext
import time
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from scipy import sparse
import pandas as pd
import seaborn as sn
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix
import xgboost as xgb
import sys
# from cStringIO import StringIO

# from google.colab import drive
# drive.mount('/content/gdrive',force_remount=True)
train_csv_file = "snli_1.0_train.csv"
test_csv_file = 'snli_1.0_test.csv' 
dev_csv_file = 'snli_1.0_dev.csv'

PATH = "/content/gdrive/My Drive/DL assignment 3/"
train_path = PATH + train_csv_file 
test_path = PATH + test_csv_file
dev_path = PATH + dev_csv_file

#Hyperparams for Logistic Regression model
# c_space = np.logspace(-5,2,50)
c_space = [2]
rand_state_space = [0]
class_weight_space = ['balanced',None]
penalty_space = ['l1']
solver_space = ['saga']
max_iter_space = [100]

# C_Logistic = 2
# RANDOM_STATE = 0
# CLASS_WEIGHT = 'balanced'

def preprocess(df):
  # df - dataframe
  # Return preprocessed dataframe
  df = df.dropna(subset=['gold_label','sentence1','sentence2'])
  # df = df[df['gold_label'] != '-']
  label2index = {'neutral':0, 'entailment':1,'contradiction':2,'-':3}
  df['gold_label'] = df['gold_label'].map(label2index)
  return df

def get_X(df,vect_word):
  # df - dataframe
  # Return the x value to be given as input to logistic regression model
  premise = vect_word[0].transform(df['sentence1'])
  hypothesis = vect_word[1].transform(df['sentence2'])
  X = sparse.hstack([premise,hypothesis])
  return X

def calc_accuracy(pred, df):
  # pred - list of predicted values
  # df - dataframe
  # Return accuracy
  predicted = sum(pred == df['gold_label'])
  total = len(df['gold_label'])
  accuracy = predicted/total * 100.
  return accuracy

def confusion_matrix(pred, df):
  # Return heat map of confusion matrix
  labels = ['neutral', 'entailment','contradiction']
  cnf_matrix = confusion_matrix(df['gold_label'].to_list(),pred)
  # return cnf_matrix
  df_cm = pd.DataFrame(cnf_matrix, index = labels, columns= labels)
  return sn.heatmap(df_cm,annot=True,fmt='g')

def fitVectorizer(df):
  #initialise the tf-idf vectorizer
  prem_vect_word = TfidfVectorizer(use_idf=True,lowercase=True,analyzer='word',stop_words='english')
  hyp_vect_word = TfidfVectorizer(use_idf=True,lowercase=True,analyzer='word',stop_words='english')
  # for the tf-idf vectorizer fit all sentences in both premise and hypothesis
  # vect_word = vect_word.fit(iter( [text for sentence in [df['sentence1'],df['sentence2']] for text in sentence ] ) )
  prem_vect_word = prem_vect_word.fit(df['sentence1'])
  hyp_vect_word = hyp_vect_word.fit(df['sentence2'])
  return [prem_vect_word, hyp_vect_word]

def trainLogisticModel(df,vect_word):
  # train_df = preprocess(train_df)
  # vect_word = fitVectorizer(train_df)
  X = get_X(df,vect_word)
  lr = LogisticRegression(multi_class='multinomial')#C=2,penalty='l1',solver='saga',random_state=0)
  # lr = SGDClassifier(loss= 'log', penalty= 'l1')
  # lr = xgb.XGBClassifier(objective='multinomial:logistic')
  # xg_param_grid = {'learning_rate':[0.1],'reg_alpha':[1,2]}
  # param_grid = {
  #               'C' : c_space, 
  #               'random_state' : rand_state_space,
  #               'class_weight' : class_weight_space,
  #               'penalty' : penalty_space ,
  #               'solver' : solver_space, 
  #               'max_iter' : max_iter_space,
  # }
  # cv = [(slice(None),slice(None))]      #to get rid of cross validation
  # lr_cv = GridSearchCV(lr,param_grid, cv = cv, n_jobs = -1, scoring = 'accuracy')
  # old_stdout = sys.stdout
  # mystdout = sys.stdout = StringIO()

  lr.fit(X,df['gold_label'])

  #plotting loss vs iterations
  # clf = SGDClassifier(**kwargs, verbose=1)
  # clf.fit(X_tr, y_tr)
  # sys.stdout = old_stdout
  # loss_history = mystdout.getvalue()
  # loss_list = []
  # for line in loss_history.split('\n'):
  #     if(len(line.split("loss: ")) == 1):
  #         continue
  #     loss_list.append(float(line.split("loss: ")[-1]))
  # plt.figure()
  # plt.plot(np.arange(len(loss_list)), loss_list)
  # plt.savefig("Logistic Reg Loss vs Iterations.png")
  # plt.xlabel("Time in epochs")
  # plt.ylabel("Loss")
  # plt.show()
  # plt.close()

  return lr

def testModel(df, lr, vect_word):
  # df = preprocess(df)
  X = get_X(df,vect_word)
  predicted = lr.predict(X)
  return calc_accuracy(predicted,df)#, confusion_matrix(predicted,df)

train_df = pd.read_csv(train_path)
train_df = preprocess(train_df)
vect_word = fitVectorizer(train_df)
lr = trainLogisticModel(train_df,vect_word)
# results = pd.DataFrame.from_dict(lr.cv_results_)
# results

accuracy= testModel(train_df,lr,vect_word) #, cnf_matrix 
print(accuracy)
# print(cnf_matrix)

test_df = pd.read_csv(test_path)
test_df_1 = preprocess(test_df)
accuracy= testModel(test_df_1,lr,vect_word) #, cnf_matrix
print(accuracy)
# print(cnf_matrix)

def print_labels(df,lr,vect_word):
  with open('tfidf.txt','w') as f:
    X = get_X(df,vect_word)
    predicted = lr.predict(X)
    index2label = ['neutral', 'entailment','contradiction']
    for label in predicted:
      f.write(index2label[label]+"\n")

import pickle
pickle.dump(lr,open("model/logistic_model.sav",'wb'))
pickle.dump(vect_word,open("model/logistic_vect_word.sav","wb"))

lr = pickle.load(open("model/logistic_model.sav","rb"))
vect_word = pickle.load(open("model/logistic_vect_word.sav","rb"))
print_labels(test_df,lr,vect_word)