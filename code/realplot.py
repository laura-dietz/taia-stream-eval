#!/usr/bin/env python

import os.path
import numpy as np
from metrics import *
from utils import *
import sys
import string
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime
from matplotlib.dates import DateFormatter, WeekdayLocator, MONDAY


WEEK = True
if len(sys.argv)>1:
    evalFile = sys.argv[1]
else:
    if (WEEK):
        evalFile = '~/kba-evaluation/taia/data/umass-runs/UMass_CIIR-FS_NV_6000.gz-eval-week.tsv'
    else :    
        evalFile = '~/kba-evaluation/taia/data/umass-runs/UMass_CIIR-FS_NV_6000.gz-eval-day.tsv'


if(WEEK):
    avgWindow = 4
else:
    avgWindow = 7


testEntityList = [ 'Darren_Rowse', 'Satoshi_Ishii', 'Bill_Coen']
fullEntityList = [
    'Aharon_Barak',
    'Alexander_McCall_Smith',
    'Alex_Kapranos',
    'Annie_Laurie_Gaylor',
    'Basic_Element_(company)',
    'Basic_Element_(music_group)',
    'Bill_Coen',
    'Boris_Berezovsky_(businessman)',
    'Boris_Berezovsky_(pianist)',
    'Charlie_Savage',
    'Darren_Rowse',
    'Douglas_Carswell',
    'Frederick_M._Lawrence',
    'Ikuhisa_Minowa',
    'James_McCartney',
    'Jim_Steyer',
    'Lisa_Bloom',
    'Lovebug_Starski',
    'Mario_Garnero',
    'Masaru_Emoto',
    'Nassim_Nicholas_Taleb',
    'Rodrigo_Pimentel',
    'Roustam_Tariko',
    'Ruth_Rendell',
    'Satoshi_Ishii',
    'Vladimir_Potanin',
    'William_Cohen',
    'William_D._Cohan',
    'William_H._Gates,_Sr',
    ]
#entityListFromData = np.unique(a['query'])
entityList = testEntityList



eval_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('intervalLow','d4'),('intervalUp','d4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('value','f4')])                        

df = np.genfromtxt(os.path.expanduser(evalFile), dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')




hfmt = dates.DateFormatter('%m/%d')

entityColors='myb'

for judgmentLevel in [1,2]:
    fig = plt.figure() 
    
    for i,metric in enumerate([ 'numPosPredictions','nDCG@R', 'numPos', 'Prec@R','MAP',  'correctedAUC']):
        thisPlot = fig.add_subplot(3,2,(i+1))
        
    
        for entityIdx,entity in enumerate(entityList):
            data = df[np.logical_and(df['query']==entity, 
                                     np.logical_and(df['metric']==metric, df['judgmentLevel']==judgmentLevel))]
            values = data['value']
            print entity, metric
            print values
            if(len(values)>0):
                print np.mean(values)
    
                plt.scatter(epochsToDate(data['intervalLow']),data['value'], c=entityColors[entityIdx], alpha=0.5)
    
                window = np.ones(int(avgWindow))/float(avgWindow)
                intervalData = np.convolve(data['value'], window, 'same')
                plt.plot(epochsToDate(data['intervalLow']),intervalData, entityColors[entityIdx])
                
                plt.ylabel(renameMetric(metric))
                plt.xlabel('ETR days')
    
    fig.subplots_adjust(hspace=0.5, wspace=0.5)
    plt.show()
    plt.suptitle("%s %s" %(evalFile,'central' if judgmentLevel==2 else 'relevant + central'))
    plt.savefig("%s-plot-%d.pdf"%(os.path.expanduser(evalFile), judgmentLevel), bbox_inches='tight')


            
