####################
# Project 2 - functions 
# FYS-STK 3155/4155
# Fall 2018 
####################

# Import necessary packages
import numpy as np
from random import random, seed
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge, Lasso, SGDClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from time import time
from imageio import imread
from sklearn.model_selection import train_test_split
from sklearn.utils import safe_indexing, indexable
import pandas as pd
#from plotfunctions import *
import re
from Neural_Network_OneDim import *
from Neural_Network_TwoDim import *
from plotfunctions import *
from mpl_toolkits.axes_grid1 import make_axes_locatable


def OneDimNetwork(X_train, E_train, X_test, E_test, eta):
    weights_output, weights_hidden, bias_output, bias_hidden = Neural_Network_OneDim(X_train, E_train, eta)
    a_h, a_o, Epredict = feed_forward_OneDim(X_test, weights_hidden, bias_hidden,weights_output, bias_output)
    Epredict = Epredict.ravel()
    mse, R2, bias, variance = quality(E_test, Epredict)
    return mse, R2, variance, bias


def OLS(X_train, E_train, X_test, E_test, num_classes, m):
    '''Calculate and return the z and Epredict value by 
    ordinary least squares method'''
    beta = (np.linalg.pinv(X_train.T @ X_train)@ X_train.T @ E_train) 
    Epredict = X_test @ beta
    mse, R2, bias, variance = quality(E_test, Epredict)
    
    return mse, R2, bias, variance, beta


def ridge(X_train, E_train, X_test, E_test, num_classes, m, lambda_value):
    ''' A function that implementes the Rigde method'''

    IX = np.eye(X_train.shape[1])
    beta = (np.linalg.pinv( X_train.T @ X_train + lambda_value*IX) @ X_train.T @ E_train).flatten()
    Epredict =  X_test @ beta
    mse, R2, bias, variance = quality(E_test, Epredict)
    return mse, R2, bias, variance, beta


def lasso(X,z,X_test, E_test, m, lambda_value):
    ''' A function that implements the Lasso method'''

    lasso=Lasso(lambda_value, max_iter=1e7, normalize = True, fit_intercept = False)
    lasso.fit(X,z) 
    beta_lasso = lasso.coef_.T
    predl=lasso.predict(X_test)

    mse, R2, bias, variance = quality(E_test, predl)
    return mse, R2, bias, variance, beta_lasso

def quality(E_test,Epredict):
    '''A function that calculate the mean square error and the R2 score of 
    the values sendt in. If the write value is anything else than zero
    the function will print out the values'''

    # Mean squared error:
    #E_test = E_test.ravel()
    #Epredict = Epredict.ravel()
    print(np.ndim(Epredict), np.shape(Epredict), np.size(E_test))
    mse = (1.0/(np.size(E_test))) *np.sum((E_test - Epredict)**2)
    print("mse: ", mse)
    # Explained R2 score: 1 is perfect prediction 
    R2 = 1- ((np.sum((E_test-Epredict)**2))/(np.sum((E_test-np.mean(E_test))**2)))
    # Bias:
    bias = np.mean((E_test - np.mean(Epredict, axis=0, keepdims=True))**2)
    print('bias:', bias)
    # Variance:
    variance = np.mean(np.var(Epredict, axis=0, keepdims=True))
    
    #covariance = 
    
    #variance = np.mean(Epredict-np.mean(Epredict, keepdims=True))
    print('var:', variance)
    return mse, R2, bias, variance

def bootstrap(x,y):

    indices = np.random.choice(len(y),len(y))
    x_train_new = x[indices]        
    y_train_new = y[indices]
    return x_train_new, y_train_new

 

def ising_energies(states,L):
    """
    This function calculates the energies of the states in the nn Ising Hamiltonian
    """
    J=np.zeros((L,L),)
    for i in range(L):
        J[i,(i+1)%L]-=1.0
    # compute energies
    J_leastsq=np.array(J).reshape((L,L))
    cmap_args=dict(vmin=-1., vmax=1., cmap='seismic')
    fig, axarr = plt.subplots(nrows=1, ncols=1)
    
    im = axarr.imshow(J_leastsq,**cmap_args)
    
    axarr.set_title('J-states',fontsize=16)
    axarr.tick_params(labelsize=16)
    divider = make_axes_locatable(axarr)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    cbar=fig.colorbar(im, cax=cax)

    cbar.ax.set_yticklabels(np.arange(-1.0, 1.0+0.25, 0.25),fontsize=14)
    cbar.set_label('$J_{i,j}$',labelpad=-40, y=1.12,fontsize=16,rotation=0)

    plt.show()

    E = np.einsum('...i,ij,...j->...',states,J,states)
    print(np.shape(E))
    return E 



