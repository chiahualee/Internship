
# coding: utf-8

# ### Data Extraction

# In[1]:


import os
rootdir = "/home/chiahual/emails_enron"

for directories, subdirs, files in os.walk(rootdir):
    print(directories, subdirs, len(files))


# In[2]:


for directories, subdirs, files in os.walk(rootdir):
    if (os.path.split(directories)[1]  == 'ham'):
        print(directories, subdirs, len(files))
    
    if (os.path.split(directories)[1]  == 'spam'):
        print(directories, subdirs, len(files))


# ### Data Preprocessing

# In[3]:


import re
import string
ham_list = []
spam_list = []


for directories, subdirs, files in os.walk(rootdir):
    for filename in files: 
        with open(os.path.join(directories, filename), encoding="latin-1") as f:
            corpus_text = f.read()
            for c in string.punctuation:
                corpus_text = corpus_text.replace(c, "")  # -- (1) remove all punctuations

            text = re.sub(r'\S*\d\S*','',corpus_text) # -- (2) replace words with digits to with empty string e.g. v3
            text = re.sub(r'[^\w\s]','',text)         # -- (3) replace anything that is not a word character or whitespace character with empty string                                                
            text = text.lower()
            text = text.lower().split()           # -- (4) remove next line characters(\n)     

            li = []
            for token in text:
                li.append(token)
            if (os.path.split(directories)[1]  == 'ham'):
                ham_list.append(" ".join(li))
            else:
                spam_list.append(" ".join(li))                
                


# In[4]:


print("len(ham_list): " + str(len(ham_list)),"len(spam_list): " + str(len(spam_list)))


# In[5]:


email_list=ham_list+spam_list
email_label=[0]*len(ham_list)+[1]*len(spam_list)


# In[6]:


# %%time
from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(min_df=50,max_df=0.8,stop_words="english")
X=vectorizer.fit_transform(email_list)


# In[7]:


len(vectorizer.vocabulary_)


# In[8]:


X.shape


# In[9]:


import math
import numpy as np
folds = 10 
one_portion = math.floor(len(email_list)/(folds+1))

indices = np.random.permutation(np.arange(len(email_list)))
training_idx, test_idx = indices[:one_portion*10],indices[one_portion*10:]


# ### Training & Validation Stage

# In[10]:


import time
start_time = time.time()

from sklearn.model_selection import KFold
from sklearn.naive_bayes import BernoulliNB
lowest_cross_val_error_BNB = np.inf
best_alpha = None


alpha_values=[1, 0.9, 0.8, 0.7, 0.6]

kf = KFold(n_splits=10, shuffle=True, random_state=9999999)


for alpha in alpha_values:
    errors_BNB = []
    for train_indices, val_indices in kf.split(training_idx):
        
        #BernoulliNB
        clf = BernoulliNB(alpha=alpha)
        clf.fit(X[train_indices], np.array(email_label)[train_indices])
        predicted_val_labels_BNB = clf.predict(X[val_indices])
        error_BNB = np.mean(predicted_val_labels_BNB != np.array(email_label)[val_indices])
        errors_BNB.append(error_BNB)
        

  
    cross_val_error_BNB = np.mean(errors_BNB)

#     print('alpha:', alpha, 'cross validation error:', cross_val_error_BNB)
 
    if cross_val_error_BNB < lowest_cross_val_error_BNB:
        lowest_cross_val_error_BNB = cross_val_error_BNB
        best_alpha = alpha

print('Best alpha:', best_alpha, 'accuracy', 1-lowest_cross_val_error_BNB)
print("--- %s seconds --- for naive bayes" % (time.time() - start_time))


# In[11]:


import time
start_time = time.time()
from sklearn.model_selection import KFold

from sklearn.neighbors import KNeighborsClassifier


lowest_cross_val_error_KNN = np.inf
best_k = None

k_values=[5, 20, 60, 80, 100]


kf = KFold(n_splits=10, shuffle=True, random_state=9999999)


for k in k_values:
    errors_KNN = []

    for train_indices, val_indices in kf.split(training_idx):
        
        #KNN
        neigh = KNeighborsClassifier(n_neighbors=k)
        neigh.fit(X[train_indices], np.array(email_label)[train_indices]) 
        predicted_val_labels_KNN = neigh.predict(X[val_indices])
        error_KNN = np.mean(predicted_val_labels_KNN != np.array(email_label)[val_indices])
        errors_KNN.append(error_KNN)
        
     
        
    cross_val_error_KNN = np.mean(errors_KNN)

#     print('k:', k, 'cross validation error:', cross_val_error_KNN)  
  
    if cross_val_error_KNN < lowest_cross_val_error_KNN:
        lowest_cross_val_error_KNN = cross_val_error_KNN
        best_k = k
    
print('Best k:', best_k, 'accuracy', 1-lowest_cross_val_error_KNN)
print("--- %s seconds --- for KNN" % (time.time() - start_time))


# In[14]:


import time
start_time = time.time()
from sklearn.model_selection import KFold
from sklearn.svm import LinearSVC



kf = KFold(n_splits=10, shuffle=True, random_state=9999999)



errors_SVC = []
for train_indices, val_indices in kf.split(training_idx):

    #SVC
    classifier = LinearSVC()
    classifier.fit(X[train_indices],np.array(email_label)[train_indices])
    predicted_val_labels_SVC = classifier.predict(X[val_indices])
    error_SVC = np.mean(predicted_val_labels_SVC != np.array(email_label)[val_indices])
    errors_SVC.append(error_SVC)

cross_val_error_SVC = np.mean(errors_SVC)
# print("cross validation error: ", cross_val_error_SVC)
print( 'accuracy', 1-cross_val_error_SVC)
print("--- %s seconds --- for SVM Linear" % (time.time() - start_time))


# ### Testing Stage

# In[17]:


clf_best = BernoulliNB(alpha=0.7)
clf_best.fit(X[training_idx], np.array(email_label)[training_idx])
predicted_test_labels_BNB = clf_best.predict(X[test_idx])
error = np.mean(predicted_test_labels_BNB != np.array(email_label)[test_idx])
print("Testing Accuracy for Naive Bayes", 1-error)


# In[18]:


neigh_best = KNeighborsClassifier(n_neighbors=k)
neigh_best.fit(X[training_idx], np.array(email_label)[training_idx])
predicted_test_labels_KNN = neigh_best.predict(X[test_idx])
error = np.mean(predicted_test_labels_KNN != np.array(email_label)[test_idx])
print("Testing Accuracy for KNN ", 1-error)


# In[19]:


SVM_best = LinearSVC()
SVM_best.fit(X[training_idx], np.array(email_label)[training_idx])
predicted_test_labels_SVM = SVM_best.predict(X[test_idx])
error = np.mean(predicted_test_labels_SVM != np.array(email_label)[test_idx])
print("Testing Accuracy for SVM Linear", 1-error)

