# -*- coding: utf-8 -*-
"""sentimentAnalysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zZeIKFjFq3j71i1BtRMw-xf6P9_AZY_r

## Importing Libraries
"""

import nltk
nltk.download('vader_lexicon')

!pip install simpletransformers

!pip install transformers

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

!pip install textblob

from textblob import TextBlob

from nltk.sentiment.vader import SentimentIntensityAnalyzer as sia
from tqdm.notebook import tqdm

"""## **Dataset Cleaning**

Reading CSV File
"""

df = pd.read_csv("/content/raw_data.csv")

df.head()

"""# Checking for null and duplicates

no nulls and duplicates
"""

df.isnull().sum()

df.duplicated().sum()

"""# Removing columns that are not needed"""

df.columns

df = df.drop(["Sno", "Covid", "Description", "Image", "Source"], axis = 1)

df.shape

df.columns

"""cleaned dataset

## VADER model
"""

sid = sia()

"""few examples"""

sid.polarity_scores("i am happy!")

sid.polarity_scores("i am devastated")

""" Polarity scores for dataset"""

#Run the polarity scores on the entire dataset
res = {}
for i, row in tqdm(df.iterrows(), total = len(df)):
  text = row['Headline']
  date = row['Date']
  res[date] = sid.polarity_scores(text)

vaders = pd.DataFrame(res).T
vaders = vaders.reset_index().rename(columns = {'index' : 'Date'})
vaders = vaders.merge(df, how = 'left')

vaders.head()

vaders['compound']

vaders['Sentiment-score'] = vaders['Sentiment'].apply(lambda c : 'pos' if c > 0 else 'neg')
vaders.head()

vaders['Compound-score'] = vaders['compound'].apply(lambda c : 'pos' if c > 0 else 'neg')
vaders.head()

print(confusion_matrix(vaders['Sentiment-score'], vaders['Compound-score']))

# VADER Result
print(classification_report(vaders['Sentiment-score'], vaders['Compound-score']))

accuracy_score(vaders['Sentiment-score'], vaders['Compound-score'])

"""## Roberta Model"""

from google.colab import drive
drive.mount('/content/drive')

train, test = train_test_split(df, test_size = 0.2)

from simpletransformers.classification import ClassificationModel

model = ClassificationModel('roberta', f"cardiffnlp/twitter-roberta-base-sentiment", num_labels = 3, args =
 {
    'reprocess_input_data' : True,
    'overwrite_output_dir' : True
  },
                            use_cuda = False)

trainr_df = pd.DataFrame({'text' : train['Headline'].replace(r'\n', ' ', regex = True), 'label' : train['Sentiment']})
evalr_df = pd.DataFrame({'text' : test['Headline'].replace(r'\n', ' ', regex = True), 'label' : test['Sentiment']})

model.train_model(trainr_df)

result, model_outputs, wrong_predictions = model.eval_model(evalr_df)

result

model_outputs

lst = []
for arr in model_outputs:
  lst.append(np.argmax(arr))

true = evalr_df['label'].tolist()
predicted = lst

import sklearn
mat = sklearn.metrics.confusion_matrix(true, predicted)
mat

#Roberta Result
sklearn.metrics.accuracy_score(true, predicted)

sklearn.metrics.f1_score(true, predicted)

"""## BERT Model"""

# Test and Train the data
train, test = train_test_split(df, test_size = 0.2)

"""Building a model"""

from simpletransformers.classification import ClassificationModel

model = ClassificationModel('bert', 'bert-base-cased', num_labels = 3, args =
 {
    'reprocess_input_data' : True,
    'overwrite_output_dir' : True
  },
                            use_cuda = False)

trainb_df = pd.DataFrame({'text' : train['Headline'].replace(r'\n', ' ', regex = True), 'label' : train['Sentiment']})
evalb_df = pd.DataFrame({'text' : test['Headline'].replace(r'\n', ' ', regex = True), 'label' : test['Sentiment']})

model.train_model(trainb_df)

result, model_outputs, wrong_predictions = model.eval_model(evalb_df)

result

model_outputs

lst = []
for arr in model_outputs:
  lst.append(np.argmax(arr))

true = evalb_df['label'].tolist()
predicted = lst

import sklearn
mat = sklearn.metrics.confusion_matrix(true, predicted)
mat

sklearn.metrics.classification_report(true, predicted, target_names = ['positive', 'negative'])

#BERT Result
sklearn.metrics.accuracy_score(true, predicted)

sklearn.metrics.f1_score(true, predicted)

"""## TextBlob Model"""

df['polarity_score'] = df['Headline'].apply(lambda s: TextBlob(s).sentiment.polarity)
df.head()

import sklearn

df['Sentiment-score'] = df['Sentiment'].apply(lambda c : 'pos' if c > 0 else 'neg')
df.head()

df['polarity-score'] = df['polarity_score'].apply(lambda c : 'pos' if c > 0 else 'neg')
df.head()

print(confusion_matrix(df['Sentiment-score'], df['polarity-score']))

#TextBlob Result
print(classification_report(df['Sentiment-score'], df['polarity-score']))

accuracy_score(df['Sentiment-score'], df['polarity-score'])