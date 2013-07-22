#!/usr/bin/env python

from utils import epochsToDate
from utils import correctWeighting
import os.path
import numpy as np
from metrics import *
import sys
import string
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime
from matplotlib.dates import DateFormatter, WeekdayLocator, MONDAY
from truthutil import *
import matplotlib.cm as cm


DEBUG=False

if len(sys.argv)>1:
    evalDir = sys.argv[1]
else:
    #evalDir = '~/kba-evaluation/taia/data/umass-runs/'
    #evalDir = '/media/dietz/bob/taia/all-runs/'
    evalDir = '~/kba-evaluation/taia/data/interval4/'

#if len(sys.argv)>2:
#    testEntity = sys.argv[2]
#else:
#    testEntity = 'Douglas_Carswell'  

if len(sys.argv)>2:
    judgmentLevel = int(sys.argv[2])
else:
    print 'using judgmentLevel 1'
    judgmentLevel=1


if len(sys.argv)>6:
   team1 = sys.argv[3]
   run1= sys.argv[4]
   team2 = sys.argv[5]
   run2 = sys.argv[6]
else:    
   team2 = 'udel_fang'
   run2 = 'UDInfoKBA_WIKI1'
   #team2 = 'UMass_CIIR'
   #run2 = 'PC_RM10_1500'
   #team2 ='uiucGSLIS'
   #run2='gslis_adaptive'
   team1 = 'CWI'
   run1= 'google_dic_3'




#if len(sys.argv)>4:
#    CORRECTED=(sys.argv[4]=='True')
#else:
#    CORRECTED = False

avgWindow = 4


runfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv')]

epochsPerWeek = int(6.048E5)
epochsPerDay = 86400
evalTR = 1325376000
evalTRend = 1338508800

numberOfIntervals = (evalTRend - evalTR)/epochsPerWeek

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


if len(sys.argv)>7:
    singleEntity = sys.argv[7]
    entityList = [singleEntity]
else:
    entityList = fullEntityList



#if DEBUG: entityList = testEntityList


