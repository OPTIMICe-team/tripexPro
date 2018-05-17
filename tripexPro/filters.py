import numpy as np
import pandas as pd

def removeVelNoiseKa(zeDataFrame, velDataFrame):

    indexNanZe_Ka = np.isnan(np.array(zeDataFrame))
    filteredV_Ka = np.array(velDataFrame)
    filteredV_Ka[indexNanZe_Ka]=np.nan

    dfFilteredVel = pd.DataFrame(columns=zeDataFrame.columns,
                                 index=zeDataFrame.index,
                                 data=filteredV_Ka)
 
    return dfFilteredVel


def removeOutliersZeKa(dataFrameList, variable):
    
    tempDFZe_Ka=dataFrameList[variable.keys().index('Ze_Ka')]
    tempDFZe_Ka[tempDFZe_Ka<-100]=np.nan
    dataFrameList[variable.keys().index('Ze_Ka')] = tempDFZe_Ka
    
    return dataFrameList


def removeClutter(dataFrameList, variable, target, maxHeight):

    tempDFZe_X = dataFrameList[variable.keys().index(target)]

    for col in tempDFZe_X.columns[tempDFZe_X.columns < maxHeight]:
        tempDFZe_X[col] = np.nan
    
    dataFrameList[variable.keys().index(target)] = tempDFZe_X
    
    return dataFrameList


def func(x,a,b):
    
    return np.log(x*b)*a 

def sensitivityFilter(dataFrameList, variable, target, sensPar):

    allZe_DF = dataFrameList[variable.keys().index(target)]
    a = sensPar['a']
    b = sensPar['b']

    for column in allZe_DF.columns:
    
        sens = func(column, a, b)
        allZe_DF[column][allZe_DF[column] < sens] = np.nan
    
    dataFrameList[variable.keys().index(target)] = allZe_DF

    return dataFrameList