def OneDim(L, iterations, lambda_values, method):

    n = 10000
    states=np.random.choice([-1, 1], size=(n,L)) # Make 10000 random states.

    X = np.zeros((n,L*L))

    for i in range(n):
        X[i] = np.outer(states[i],states[i]).ravel()
    

    energies=ising_energies(states,L) # Calculate the energies of the states.

    X_train, X_test, E_train, E_test = train_test_split(X, energies, train_size = 0.7)

    mse = np.zeros(iterations)
    r2score = np.zeros(iterations)
    bias = np.zeros(iterations)
    var = np.zeros(iterations)
    beta_list = [] 

    beta= 0
    num_classes = 1
    #OneDimNetwork(X_train, E_train, X_test, E_test)
    file = open('results_OneDim_%s.txt' %method,  'w')
    if method == 'OLS':
        beta= 0
        best_beta = 0
        mse_min = 1000
        r2_for_min_mse = 0

        
        for i in range(iterations):
            X_train, E_train = bootstrap(X_train,E_train)
            print(i)
            mse[i], r2score[i], bias[i], var[i], beta = OLS(X_train,E_train, X_test, E_test, num_classes, method)
            beta_list.append(beta)
            
            if mse[i] < mse_min: 
                mse_min = mse[i]
                r2_for_min_mse = r2score[i]
                iteration_best = i

        mse_average = np.mean(mse)
        r2score_average = np.mean(r2score)
        bias_average = np.mean(bias)    
        var_average = np.mean(var)

        #L = 40
        J_leastsq=np.array(beta).reshape((L,L))
        cmap_args=dict(vmin=-1., vmax=1., cmap='seismic')
        fig, axarr = plt.subplots(nrows=1, ncols=1)
    
        im = axarr.imshow(J_leastsq,**cmap_args)
        axarr.set_title('$\\mathrm{OLS}$',fontsize=16)
        axarr.tick_params(labelsize=16)
        divider = make_axes_locatable(axarr)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        cbar=fig.colorbar(im, cax=cax)

        cbar.ax.set_yticklabels(np.arange(-1.0, 1.0+0.25, 0.25),fontsize=14)
        cbar.set_label('$J_{i,j}$',labelpad=-40, y=1.12,fontsize=16,rotation=0)
        plt.show()

        file.write('MSE_average:        %f \n' %mse_average)
        file.write('R2_score_average:   %f \n' %r2score_average)
        file.write('Bias_average:       %f \n' %bias_average)
        file.write('Variance_average:   %f \n' %var_average)
        file.write('\n') 
        file.write('Min_MSE_value:      %f \n' %mse_min)
        file.write('R2_for_Min_MSE_value:       %f \n' %r2_for_min_mse)
        file.close()

    elif method == 'NN':
        mse_average = []
        r2score_average = []
        bias_average = []    
        var_average = []  

        etas = [1e-9,1e-8,1e-7,1e-6,1e-5,1e-4,1e-3]

        for eta in etas:
            mse, r2_score, bias, var = OneDimNetwork(X_train, E_train, X_test, E_test, eta)
            
            mse_average.append(mse)
            r2score_average.append(np.mean(r2score))
            bias_average.append(bias) 
            var_average.append(var)
            #mse_min.append(mse_min_value)
            #r2_for_min_mse.append(R2_for_Min_MSE_value)
        file.write('Etas: %s' % etas)
        file.write('MSE_average:        %s \n' %mse_average)
        file.write('R2_score_average:   %s \n' %r2score_average)
        file.write('Bias_average:       %s \n' %bias_average)
        file.write('Variance_average:   %s \n' %var_average)
        #file.write('Min_MSE_value:      %s \n' %mse_min)
        #file.write('R2_for_Min_MSE_value:       %f \n' %r2_for_min_mse)
        file.write('\n') 
        file.close()

    else:

        mse_average = []
        r2score_average = []
        bias_average = []    
        var_average = []   
        mse_min = []
        iteration_best = []
        r2_for_min_mse = []

        for l, lambda_value in enumerate(lambda_values):
            print(lambda_values)
            if method == 'Ridge':
                mse_min_value = 1000
                for i in range(iterations):
                    X_train, E_train = bootstrap(X_train,E_train)
                    mse[i], r2score[i], bias[i], var[i], beta = ridge(X_train,E_train,X_test,E_test, num_classes, method, lambda_value)
                    beta_list.append(beta)
                    if mse[i] < mse_min_value: 
                        mse_min_value = mse[i]
                        R2_for_Min_MSE_value = r2score[i]
                        best_beta = beta
                        iteration_best = i
                        #print('mse_min:', mse_min)

            if method == 'Lasso':
                mse_min_value = 1000
                for i in range(iterations):
                    X_train, E_train = bootstrap(X_train,E_train)
                    #print(i)
                    mse[i], r2score[i], bias[i], var[i], beta = lasso(X_train,E_train,X_test,E_test, method, lambda_value)
                    beta_list.append(beta)
                    if mse[i] < mse_min_value: 
                        #print('hei')
                        mse_min_value = mse[i]
                        R2_for_Min_MSE_value = r2score[i]
                        best_beta = beta
                        iteration_best = i
                        #print('mse_min:', mse_min)
            mse_average.append(np.mean(mse))
            r2score_average.append(np.mean(r2score))
            bias_average.append(np.mean(bias)) 
            var_average.append(np.mean(var))
            mse_min.append(mse_min_value)
            r2_for_min_mse.append(R2_for_Min_MSE_value)

        plot_Jstates(beta, method, lambda_value, L)

        file.write('The results from running with lamda = %s \n' % lambda_values)
        file.write('MSE_average:        %s \n' %mse_average)
        file.write('R2_score_average:   %s \n' %r2score_average)
        file.write('Bias_average:       %s \n' %bias_average) 
        file.write('Variance_average:   %s \n' %var_average)
        file.write('Min_MSE_value:      %s \n' %mse_min) 
        file.write('R2_for_Min_MSE_value:       %s \n' %r2_for_min_mse)
        file.write('\n')
        file.close()


    #return mse_average, r2score_average, bias_average, var_average, np.array(beta_list), mse_min, r2_for_min_mse 



