import os.path
import numpy as np
from utils import *
import matplotlib.pyplot as plt
from matplotlib import dates
import matplotlib.cm as cm
from truthutil import *
from argparse import ArgumentParser
import os
import targetentities


DEBUG = False

evalDir = '~/kba-evaluation/taia/data/intervals/'
plotDir = 'aggregation_weights/'


parser = ArgumentParser()
parser.add_argument('--judgmentLevel', type=int, help='Judgement level', default=1)
parser.add_argument('-d', '--dir', metavar='DIR', default=evalDir)
args = parser.parse_args()

judgmentLevel = args.judgmentLevel
CORRECTED = True
evalDir = os.path.expanduser(args.dir)
if not os.path.exists(evalDir+plotDir):
    os.makedirs(evalDir+plotDir)
print "writing plots to ",(evalDir+plotDir)



testEntityList = [ 'Alex_Kapranos' ,'Darren_Rowse', 'Satoshi_Ishii', 'Bill_Coen']
fullEntityList =targetentities.loadEntities()
entityList = fullEntityList



eval_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('intervalLow','d4'),('intervalUp','d4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('value','f4')])                        

def judgmentLevelToStr(judgementLevel):
    return 'central' if judgmentLevel==2 else 'relevant+central'

def correctedToStr():
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'


hfmt = dates.DateFormatter('%m/%d')

entityColors='myb'
entityIdx=0

stats_dtype = np.dtype([('entityListName','50a'),('intervalLow','f4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('mean','f4'),('stdev','f4'),('intervalType','50a')])



def createStatsRecord(entityListName, intervalLow, unjudgedAs, judgmentLevel, metricname, mean, stdev, intervalType):
    return np.array([(entityListName, intervalLow, unjudgedAs,judgmentLevel,metricname, mean, stdev, intervalType)],  dtype=stats_dtype)

records = []


fig = plt.figure() 

allteams = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang', 'uiucGSLIS']
teamColors={team:cm.hsv(1. * i/len(allteams),1) for i,team in enumerate(np.unique(allteams))}

print teamColors

def teamColor(team):
    return teamColors[team]    

teamss=[]

def createWeightPlot(prefix, entityList, title):
    if len(entityList) ==1: entityListName = entityList[0]
    else: entityListName= "all"
    plt.suptitle('weights '+title)
    for idx,intervalType in enumerate(['all','week','day']):
        fig.add_subplot(1,2,1)
        plt.locator_params(axis='both', nbins=5)
        plt.title(intervalType)
        ys = []
        xs = []
        seriesLabel = "aggregation weights"

        for (intervalLow, intervalUp) in intervalBounds[judgmentLevel][intervalType]:


            unjudgedAs = 'neg'

            weightedValues = [ correctWeighting( 1.0
                , posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp)
                , posTruths(judgmentLevel, entity)
                , numPosIntervals(judgmentLevel, entity, intervalType))
                                for entity in entityList
                                if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
            ]
            if(len(weightedValues)>0):
                records.append(createStatsRecord(entityListName, intervalLow, unjudgedAs, judgmentLevel, "weight", np.mean(weightedValues), np.std(weightedValues), intervalType))
                ys.append(np.mean(weightedValues))
                xs.append(intervalLow)



        if(ys) and intervalType=='all':
            xs.append(evalTRend)
            ys.append(ys[-1])

        print 'sums to', np.sum(ys), 'mean is ', np.mean(ys)
        plotcolor = 'k'
        plt.plot(epochsToDate(np.array(xs)), ys, label=seriesLabel, color=plotcolor, alpha=0.5, ls='-',marker='o')
        plt.ylabel('weights')
        plt.xlabel('ETR days')

        plt.xlim(0, 124)
        figfile = "%s%s_%s_teams_over_time_%s_%s.pdf"%(prefix,intervalType,'weights', judgmentLevelToStr(judgmentLevel), correctedToStr())
        print "saving to... ",figfile
        plt.savefig(figfile, bbox_inches='tight')
        plt.clf()


def plotWeights():
    createWeightPlot(evalDir+plotDir+"all_weights__", entityList, 'all')
    for entity in entityList:
        createWeightPlot(evalDir+plotDir+entity+"__weights__", [entity], entity)

def savePlottedValues(plottedValues):
    tableFile = "%s_weights_over_time_%s.tsv"%(evalDir+plotDir, judgmentLevelToStr(judgmentLevel))
    #tableFile="%s%s_micro_stats_%s_%s.tsv"%(os.path.expanduser(evalDir),judgmentLevelToStr(judgmentLevel), correctedToStr())
    #stats_dtype = np.dtype([('team','50a'),('runname','50a'),('intervalLow','f4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('mean','f4'),('stdev','f4'),('intervalType','50a')])

    print plottedValues[:1]
    np.savetxt(tableFile,plottedValues,fmt='%s\t%f\t%s\t%d\t%s\t%f\t%f\t%s')

    #np.savetxt(tableFile, table,fmt='%s\t%s\t%s\t%s\t%s')
    print 'micro stats in table ',tableFile



plotWeights()

plottedValues=np.hstack(records)
savePlottedValues(plottedValues)


print(plottedValues)