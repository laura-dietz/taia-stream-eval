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
import cPickle

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

metrics =  ['correctedAUC','MAP','nDCG@R','Prec@R','numPosPredictions']

#intervalList = [(start, start + epochsPerInterval) for start in starts]
#intervalList = [(1325379600,1328058000)]#, (0, 1371517333)]


weekRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv')]
dayRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('day.tsv')]
allRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('all.tsv')]

testEntityList = [ 'Alex_Kapranos' ,'Darren_Rowse', 'Satoshi_Ishii', 'Bill_Coen']
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


#intervalBounds = {'all':listOfPosIntervals(judgmentLevel,[(evalTR, evalTRend)]),
#                     'week':listOfPosIntervals(judgmentLevel,intervalRange(epochsPerWeek)), 
#                     'day':listOfPosIntervals(judgmentLevel,intervalRange(epochsPerDay))} 

#numberOfIntervals = {'all':1,
#                     'week':len(intervalBounds['week']), 
#                     'day':len(intervalBounds['day'])} 

plotData = {}

def addPlot(team, runname, metric, judgmentLevel, intervalType, xs, weightedYs, uniformYs):
    plotData[(team, runname, metric, judgmentLevel, intervalType)]= (xs,weightedYs, uniformYs)


def savePlot():
    cPickle.dump(plotData, open(os.path.expanduser(evalDir)+'perf_over_time','w'))


def loadPlot():
    return cPickle.load(open(os.path.expanduser(evalDir)+'perf_over_time','r'))
    



def createData(prefix,intervalRunfiles, metric):
    for idx,(intervalType, runfiles) in enumerate(intervalRunfiles.items()[:]):
        for runIdx, evalFile in enumerate(sorted(runfiles[:])):
            print ' processing evalFile',evalFile
            df = np.genfromtxt(evalFile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
            team = df[0]['team']                                     
            teamss.append(team)
            runname = df[0]['runname']
            weightedYs = []
            uniformYs = []
            xs = []


            #print 'intervalBounds', intervalType, intervalBounds[intervalType]
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
                    correctedValues = [ posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp) 
                            / posTruths(judgmentLevel, entity) 
                            * numPosIntervals(judgmentLevel, entity, intervalType) 
                            * data[data['query']==entity]['value'][0]
                        if np.count_nonzero(data['query']==entity)>0 else 0.0 
                        for entity in entityList 
                        if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
                        ]
                    uniformWeighting = values
                    
                    correctedWeighting = correctedValues
                    weightedValues = uniformWeighting if not CORRECTED else correctedWeighting
                    #records.append(createStatsRecord(team, runname, intervalLow, unjudgedAs, judgmentLevel, metric, np.mean(weightedValues), np.std(weightedValues), intervalType))
                    #ys.append(np.mean(weightedValues))
                    weightedYs.append(np.mean(correctedWeighting))
                    uniformYs.append(np.mean(uniformWeighting))
                    xs.append(intervalLow)
            if(weightedYs) and intervalType=='all':                
                xs.append(evalTRend)
                weightedYs.append(weightedYs[-1])
                uniformYs.append(uniformYs[-1])
            addPlot(team, runname, metric, judgmentLevel, intervalType, xs, weightedYs, uniformYs)


def createAll():
    for metric in metrics:
        createData(os.path.expanduser(evalDir)+'overview_',allIntervalRunfiles, metric)
    savePlot()


def createTest():
    for metric in metrics[:1]:
        runf = {'all':allIntervalRunfiles['all'][:1],'week':allIntervalRunfiles['week'][:1],'day':allIntervalRunfiles['day'][:1]}
        createData(os.path.expanduser(evalDir)+'overview_',runf, metric)
    savePlot()


createTest()