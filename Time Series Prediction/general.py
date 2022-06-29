# -*- coding: utf-8 -*-
"""General.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OSAJIK2-RG09WstH90W_1hgc6Cb-LGrN
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import string
import re #regular expressions
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA

from scipy.stats import multivariate_normal as mvn

def accuracy(y,y_hat):
  return np.mean(y==y_hat)

def R2(y, y_hat):
  return (1 - (np.sum((y - y_hat)**2) / np.sum((y - np.mean(y))**2)))

def coinFlip(y):
  y_hat = np.zeros(len(y))

  for i in range(len(y)):
    flip = np.random.randn(1)
    if flip > 0:
      y_hat[i] = 1
  
  return y_hat

def OLS(y, y_hat):
  return (1/(2*len(y))) * np.sum((y-y_hat)**2)

def derivative(Z, a):
  if a == linear:
    return 1
  elif a == sigmoid:
    return Z * (1-Z)
  elif a == relu:
    return (Z>0).astype(int)
  elif a == np.tanh:
    return 1-Z*Z
  else:
    ValueError("Unknown Activation Function")

def sigmoid(h):
  return 1 / (1 + np.exp(-h))

def linear(H):
  return H

def softmax(H):
  eH = np.exp(H)
  return eH/eH.sum(axis=1, keepdims=True)

def bin_cross_entropy(y, p_hat):
  return -(1 / len(y)) * np.sum(y * np.log(p_hat) + (1-y)*np.log(1-p_hat))

def cross_entropy(y, p_hat):
  return -(1 / len(y)) * np.sum(np.sum(y * np.log(p_hat), axis=1), axis=0)

def one_hot(y,binary):
  if binary:
    return y
  else:
    N = len(y)
    K = len(set(y))
    Y = np.zeros((N,K))
    for i in range(N):
      Y[i, y[i]] = 1
  
    return Y

def relu(H):
  return H*(H>0)

class contValData():
  #Set the random seed
  def random_seed(rseed):
    np.random.seed(rseed)

  def create(self, D, N, r=20):
    self.x = np.linspace(0, r, N).reshape(N, D)
    self.y = np.sqrt(self.x) + np.exp(-(self.x-5)**2) - 2*(np.exp(-(self.x-12.5)**2) + np.random.randn(N,1)*0.2)
    return self.x, self.y

  def show(self):
    plt.figure(figsize=(10,7))
    plt.scatter(self.x, self.y)

def confusionMatrix(actual, predicted):

    # extract the different classes
    classes = np.unique(actual)

    # initialize the confusion matrix
    confmat = np.zeros((len(classes), len(classes)))

    # loop across the different combinations of actual / predicted classes
    for i in range(len(classes)):
        for j in range(len(classes)):

           # count the number of instances in each combination of actual / predicted classes
           confmat[i, j] = np.sum((actual == classes[i]) & (predicted == classes[j]))

    return confmat

class KNNClassifier():
  def fit(self, x, y):
    self.x = x
    self.y = y

  def predict(self, x, k, epsilon=1e-3):
    N = len(x)  #Number of rows
    y_hat = np.zeros(N)

    for i in range(N):
      dist_sqr = np.sum((self.x - x[i])**2, axis=1) #Get the squared distance of each point
      idxt = np.argsort(dist_sqr)[:k] #Get the indexes of the K nearest neighbors
      gamma_k = 1 / (np.sqrt(dist_sqr[idxt]+epsilon)) #Get the weights

      y_hat[i] = np.bincount(self.y[idxt], weights=gamma_k).argmax()

    return y_hat

class GaussNB():
  def fit(self, x, y, epsilon=1e-3):
    self.likelihoods = dict()
    self.priors = dict()

    #Determine your classes
    self.K = set(y.astype(int))

    #Assign the x values to every given class
    for k in self.K:
      x_k = x[y==k,:]

      #Populate likelihoods
      self.likelihoods[k] = {"Mean" : x_k.mean(axis=0),
                             "Covariance" : x_k.var(axis=0) + epsilon}
      #populate priors (probability of x given y)
      self.priors[k] = len(x_k) / len(x)
    
  def predict(self, x):
    #Get number and dimension of observations
    N, D = x.shape

    #Get the predicted probability for every observation
    p_hat = np.zeros((N,len(self.K)))

    for k,l in self.likelihoods.items():
      p_hat[:,k] = mvn.logpdf(x, l['Mean'], l['Covariance']) + np.log(self.priors[k])

    return p_hat.argmax(axis=1)

class GaussBayes():
  def fit(self, x, y, epsilon=1e-3):
    self.likelihoods = dict()
    self.priors = dict()
    self.K = set(y.astype(int))

    #Set the covariance matrix
    for k in self.K:
      x_k = x[y==k,:]
      N_k, D = x_k.shape
      mu_k = x_k.mean(axis=0)
      
      self.likelihoods[k] = {'Mean' : mu_k,
                             'Covariance' : (1/(N_k-1)) * np.matmul((x_k - mu_k).T, x_k-mu_k) + epsilon*np.identity(D)}
      self.priors[k] = len(x_k) / len(x)

  def predict(self, x):
    #Get number and dimension of observations
    N, D = x.shape

    #Get the predicted probability for every observation
    p_hat = np.zeros((N,len(self.K)))

    for k,l in self.likelihoods.items():
      p_hat[:,k] = mvn.logpdf(x, l['Mean'], l['Covariance']) + np.log(self.priors[k])

    return p_hat.argmax(axis=1)

class KNNRegressor():
  def fit(self,x,y):
    self.x = x
    self.y = y

  def predict(self, x, K):
    N = len(x)
    y_hat = np.zeros(N)

    for i in range(N):
      dist2 = np.sum((self.x-x[i])**2, axis=1)
      idxt = np.argsort(dist2)[:K]
      gamma_K = np.exp(-dist2[idxt]) / np.exp(-dist2[idxt]).sum()
      y_hat[i] = gamma_K.dot(self.y[idxt])

    return y_hat

class SimpleLinearReg():
  def fit(self, x, y):
    self.y = y
    
    self.d = np.mean(x**2) - np.mean(x)**2  #Denominator for getting w0 and w1
    self.w0 = ((np.mean(y) * np.mean(x**2)) - (np.mean(x) * np.mean(x*y))) / self.d
    self.w1 = (np.mean(x*y) - (np.mean(x) * np.mean(y))) / self.d

  def predict(self, x, y, show=0):
    y_hat = self.w0 + (self.w1 * x)

    if show:
      plt.figure(figsize=(10,7))
      plt.scatter(x, y, s=8)
      plt.plot(x, y_hat, color='#FF0000')

    return y_hat

class MultipleLinearRegression():
  def fit(self, x, y):
    self.w = np.linalg.solve(x.T @ x, x.T @ y)

  def predict(self, x):
    return np.matmul(x, self.w)

class OurLinearRegression():
  def fit(self, x, y, eta=1e-3, epochs=1e3, show_curve=False):
    epochs = int(epochs)
    N, D = x.shape
    y = y

    #Stochastic initialization of weights
    self.W = np.random.randn(D)

    J = np.zeros(epochs)

    #Gradient descent for weight calculation
    for epoch in range(epochs):
      y_hat = self.predict(x)
      J[epoch] = OLS(y, y_hat, N) #Error calculation
      self.W -= eta*(1/N)*(x.T@(y_hat-y)) #Weight update rule

    if show_curve:
      plt.figure(figsize=(10,7))
      plt.plot(J)
      plt.xlabel('Epochs')
      plt.ylabel('$\mathcal{J}$')
      plt.title('Training Curve')
  
  def predict(self, x):
    return x@self.W

class SimpleLogisticRegression():
  def __init__(self, thresh=0.5):
    self.thresh = thresh
    self.W = None
    self.b = None

  def fit(self, x, y, lr=1e-3, epochs=1e3, show_curve=False):
    epochs = int(epochs)
    N, D = x.shape

    #Randomly initialize weights and bias
    self.W = np.random.randn(D)
    self.b = np.random.randn(1)

    #Initialize the loss function values
    J = np.zeros(epochs)

    for epoch in range(epochs):
      #Calculate the probability with forward propagation
      p_hat = self.__forward__(x)
      J[epoch] = bin_cross_entropy(y, p_hat)

      #Update the weights and bias through backpropagation
      self.W -= lr * (1/N) * x.T @ (p_hat-y)
      self.b -= lr * (1/N) * np.sum(p_hat-y)

    if show_curve:
      plt.figure(figsize=(10,7))
      plt.plot(J)
      plt.xlabel('epochs')
      plt.ylabel('Loss $\mathcal{J}$')
      plt.title('Training Curve')

  def __forward__(self, x):
    return sigmoid(x @ self.W + self.b)

  def predict(self, x):
    return (self.__forward__(x) >= self.thresh).astype(np.int32)

class MVLogisticRegression():
  def __init__(self, thresh=0.5):
    self.thresh = thresh

  def fit(self, x, y, lr=1e-3, epochs=1e3, show_curve=False):
    epochs = int(epochs)
    N, D = x.shape
    K = len(np.unique(y)) #Number of classes
    y_values = np.unique(y, return_index=False)
    Y = one_hot(y, K).astype(int) #Encode each output with one-hot vectors

    #Stochastic initialization of weights and biases
    self.W = np.random.randn(D, K)
    self.b = np.random.randn(N, K)

    J = np.zeros(epochs)

    #Gradient descent
    for epoch in range(epochs):
      p_hat = self.__forward__(x)
      J[epoch] = cross_entropy(Y, p_hat)

      #Update weights and bias
      self.W -= lr * (1/N) * x.T @ (p_hat - Y)
      self.b -= lr * (1/N) * np.sum(p_hat-Y, axis=0)

    if show_curve:
      plt.figure(figsize=(10,7))
      plt.plot(J)
      plt.xlabel('epochs')
      plt.ylabel('Loss $\mathcal{J}$')
      plt.title('Training Curve')

  def __forward__(self, x):
    return softmax(x @ self.W + self.b)

  def predict(self, x):
    return np.argmax(self.__forward__(x), axis=1)

class Shallow_ANN():
  def fit(self, X, y, neurons=10, lr=1e-3, epochs=1e3, show_curve=False):
    epochs = int(epochs)
    Y = one_hot(y)

    N, D = X.shape
    K = Y.shape[1]

    #Initialize the weights
    self.W = {l: np.random.randn(M[0],M[1]) for l,M in enumerate(zip([D,neurons], [neurons,K]), 1)}
    self.b = {l: np.random.randn(M) for l,M in enumerate([neurons,K], 1)}

    self.a = {1:np.tanh, 2:softmax}

    J = np.zeros(epochs)

    for epoch in range(epochs):
      self.__forward__(X)
      J[epoch] = cross_entropy(Y, self.Z[2])

      #Weight update
      self.W[2] -= lr* (1/N) * self.Z[1].T @ (self.Z[2] - Y)
      self.W[1] -=lr* (1/N) * X.T @ ((self.Z[2] - Y) @ self.W[2].T * (1 - self.Z[1]**2))

      #Bias update
      self.b[2] -= lr * (1/N) * (self.Z[2] - Y).sum(axis=0)
      self.b[1] -= lr * (1/N) * ((self.Z[2] - Y) @ self.W[2].T * (1 - self.Z[1]**2)).sum(axis=0)

    if show_curve:
      plt.figure(figsize=(10,7))
      plt.plot(J)
      plt.xlabel('epochs')
      plt.ylabel('Loss $\mathcal{J}$')
      plt.title('Training Curve')

  def __forward__(self, X):
    self.Z = {0:X}

    for l in sorted(self.W.keys()):
      self.Z[l] = self.a[l](self.Z[l-1]@self.W[l]+self.b[l])

  def predict(self, X):
    self.__forward__(X)
    return self.Z[2].argmax(axis=1)

class ANN():
  def __init__(self, architecture, activations=None, mode=0):
    self.mode = mode
    self.architecture = architecture
    self.activations = activations
    self.L = len(architecture) + 1

  def fit(self, x, y, lr=1e-3, epochs=1e3, show_curve=False, binary=False):
    epochs = int(epochs)

    #Regression
    if self.mode:
      y = y
    #Classification
    else:
      y = one_hot(y,binary)

    N, D = x.shape
    if binary:
      K = 1
    else:
      K = y.shape[1]

    #Initialize weights and bias
    self.W = {l: np.random.randn(M[0],M[1]) for l,M in
              enumerate(zip(([D]+self.architecture),(self.architecture+[K])),1)}
    self.b = {l: np.random.randn(M) for l,M in enumerate(self.architecture+[K],1)}

    #Load activation functions
    if self.activations is None:
      self.a = {l:relu for l in range(1,self.L)}
    else:
      self.a = {l:act for l,act in enumerate(self.activations,1)}

    #Set mode
    if self.mode:
      self.a[self.L] = linear
    else:
      if binary:
        self.a[self.L] = sigmoid  #Change into sigmoid for binary classification
      else:
        self.a[self.L] = softmax

    J = np.zeros(epochs)

    for epoch in range(epochs):
      #Forward propagation
      self.__forward__(x)

      if self.mode:
        J[epoch] = OLS(y, self.Z[self.L])
      else:
        if binary:
          J[epoch] = bin_cross_entropy(y, self.Z[self.L])
        else:
          J[epoch] = cross_entropy(y, self.Z[self.L])

      #Backpropagation
      dH = (1/N) * (self.Z[self.L]-y)

      for l in sorted(self.W.keys(), reverse=True):
        dW = self.Z[l-1].T @ dH
        db = dH.sum(axis=0)

        if binary:
          self.W[l] = self.W[l] - lr * dW
          self.b[l] = self.b[l] - lr * db
        else:
          self.W[l] -= lr * dW
          self.b[l] -= lr * db

        if l > 1:
          dZ = dH @ self.W[l].T
          dH = dZ * derivative(self.Z[l-1], self.a[l-1])

    if show_curve:
      plt.figure(figsize=(10,7))
      plt.plot(J)
      plt.xlabel('epochs')
      plt.ylabel('Loss $\mathcal{J}$')
      plt.title('Training Curve')

  def __forward__(self, x):
    self.Z = {0:x}

    for l in sorted(self.W.keys()):
      self.Z[l] = self.a[l](self.Z[l-1]@self.W[l]+self.b[l])

  def predict(self, x):
    self.__forward__(x)

    if self.mode:
      return self.Z[self.L]
    else:
      return self.Z[self.L].argmax(axis=1)

def preprocess(sentence,lemma=True):
  #Remove url links
  proc_sent = re.sub(r'https?:\/\/.*[\r\n]*','',sentence)

  #Delete non-ASCII values
  proc_sent = str(proc_sent.encode("ascii","ignore"))[1:]

  #Remove punctuation
  proc_sent = ''.join([char for char in proc_sent if char not in string.punctuation])

  #Parse to lower case
  proc_sent = proc_sent.lower()

  #Tokenize and remove stop words
  stop_words = stopwords.words('english')
  proc_sent = word_tokenize(proc_sent)
  proc_sent = [word for word in proc_sent if word not in stop_words]

  #Remove single letters
  proc_sent = [word for word in proc_sent if len(word) != 1]

  #Stem or lemmatize (just 1)
  if lemma:
    lemmatizer = WordNetLemmatizer()
    proc_sent = [lemmatizer.lemmatize(word) for word in proc_sent]
  else:
    porter = PorterStemmer()
    proc_sent = [porter.stem(word) for word in proc_sent] #Stemming

  return proc_sent

def distance(X, means, *args, **kwargs):
  diff = []
  dists = []

  for mean in means:
    diff = X - mean
    dist = np.sqrt(np.sum(diff**2, axis=1, keepdims=True))
    dists.append(dist)

  return np.hstack(dists)

def Responsibility(X,means,beta=1e-3,*args,**kwargs):
  diff = []
  responsibilities = []

  for mean in means:
    diff = X - mean
    dist = (np.sum(diff ** 2, axis=1, keepdims=True))

    numerator = np.exp(-(beta*dist))
    denominator = np.sum(numerator)
    responsibility = -numerator / denominator

    responsibilities.append(responsibility)
    
  return np.hstack(responsibilities)

class K_Means:
  def __init__(self, k=3, distance_func=distance, beta=None):
    self.k = k
    self.distance_func = distance_func
    self.beta = beta

  def fit(self,X,iterations=5, show_figure=False):
    indices = np.arange(X.shape[0])
    sample_indices = np.random.choice(indices,size=self.k,replace=False)
    self.means = X[sample_indices]

    for i in range(iterations):
      y_hat = self.Predict(X)
      self.means = []

      for j in range(self.k):
        mean = np.mean(X[y_hat==j], axis=0)
        self.means.append(mean)
      self.means=np.vstack(self.means)

    y_hat = self.Predict(X)

    if show_figure:
      plt.figure(figsize=(10,7))
      plt.scatter(X[:,0],X[:,1],s=1,c=y_hat)
      plt.scatter(self.means[:,0],self.means[:,1], c='k',s=10)

    return y_hat
  
  def Predict(self,X):
    dist = self.distance_func(X,self.means,self.beta)
    y_hat = np.argmin(dist,axis=1)
    return y_hat

def distance(X, means, *args, **kwargs):
  diff = []
  dists = []

  for mean in means:
    diff = X - mean
    dist = np.sqrt(np.sum(diff**2, axis=1, keepdims=True))
    dists.append(dist)

  return np.hstack(dists)

def Responsibility(X,means,beta=1e-3,*args,**kwargs):
  diff = []
  responsibilities = []

  for mean in means:
    diff = X - mean
    dist = (np.sum(diff ** 2, axis=1, keepdims=True))

    numerator = np.exp(-(beta*dist))
    denominator = np.sum(numerator)
    responsibility = -numerator / denominator

    responsibilities.append(responsibility)
    
  return np.hstack(responsibilities)

class K_Means:
  def __init__(self, k=3, distance_func=distance, beta=None):
    self.k = k
    self.distance_func = distance_func
    self.beta = beta

  def fit(self,X,iterations=5,show_figure=False):
    indices = np.arange(X.shape[0])
    sample_indices = np.random.choice(indices,size=self.k,replace=False)
    self.means = X[sample_indices]

    for i in range(iterations):
      y_hat = self.Predict(X)
      self.means = []

      for j in range(self.k):
        mean = np.mean(X[y_hat==j], axis=0)
        self.means.append(mean)
      self.means=np.vstack(self.means)

    y_hat = self.Predict(X)

    if show_figure:
      plt.figure(figsize=(10,7))
      plt.scatter(X[:,0],X[:,1],s=1,c=y_hat)
      plt.scatter(self.means[:,0],self.means[:,1], c='k',s=10)

    return y_hat
  
  def Predict(self,X):
    dist = self.distance_func(X,self.means,self.beta)
    y_hat = np.argmin(dist,axis=1)
    return y_hat

def logTransform(data, ts):
  return data[ts].apply(lambda x:np.log(x))

def plot_decomposition(data, ts, trend, seasonal, residual):
  fig, ((ax1,ax2), (ax3,ax4)) = plt.subplots(2,2, figsize=(15,5), sharex=True)

  ax1.plot(data[ts], label='Original')
  ax1.legend(loc='best')
  ax1.tick_params(axis='x', rotation=45)

  ax2.plot(data[trend], label='Trend')
  ax2.legend(loc='best')
  ax2.tick_params(axis='x', rotation=45)

  ax3.plot(data[seasonal], label='Seasonal')
  ax3.legend(loc='best')
  ax3.tick_params(axis='x', rotation=45)

  ax4.plot(data[residual], label='Residual')
  ax4.legend(loc='best')
  ax4.tick_params(axis='x', rotation=45)

  plt.tight_layout()
  plt.show()

def test_stationarity(data, ts):
  rolmean = data[ts].rolling(window=12, center=False).mean()
  rolstd = data[ts].rolling(window=12, center=False).std()

  orig = plt.plot(data[ts], color='blue', label='Original')
  mean = plt.plot(rolmean, color='red', label='Rolling Mean')
  std_dev = plt.plot(rolstd, color='black', label='Rolling Std. Dev.')

  plt.legend(loc='best')
  plt.title(f"Rolling Mean and Std. Deviation for {ts}")
  plt.xticks(rotation=45)
  plt.show(block=False)
  plt.close

  print("%%% Results %%%")
  dftest = adfuller(data[ts], autolag='AIC')
  dfoutput = pd.Series(dftest[0:4], index=["Test Statistic", "p_value", "# Lags used", "Number of Observations"])

  for key,value in dftest[4].items():
    dfoutput[f'Critical Value({key})'] = value
  print(dfoutput)

def runArima(data, ts, p, d, q):
  model = ARIMA(data[ts], order=(p,d,q))
  results = model.fit(disp=-1)

  len_res = len(results.fittedvalues)
  ts_modified = data[ts][-len_res:]

  rss = sum((results.fittedvalues - ts_modified)**2)
  rmse = np.sqrt(rss/len(data[ts]))
  print(f"RMSE: {rmse}")

  plt.figure()
  plt.plot(data[ts])
  plt.plot(results.fittedvalues, color='red')
  plt.show()

  return results