def TwoDim(X_train, X_test, Y_train, Y_test, NN, num_classes):


        
    if NN == 'y':
            
        etas = [1e-4,1e-3,1e-2,1e-1,1e0,1e1]
        for eta in etas:
    
            Acc_training, Acc_after_train, Acc_before_train = Neural_Network_TwoDim(X_train, Y_train, X_test, Y_test, eta)
            print("------------------")
            print("The accuracy before the training: ", Acc_before_train)
            print("The accuracy after the training: ", Acc_after_train)
            print("------------------")

            answer = input("Do you want to plot the training accuracies for eta = %1.1e? [y/n]" % eta)
            if answer == 'y':
                
                Plot_Accuracy(Acc_training, eta)

    else:
        etas = [1e-11,1e-10,1e-9,1e-8,1e-7,1e-6,1e-5]
        for eta in etas:

            Niterations = 30
            beta = 1e-6*np.random.randn(1600)
            p1 = 1./(1 + np.exp(-X_test @ beta))
            Error = p1 - Y_test
            Acc_before_train = Accuracy(Error)
            #eta = 0.01
            #batch = 200
            Acc_training = []
            for i in range(Niterations):
                #index = np.random.randint(len(X_train), size = batch)
                p = 1./(1+np.exp(-X_train @ beta)) 
                
                #p = np.choose(Y_train, [p0,p1])
                dC = -X_train.T @ (Y_train - p)# / len(Y_train[index])
                beta = beta - dC*eta # beta is the same as weights in one dim.
                #correct = p >= 0.5
                Error = p - Y_train
                Acc_training.append(Accuracy(Error))
                
            p = 1./(1 + np.exp(-X_test @ beta))
            Error = p - Y_test
            Acc_after_train = Accuracy(Error)
            
            print("------------------")
            print("The accuracy before the training: ", Acc_before_train)
            print("The accuracy after the training: ", Acc_after_train)
            print("------------------")
            
            answer = input("Do you want to plot the training accuracies for eta = %1.1e? [y/n]" % eta)
            
            if answer == 'y':
                
                Plot_Accuracy(Acc_training, eta)


    del X_train, X_test, Y_train, Y_test
        



def Plot_Accuracy(acc, eta): # TO BE REMOVED!

    xaxis = np.linspace(0,len(acc)-1, len(acc))
    plt.plot(xaxis , acc, 'bo', markersize=2, label='Training accuracy')
    plt.title(r"Accuracy for the training on two dimensional Ising-model with $\eta$ = %1.1e" % eta)
    plt.xlabel("Number of iterations")
    plt.ylabel("Percentage of correct predictions")
    plt.legend()
    plt.show()