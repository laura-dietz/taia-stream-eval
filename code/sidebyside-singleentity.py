#!/usr/bin/env python

from utils import epochsToDate
from utils import correctWeighting
import os.path
import numpy as np
import matplotlib.pyplot as plt
from truthutil import *
import matplotlib.cm as cm
from argparse import ArgumentParser
import targetentities

DEBUG=False

evalDir = '~/kba-evaluation/taia/data/interval4/'
plotDir = 'sidebyside/'


parser = ArgumentParser()
parser.add_argument('--judgmentLevel', type=int, help='Judgement level')
parser.add_argument('--team1', help='Team name of first run')
parser.add_argument('--run1', help='Name of first comparison run')
parser.add_argument('--team2', help='Team name of second run')
parser.add_argument('--run2', help='Name of second comparison run')
parser.add_argument('--entity',metavar='ENTITY', help='Optional: Entity to evaluate on', default='')
parser.add_argument('-d', '--dir', metavar='DIR', default=evalDir)
args = parser.parse_args()

team1 = args.team1
run1 = args.run1
team2 = args.team2
run2 = args.run2
judgmentLevel = args.judgmentLevel
print 'using judgmentLevel', judgmentLevel

evalDir = os.path.expanduser(args.dir)
if not os.path.exists(evalDir+plotDir):
    os.makedirs(evalDir+plotDir)

runfiles = [(os.path.expanduser(evalDir)+file) for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv')]


fullEntityList =targetentities.loadEntities()
if len(args.entity)>0:
    entityList = [args.entity]
else:
    entityList = fullEntityList



eval_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('intervalLow','d4'),('intervalUp','d4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('value','f4')])                        


def correctedToStrs(CORRECTED):
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'

allteams = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang', 'uiucGSLIS']
teamColors={team:cm.hsv(1. * i/len(allteams),1) for i,team in enumerate(np.unique(allteams))}

for metric in ['MAP','nDCG@R','Prec@R']:
   intervalType ='day'
    
   for entity in entityList:

        runfile1 = (os.path.expanduser(evalDir)+('input.%s-%s.gz-eval-%s.tsv'%(team1,run1,intervalType)))
        
        runfile2 = (os.path.expanduser(evalDir)+('input.%s-%s.gz-eval-%s.tsv'%(team2,run2,intervalType)))
        print 'team1', runfile1
        print 'team2', runfile2
        
        
        df1 = np.genfromtxt(runfile1, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
        data1 =df1[np.logical_and(df1['query']==entity,
                                     np.logical_and(df1['metric']==metric, df1['judgmentLevel']==judgmentLevel))]
        posData1 = np.array([posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d in data1])

        df2 = np.genfromtxt(runfile2, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
        data2 =df2[np.logical_and(df2['query']==entity,
                                     np.logical_and(df2['metric']==metric, df2['judgmentLevel']==judgmentLevel))]
        posData2 = np.array([posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d in data2])

        fig = plt.figure(figsize=(8.0, 3.0)) 
           
        totalposvalues = posTruths(judgmentLevel, entity)

        def plot(data, posData, CORRECTED, team, metric):
            
            if(len(data)>0):
                values = data['value']

                print entity, metric
                uniformWeighting = values

                #correctedWeighting = posData/totalposvalues*numberOfIntervals*values
                correctedWeighting = correctWeighting(values, posData, totalposvalues, numberOfIntervals[judgmentLevel][intervalType])
                weightedValues = uniformWeighting if not CORRECTED else correctedWeighting

                print "plotting side by side", team, weightedValues

                plt.scatter(epochsToDate(data['intervalLow']),weightedValues, c=teamColors[team], alpha=0.5)
                #plt.xlim(0,filenames.MAX_DAYS)
                
                window = np.ones(int(4))/float(4)
                intervalData = np.convolve(weightedValues, window, 'same')
                plt.plot(epochsToDate(data['intervalLow']),intervalData, c=teamColors[team])

        
        
        fig.add_subplot(1,2,1)
        plot(data1, posData1, False, team1, metric)
        plot(data2, posData2, False, team2, metric)
        plt.ylabel(renameMetric(metric))
        plt.xlabel('ETR days')
        #plt.xlim(0, filenames.MAX_DAYS)
        plt.title( correctedToStrs(False))

        fig.add_subplot(1,2,2)
        plot(data1, posData1,True,team1, metric)
        plot(data2, posData2, True,team2, metric)
        plt.ylabel(renameMetric(metric))
        plt.xlabel('ETR days')
        #plt.xlim(0, filenames.MAX_DAYS)
        plt.title( correctedToStrs(True))
        
        fig.subplots_adjust(hspace=0.5, wspace=0.5)
        plt.suptitle("%s" %(targetentities.shortname(entity)))
        figureFilename="%s%s_%s-vs-%s_%s_sidebyside_%s_%s.pdf"%(evalDir+plotDir,team1, run1, team2, run2, metric, targetentities.shortname(entity))
        plt.savefig(figureFilename, bbox_inches='tight')
        print figureFilename
