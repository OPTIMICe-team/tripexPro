import pandas as pd
import numpy as np
from netCDF4 import Dataset
import attenuationLib as attLib

def getCloudNetData(cloudNetFilePath,varName):
    
    
    cloudNetData = Dataset(cloudNetFilePath, 'r')
    height = cloudNetData['height'][:]
    time = cloudNetData['time'][:]
    variableData = cloudNetData[varName][:]

            
    return variableData, height, time
    


def fillGaps(timeRef, originalDF, colName):
    
    # fill the absence of values    
    timeData = originalDF.index
    filledDF = pd.DataFrame(index=timeRef, columns=[colName],
                            data=np.zeros(len(timeRef),np.int)-999)

    for timeId, timeStamp in enumerate(timeData):
    
        try:
            data = originalDF[0][timeStamp]                          
            filledDF[colName][timeStamp:timaData[timeId+1]] = data
    
        except:
            data = originalDF[0][timeStamp]
            filledDF[colName][timeStamp:]=data
    
        #print timeStamp, timeData[timeId+1]
        
    filledDF[filledDF<0]=0
    
    return filledDF


def getRainFlag(cloudNetFilePath, timeRef, colName,
                year, month, day):
    
    cloudNetCateg, heightData, timeData = getCloudNetData(cloudNetFilePath, 'category_bits')

    cloudNetCateg[cloudNetCateg>3]=-1
    cloudNetCateg[cloudNetCateg>0]=1
    cloudNetCateg[cloudNetCateg<0]=0

    timeData = attLib.convCloudTime2HumTime(timeData)

    timeDataCorr = pd.datetime(int(year), int(month), int(day))\
                               + pd.to_timedelta(np.array(timeData),
                               unit='s')

    categDF = pd.DataFrame(index=timeDataCorr,
                           columns=heightData,
                           data=cloudNetCateg)

    flagRain = pd.DataFrame(categDF.sum(axis=1))
    flagRain[flagRain>0]=1

    finalFlagRain = fillGaps(timeRef, flagRain, 'rainFlag')
    
    return finalFlagRain
    

def getHatProData(hatproFilePath,varName):
    
    cloudNetData = Dataset(hatproFilePath, 'r')
    
    units = getattr(cloudNetData.variables['time'],'units').split(' ')
    epoch = pd.to_datetime(' '.join([units[-3], units[-2]]))
    
    time = cloudNetData['time'][:]
    variableData = cloudNetData[varName][:]
    humanTime = epoch + pd.to_timedelta(time, unit='S' )
    
    return variableData, humanTime


def getLwpFlag(lwpFilePath, timeRef, colName,
               year, month, day):

    hatproLwp, timeData = getHatProData(lwpFilePath, 'clwvi')
    lwpDF = pd.DataFrame(index=timeData, data=hatproLwp*1000.)
    
    lwpDF['times']=timeData
    lwpDF=lwpDF.drop_duplicates(subset=['times'])
    del lwpDF['times']
    
    lwpDF = lwpDF.dropna(how='any')
    lwpDF[lwpDF <= 200] = 0
    lwpDF[lwpDF > 200] = 1

    finalFlagLwp= fillGaps(timeRef, lwpDF, colName)

    return finalFlagLwp


#def getLwpFlag(cloudNetFilePath, timeRef, colName, 
               #year, month, day):
    
#    cloudNetLwp, heightData, timeData = getCloudNetData(cloudNetFilePath, 'lwp')
#    timeData = attLib.convCloudTime2HumTime(timeData)
#    timeDataCorr = pd.datetime(int(year), int(month), int(day))\
               #                + pd.to_timedelta(np.array(timeData),
               #                unit='s')

#    lwpDF = pd.DataFrame(index=timeDataCorr, data=cloudNetLwp)
#    lwpDF = lwpDF.dropna(how='any')
#    lwpDF[lwpDF <= 200] = 0
#    lwpDF[lwpDF > 200] = 1
    
#    finalFlagLwp= fillGaps(timeRef, lwpDF, 'lwpFlag')
    
#    return finalFlagLwp


def getFlag(dataFrame, criteria): 

   dataFrame[np.isnan(dataFrame)==True]=0
   dataFrameFlag = dataFrame.copy()
   dataFrameAna = dataFrame.copy()
   dataFrameFlag[dataFrameAna >= criteria]=0
   dataFrameFlag[dataFrameAna < criteria]=1

   return dataFrameFlag



def getUnifiedFlag(rainFlagDF, lwpFlagDF,
                   corrFlagDF, pointFlagDF):

   rainFlag = rainFlagDF.loc[:,rainFlagDF.columns==100]
   rainFlag = np.array(rainFlag, np.uint16)<<7

   lwpFlag = lwpFlagDF.loc[:,lwpFlagDF.columns==100]
   lwpFlag = np.array(lwpFlag, np.uint16)<<6

   corrFlag = corrFlagDF.loc[:,corrFlagDF.columns==100]
   corrFlag = np.array(corrFlag, np.uint16)<<14

   pointFlag = pointFlagDF.loc[:,pointFlagDF.columns==100]
   pointFlag = np.array(pointFlag, np.uint16)<<15

   finalFlag = rainFlag + lwpFlag + corrFlag + pointFlag

   flagDF = pd.DataFrame(index=rainFlagDF.index, columns=['flag'],
                         data=finalFlag)

   return flagDF
