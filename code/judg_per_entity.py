#!/usr/bin/env python

import matplotlib

matplotlib.use('Agg')

import os.path
import numpy as np
from metrics import *
from utils import epochsToDate
import sys
import string
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime
from matplotlib.dates import DateFormatter, WeekdayLocator, MONDAY
from truthutil import *
import matplotlib
from utils import *
import targetentities

DEBUG = False

if len(sys.argv) > 1:
    targetDir = sys.argv[1]
else:
    targetDir = ''

avgWindow = 7

testEntityList = ['Mario_Garnero']
fullEntityList = targetentities.loadEntities()
entityList = testEntityList


#if DEBUG: entityList = testEntityList


eval_dtype = np.dtype(
    [('team', '50a'), ('runname', '50a'), ('query', '50a'), ('intervalLow', 'd4'), ('intervalUp', 'd4'),
     ('unjudged', '50a'), ('judgmentLevel', 'd4'), ('metric', '50a'), ('value', 'f4')])

#df = np.genfromtxt(os.path.expanduser(evalFile), dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')

if DEBUG: entityList = testEntityList


def judgmentLevelToStr(judgmentLevel):
    return 'central' if judgmentLevel == 2 else 'relevant+central'


hfmt = dates.DateFormatter('%m/%d')

entityColors = 'myb'

#==============================================================================
# def allEntities():
#   for page in range(0,len(entityList),3):
#     entityList = fullEntityList[page:page+3]
#     
#     fig = plt.figure() 
#     
#     for entityIdx,entity in enumerate(entityList):    
#         for judgmentLevel in [1,2]:
#     
#             thisPlot = fig.add_subplot(3,2,(entityIdx*2+judgmentLevel))
#             metric = 'numPos'
#         
#             
#             data = df[np.logical_and(df['query']==entity, 
#                                      np.logical_and(df['metric']==metric, df['judgmentLevel']==judgmentLevel))]
#             values = data['value']
#             print entity, metric
#             print values
#             if(len(values)>0):
#                 print np.mean(values)
#     
#                 plt.scatter(epochsToDate(data['intervalLow']),data['value'], c=entityColors[entityIdx], alpha=0.5)
#     
#                 window = np.ones(int(avgWindow))/float(avgWindow)
#                 intervalData = np.convolve(data['value'], window, 'same')
#                 plt.plot(epochsToDate(data['intervalLow']),intervalData, c=entityColors[entityIdx])
#                 
#                 plt.ylabel(metric)
#                 plt.xlabel('ETR days')
#                 plt.title(entity + ' '+judgmentLevelToStr(judgmentLevel))
#         
#         fig.subplots_adjust(hspace=0.5, wspace=0.5)
#             #pl.show()
#         plt.suptitle("numPos %s (page %d)" %(evalFile, page))
#         figureFilename="%s-entity_numPos-%d.pdf"%(os.path.expanduser(evalFile),page)
#==============================================================================
#        plt.savefig(figureFilename)
#        print figureFilename


def singlePlot(entity, judgmentLevel):
    metric = 'numPos'
    fig = plt.figure(figsize=(8.0, 3.0))
    intervalType = 'day'

    #data = df[np.logical_and(df['query']==entity,
    #                         np.logical_and(df['metric']==metric, df['judgmentLevel']==judgmentLevel))]
    intervalStarts = [epochsToDate(low) for (low, up) in intervalBounds[judgmentLevel][intervalType]]
    data = [(posTruthsInterval(judgmentLevel, entity, low, up), epochsToDate(low)) for (low, up) in
            intervalBounds[judgmentLevel][intervalType]]
    dataAll = [val for val, low in data]
    dataNonZero = [(val, low) for val, low in data if val > 0.0]
    values = data
    print entity, metric
    print values
    if (len(values) > 0):
        print np.mean(values)

        plt.scatter([low for val, low in dataNonZero], [val for val, low in dataNonZero], c='k', alpha=0.7)

        window = np.ones(int(avgWindow)) / float(avgWindow)
        intervalData = np.convolve(dataAll, window, 'same')
        plt.plot(intervalStarts, intervalData, c='k')

        plt.ylabel(renameMetric(metric))
        plt.ylim()
        plt.xlabel('ETR days')
        plt.title(entity + ' ' + judgmentLevelToStr(judgmentLevel))

    plt.xlim(0, kbaconfig.MAX_DAYS)
    #pl.show()
    #plt.suptitle("numPos %s (page %d)" %(evalFile, page))
    figureFilename = "%s_relevant_over_time_entity_%s.pdf" % (os.path.expanduser(targetDir), entity)
    print 'saving ', figureFilename
    plt.savefig(figureFilename, bbox_inches='tight')

# singlePlot('Mario_Garnero', 1)
for entity in fullEntityList:
    singlePlot(entity, 1)