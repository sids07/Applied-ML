import pandas as pd 
import numpy as np 

from sklearn import ensemble
from sklearn import model_selection
from sklearn import metrics

from functools import partial

import optuna

def optimize(trial,x,y):
    #params = dict(zip(param_names,params))

    # ---

    criterion = trial.suggest_categorical("criterion",['gini','entropy'])
    n_estimators = trial.suggest_int("n_estimators",100,1500)
    max_depth = trial.suggest_int("max_depth",3,15)
    max_features = trial.suggest_uniform('max_features',0.01,1.0)

    model = ensemble.RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        max_features=max_features,
        criterion = criterion,
        )

    kf = model_selection.StratifiedKFold(n_splits=5)
    accuracies =[]
    for idx in kf.split(X=x,y=y):
        train_idx,test_idx = idx[0],idx[1]
        xtrain = x[train_idx]
        ytrain = y[train_idx]

        xtest = x[test_idx]
        ytest = y[test_idx]

        model.fit(xtrain,ytrain)

        pred = model.predict(xtest)

        fold_acc  = metrics.accuracy_score(ytest,pred)

        accuracies.append(fold_acc)
    return -1.0 * np.mean(accuracies)

if __name__ =="__main__":
    df = pd.read_csv('../input/mobile-train.csv')
    X= df.drop("price_range",axis=1).values 
    y = df.price_range.values 
    
    optimization_function = partial(optimize,x=X,y=y)

    study = optuna.create_study(direction='minimize')

    study.optimize(optimization_function,n_trials =15)