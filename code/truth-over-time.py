
import matplotlib
matplotlib.use('Agg')

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
import operator
import math
import matplotlib.cm as cm
from truthutil import *
from argparse import ArgumentParser
from utils import correctWeighting
import targetentities

DEBUG = False

#evalDir = '~/kba-evaluation/taia/data/umass-runs/'
#evalDir = '/media/dietz/bob/taia/all-runs/'
evalDir = '~/kba-evaluation/taia/data/intervals/'

parser = ArgumentParser()
parser.add_argument('--plot-teams', action='store_true',default=False)
parser.add_argument('--judgmentLevel', type=int, help='Judgement level', default=1)
parser.add_argument('--subplot', action='store_true', help='Plot everything on one figure', default=False)
parser.add_argument('--weighted', action='store_true', default=False)
parser.add_argument('-d', '--dir', metavar='DIR', default=evalDir)
args = parser.parse_args()

judgmentLevel = args.judgmentLevel
plotTeams = args.plot_teams
CORRECTED = args.weighted
evalDir = args.dir

#CORRECTED=True
metrics =  kbaconfig.METRICS

#intervalList = [(start, start + epochsPerInterval) for start in starts]
#intervalList = [(1325379600,1328058000)]#, (0, 1371517333)]


weekRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv')]
dayRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('day.tsv')]
allRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('all.tsv')]

testEntityList = [ 'Alex_Kapranos' ,'Darren_Rowse', 'Satoshi_Ishii', 'Bill_Coen']
fullEntityList =targetentities.loadEntities()
entityList = fullEntityList
if DEBUG: entityList = fullEntityList



#if DEBUG: entityList = testEntityList