eval_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('intervalLow','d4'),('intervalUp','d4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('value','f4')])                        


def judgmentLevelToStr(judgementLevel):
    return 'central' if judgmentLevel==2 else 'relevant+central'

def correctedToStr():
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'

def correctedToStrs(CORRECTED):
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'

hfmt = dates.DateFormatter('%m/%d')

entityColors='myb'
entityIdx=0

#metric = 'nDCG@R'
#metric= 'Prec@R'

def myuniq(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]


#def plotAll():
# for metric in ['nDCG@R','correctedAUC','MAP','numPosPredictions','Prec@R']:
#    for page in range(0,len(runfiles),6):
#        runfileList = runfiles[page:page+6]
#        fig = plt.figure() 
#        for runIdx, evalFile in enumerate(runfileList):
#        
#            df = np.genfromtxt(evalFile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
#            
#            entity = testEntity
#        
#            fig.add_subplot(3,2,(runIdx+1))
#        
#            print metric,' processing evalFile',evalFile
#            data = df[np.logical_and(df['query']==entity, 
#                                     np.logical_and(df['metric']==metric, df['judgmentLevel']==judgmentLevel))]
#            
#            posData = np.array([posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d in data])
#            
#            if(len(data)>0):
#                team = data[0]['team']                                     
#                runname = data[0]['runname']
#                values = data['value']
#
#                totalposvalues = posTruths(judgmentLevel, entity)
#                print entity, metric
#                uniformWeighting = values
#
#                correctedWeighting = posData/totalposvalues*numberOfIntervals*values
#                weightedValues = uniformWeighting if not CORRECTED else correctedWeighting
#                print 'uniform =',np.mean(uniformWeighting), ' corrected=',np.mean(correctedWeighting),' choosing ',np.mean(weightedValues)
#    
#                plt.scatter(epochsToDate(data['intervalLow']),weightedValues, c=entityColors[entityIdx], alpha=0.5)
#    
#                window = np.ones(int(avgWindow))/float(avgWindow)
#                intervalData = np.convolve(weightedValues, window, 'same')
#                if(len(data['intervalLow'])== len(intervalData)):
#                    print len(epochsToDate(data['intervalLow'])), len(data['intervalLow']), len(intervalData)
#                    plt.plot(epochsToDate(data['intervalLow']),intervalData, c=entityColors[entityIdx])
#                
#                plt.ylabel(metric)
#                plt.xlabel('ETR days')
#                plt.title( team+' '+runname+' '+judgmentLevelToStr(judgmentLevel))
#        
#            fig.subplots_adjust(hspace=0.5, wspace=0.5)
#            plt.suptitle("%s %s %s (page %d)" %(metric,entity, correctedToStr(), page))
#            figureFilename="%s%s_entity_%s_%s_%s_%d.pdf"%(os.path.expanduser(evalDir),metric,entity,judgmentLevelToStr(judgmentLevel),correctedToStr(),page)
#            plt.savefig(figureFilename)
#            print figureFilename
#        
                    
allteams = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang', 'uiucGSLIS']
teamColors={team:cm.hsv(1. * i/len(allteams),1) for i,team in enumerate(np.unique(allteams))}

for metric in ['MAP','correctedAUC','nDCG@R','Prec@R']:
   #team1 = 'UvA'
   #run1 = 'UvAIncLearnHigh'
   intervalType ='day'
    
   for entity in entityList:
       #entity = testEntity#'Mario_Garnero'
        judgmentLevel=1        
        
        #umassRunfile = (os.path.expanduser(evalDir)+'input.UMass_CIIR-PC_RM10_1500.gz-eval-day.tsv')
        umassRunfile = (os.path.expanduser(evalDir)+('input.%s-%s.gz-eval-%s.tsv'%(team1,run1,intervalType)))
        
        uiucRunfile = (os.path.expanduser(evalDir)+('input.%s-%s.gz-eval-%s.tsv'%(team2,run2,intervalType)))
        print 'team1', umassRunfile
        print 'team2', uiucRunfile
        
        
        umassdf = np.genfromtxt(umassRunfile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
        umassData =umassdf[np.logical_and(umassdf['query']==entity, 
                                     np.logical_and(umassdf['metric']==metric, umassdf['judgmentLevel']==judgmentLevel))] 
        umassPosData = np.array([posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d in umassData])

        uiucdf = np.genfromtxt(uiucRunfile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
        uiucData =uiucdf[np.logical_and(uiucdf['query']==entity, 
                                     np.logical_and(uiucdf['metric']==metric, uiucdf['judgmentLevel']==judgmentLevel))] 
        uiucPosData = np.array([posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d in uiucData])

        fig = plt.figure(figsize=(8.0, 3.0)) 
           
        #entity = 'Mario_Garnero'
        totalposvalues = posTruths(judgmentLevel, entity)

        def plot(data, posData, CORRECTED, team, metric):
            
            if(len(data)>0):
                team = data[0]['team']                                     
                runname = data[0]['runname']
                values = data['value']

                print entity, metric
                uniformWeighting = values

                #correctedWeighting = posData/totalposvalues*numberOfIntervals*values
                correctedWeighting = correctWeighting(values, posData, totalposvalues, numberOfIntervals)
                weightedValues = uniformWeighting if not CORRECTED else correctedWeighting
                # print 'uniform =',np.mean(uniformWeighting), ' corrected=',np.mean(correctedWeighting),' choosing ',np.mean(weightedValues)
    
                plt.scatter(epochsToDate(data['intervalLow']),weightedValues, c=teamColors[team], alpha=0.5)
                plt.xlim(0,110)
                
                #intervalStarts = [low for (low,up) in intervalBounds[judgmentLevel]['day']]
                #allData = [data[data['intervalLow']==low]['value'] if ???? else 0.0 for low in intervalStarts]
                window = np.ones(int(4))/float(4)
                intervalData = np.convolve(weightedValues, window, 'same')
                #if(len(data['intervalLow'])== len(intervalData)):
                plt.plot(epochsToDate(data['intervalLow']),intervalData, c=teamColors[team])
                #plt.plot([epochsToDate(start) for start in intervalStarts], intervalData, c=teamColors[team])
                
        
        
        fig.add_subplot(1,2,1)
        plot(umassData, umassPosData, False, team1, metric)
        plot(uiucData, uiucPosData, False, team2, metric)
        plt.ylabel(renameMetric(metric))
        plt.xlabel('ETR days')
        plt.xlim(0, 110)
        plt.title( correctedToStrs(False))

        fig.add_subplot(1,2,2)
        plot(umassData, umassPosData,True,team1, metric)
        plot(uiucData, uiucPosData, True,team2, metric)
        plt.ylabel(renameMetric(metric))
        plt.xlabel('ETR days')
        plt.xlim(0, 110)
        plt.title( correctedToStrs(True))
        
        fig.subplots_adjust(hspace=0.5, wspace=0.5)
        #plt.suptitle("%s" %(entity))
        figureFilename="%s%s_%s-vs-%s_%s_sidebyside_%s_%s.pdf"%(os.path.expanduser(evalDir),team1, run1, team2, run2, metric, entity)
        plt.savefig(figureFilename, bbox_inches='tight')
        print figureFilename
        
