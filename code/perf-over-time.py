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

def createPlot(prefix,intervalRunfiles, metric,entityList):
    fig = plt.figure(figsize=(8.0, 4.0)) 
    #plt.suptitle(metric+'_'+correctedToStr())
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

                    correctedValues = [ correctWeighting( data[data['query']==entity]['value'][0]
                        , posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp)
                        , posTruths(judgmentLevel, entity)
                        ,numPosIntervals(judgmentLevel, entity, intervalType))
                        if np.count_nonzero(data['query']==entity)>0 else 0.0 
                        for entity in entityList 
                        if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
                        ]


#                    correctedValues = [ posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp) 
#                            / posTruths(judgmentLevel, entity) 
#                            * numPosIntervals(judgmentLevel, entity, intervalType) 
#                            * data[data['query']==entity]['value'][0]
#                        if np.count_nonzero(data['query']==entity)>0 else 0.0 
#                        for entity in entityList 
#                        if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
#                        ]

                    team = data[0]['team']                                     
                    runname = data[0]['runname']
                    unjudgedAs = data[0]['unjudged']
                    uniformWeighting = values
                    
                    correctedWeighting = correctedValues
                    weightedValues = uniformWeighting if not CORRECTED else correctedWeighting
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
        
            plotcolor = teamColors[team]
            plt.plot(epochsToDate(np.array(xs)), ys, label=seriesLabel, color=plotcolor, alpha=0.5, ls='-',marker='.')
            if args.subplot and idx==0:
                plt.legend(loc='center left', bbox_to_anchor=(1.+(idx*0.5), 0.5),fontsize='small')
            if not args.subplot:
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5),fontsize='small')
            plt.ylabel(renameMetric(metric))
            plt.xlabel('ETR days')

        #plt.gca().autoscale_view(tight=True, scalex=True, scaley=False)
        plt.xlim(0, 110)
        if not args.subplot:
            plt.savefig("%s%s_%s_teams_over_time_%s_%s.pdf"%(prefix,intervalType,metric, judgmentLevelToStr(judgmentLevel), correctedToStr()), bbox_inches='tight')
            plt.clf()
    if args.subplot: fig.subplots_adjust(hspace=0.5, wspace=0.5)
    if args.subplot: plt.savefig("%s%s_teams_over_time_%s_%s.pdf"%(prefix,metric, judgmentLevelToStr(judgmentLevel),correctedToStr()), bbox_inches='tight')
    plt.clf()

def plotAll(prefix):
    for metric in metrics:
        createPlot(os.path.expanduser(evalDir)+prefix+'_',allIntervalRunfiles, metric,entityList)

def plotTeams():
    if plotTeams:
        for team in allteams[:]:
             print 'processing team',team
             tweekRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv') and team in file]
             tdayRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('day.tsv') and team in file]
             tallRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('all.tsv') and team in file]
             
             intervalRunfiles = {'all':tallRunfiles[:], 'week':tweekRunfiles[:], 'day':tdayRunfiles[:]}
             for metric in metrics:
                 createPlot(os.path.expanduser(evalDir)+team+'_', intervalRunfiles, metric,entityList)
    


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
            createPlot(os.path.expanduser(evalDir)+'_groundtruth_', intervalRunfiles, metric,entityList)

        for entity in entityList:
            for metric in ['numPos','numPredictions']:
                createPlot(os.path.expanduser(evalDir)+entity+'_groundtruth_', intervalRunfiles, metric,[entity])




plotAll('overview')
plotTeams()
#plotTruth()

def testplot():
        for team in allteams[5:6]:
             print 'processing team',team
             tweekRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv') and team in file]
             tdayRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('day.tsv') and team in file]
             tallRunfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('all.tsv') and team in file]
             
             intervalRunfiles = {'all':tallRunfiles[:1], 'week':tweekRunfiles[:1], 'day':tdayRunfiles[:1]}
             print 'intervalRunfiles', intervalRunfiles
             for metric in ['Prec@R']:
                 createPlot(os.path.expanduser(evalDir)+team+'_', intervalRunfiles, metric)


#testplot()