eval_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('intervalLow','d4'),('intervalUp','d4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('value','f4')])                        

def judgmentLevelToStr(judgementLevel):
    return 'central' if judgmentLevel==2 else 'relevant+central'

def correctedToStr():
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'


hfmt = dates.DateFormatter('%m/%d')

entityColors='myb'
entityIdx=0

#metric = 'nDCG@R'
#metric= 'Prec@R'

stats_dtype = np.dtype([('team','50a'),('runname','50a'),('intervalLow','f4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('mean','f4'),('stdev','f4'),('intervalType','50a')])                        



def createStatsRecord(team, runname, intervalLow, unjudgedAs, judgmentLevel, metricname, mean, stdev, intervalType):
    return np.array([(team, runname, intervalLow, unjudgedAs,judgmentLevel,metricname, mean, stdev, intervalType)],  dtype=stats_dtype)

records = []

allIntervalRunfiles = {'all':allRunfiles, 'week':weekRunfiles, 'day':dayRunfiles}
intervalTypeStarts = {'all':allStarts, 'week':weekStarts, 'day':dayStarts}
intervalTypeDuration = {'all':(evalTRend-evalTR), 'week':epochsPerWeek, 'day':epochsPerDay}
#metric = 'nDCG@R'

#for intervalType, runfiles in intervalRunfiles.items():
#intervalType = 'week'
#runfiles = intervalRunfiles[intervalType]    



fig = plt.figure() 

allteams = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang', 'uiucGSLIS']
teamColors={team:cm.hsv(1. * i/len(allteams),1) for i,team in enumerate(np.unique(allteams))}
#teamColors={team:cm.summer(i,1) for i,team in enumerate(np.unique(allteams))}

print teamColors

def teamColor(team):
    return teamColors[team]    

teamss=[]

def createTruthPlot(prefix,intervalRunfiles, metric,entityList):
    plt.suptitle(metric+'_'+correctedToStr())
    for idx,(intervalType, runfiles) in enumerate(intervalRunfiles.items()[:]):
        if args.subplot : fig.add_subplot(3,2,(idx*2+1))
        else: fig.add_subplot(1,2,1)
        plt.locator_params(axis='both', nbins=5)
        plt.title(intervalType)
        for runIdx, evalFile in enumerate(sorted(runfiles[:])):
            print ' processing evalFile',evalFile
            df = np.genfromtxt(evalFile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
            team = df[0]['team']                                     
            teamss.append(team)
            runname = df[0]['runname']
            ys = []
            xs = []
            seriesLabel=team+' '+runname


            #print 'intervalBounds', intervalType, intervalBounds[judgmentLevel][intervalType]
            for (intervalLow, intervalUp) in intervalBounds[judgmentLevel][intervalType]:
                data = df[np.logical_and(df['intervalLow']==intervalLow, 
                                         np.logical_and(df['metric']==metric, df['judgmentLevel']==judgmentLevel))]
                
                if len(data)>0:
                    values = [data[data['query']==entity]['value'][0] 
                        if np.count_nonzero(data['query']==entity)>0 else 0.0 
                        for entity in entityList 
                        if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
                        ]
                        
    
                    #compute numPos / totalPos * numScoredIntervals * values 

#                    correctedValues = [ data[data['query']==entity]['value'][0]
 #                       if np.count_nonzero(data['query']==entity)>0 else 0.0 
  #                      for entity in entityList 
   #                     #if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
    #                    ]


                    team = data[0]['team']                                     
                    runname = data[0]['runname']
                    unjudgedAs = data[0]['unjudged']
                    uniformWeighting = values
                    
                    weightedValues = uniformWeighting
                    
                    #print 'uniform =',np.mean(uniformWeighting), ' corrected=',np.mean(correctedWeighting),' choosing ',np.mean(weightedValues)
                    records.append(createStatsRecord(team, runname, intervalLow, unjudgedAs, judgmentLevel, metric, np.mean(weightedValues), np.std(weightedValues), intervalType))
                    ys.append(np.mean(weightedValues))
                    xs.append(intervalLow)
            
                    
                #else: 
                    #ys.append(0.0)
                    #xs.append(intervalLow)
            if(ys) and intervalType=='all':                
                xs.append(evalTRend)
                ys.append(ys[-1])
        
            #plotcolor = teamColors[team]
            plt.plot(epochsToDate(np.array(xs)), ys, label=seriesLabel, color='k', alpha=0.5, ls='',marker='o')

            # moving average
            if(not intervalType == 'all'):
                window = np.ones(int(7))/float(7)
                ywindow = np.convolve(ys, window, 'same')
                plt.plot(epochsToDate(np.array(xs)),ywindow, color='k')
            
            
            plt.ylabel(metric)
            plt.xlabel('ETR days')

        #plt.gca().autoscale_view(tight=True, scalex=True, scaley=False)
        plt.xlim(0, kbaconfig.MAX_DAYS)
        if not args.subplot:
            plt.savefig("%s%s_%s_teams_over_time_%s_%s.pdf"%(prefix,intervalType,metric, judgmentLevelToStr(judgmentLevel), correctedToStr()), bbox_inches='tight')
            plt.clf()
    if args.subplot: fig.subplots_adjust(hspace=0.5, wspace=0.5)
    if args.subplot: plt.savefig("%s%s_teams_over_time_%s_%s.pdf"%(prefix,metric, judgmentLevelToStr(judgmentLevel),correctedToStr()), bbox_inches='tight')
    plt.clf()


# ground truth plot
def plotTruth():
    #for team in allteams[5:6]:
        team = 'UvA'
        #team = 'UMass_CIIR'
        tweekRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv') and team in file]
        tdayRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('day.tsv') and team in file]
        tallRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('all.tsv') and team in file]
        
        intervalRunfiles = {'all':tallRunfiles[:1], 'week':tweekRunfiles[:1], 'day':tdayRunfiles[:1]}
        for metric in ['numPos','numPredictions']:
            createTruthPlot(os.path.expanduser(evalDir)+'_groundtruth_', intervalRunfiles, metric,entityList)

        for entity in entityList:
            for metric in ['numPos','numPredictions']:
                createTruthPlot(os.path.expanduser(evalDir)+entity+'_groundtruth_', intervalRunfiles, metric,[entity])




#plotTeams()
plotTruth()

def plotPaper():
        team = 'UvA'
        #team = 'UMass_CIIR'
        tweekRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv') and team in file]
        tdayRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('day.tsv') and team in file]
        tallRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('all.tsv') and team in file]
        
        intervalRunfiles = {'all':tallRunfiles[:1], 'week':tweekRunfiles[:1], 'day':tdayRunfiles[:1]}
        for metric in ['numPos','numPredictions']:
            createTruthPlot(os.path.expanduser(evalDir)+'_groundtruth_', intervalRunfiles, metric,entityList)

        entity = 'Mario_Garnero'
        for metric in ['numPos','numPredictions']:
            createTruthPlot(os.path.expanduser(evalDir)+entity+'_groundtruth_', intervalRunfiles, metric,[entity])




