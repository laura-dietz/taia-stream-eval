"""
Plot system performance over time for days, weeks, and all.
"""

import matplotlib

matplotlib.use('Agg')
import os.path
import numpy as np
from utils import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from truthutil import *
from argparse import ArgumentParser
from utils import correctWeighting
import targetentities
import kbaconfig

evalDir = '~/kba-evaluation/taia/data/intervals/'
plotDir = 'perf-over-time/'

parser = ArgumentParser()
parser.add_argument('--plot-teams', action='store_true', help='Generate plots for each team', default=False)
parser.add_argument('--judgmentLevel', type=int, help='Judgement level', default=1)
parser.add_argument('--subplot', action='store_true', help='Plot week,day,all on one figure', default=False)
parser.add_argument('--weighted', action='store_true', help='Use weighted aggregation', default=False)
parser.add_argument('-d', '--dir', metavar='DIR', default=evalDir)
args = parser.parse_args()

judgmentLevel = args.judgmentLevel
plot_teams = args.plot_teams
CORRECTED = args.weighted
evalDir = os.path.expanduser(args.dir)
if not os.path.exists(evalDir + plotDir):
    os.makedirs(evalDir + plotDir)
print "writing plots to ", (evalDir + plotDir)

metrics = kbaconfig.METRICS

weekRunfiles = [(evalDir) + file for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('week.tsv')]
dayRunfiles = [(evalDir) + file for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('day.tsv')]
allRunfiles = [(evalDir) + file for file in os.listdir(os.path.expanduser(evalDir)) if file.endswith('all.tsv')]

testEntityList = ['Alex_Kapranos', 'Darren_Rowse', 'Satoshi_Ishii', 'Bill_Coen']
fullEntityList = targetentities.loadEntities()

entityList = fullEntityList

eval_dtype = np.dtype(
    [('team', '50a'), ('runname', '50a'), ('query', '50a'), ('intervalLow', 'd4'), ('intervalUp', 'd4'),
     ('unjudged', '50a'), ('judgmentLevel', 'd4'), ('metric', '50a'), ('value', 'f4')])


def judgmentLevelToStr(judgementLevel):
    return 'central' if judgmentLevel == 2 else 'relevant+central'


def correctedToStr():
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'


stats_dtype = np.dtype(
    [('team', '50a'), ('runname', '50a'), ('intervalLow', 'f4'), ('unjudged', '50a'), ('judgmentLevel', 'd4'),
     ('metric', '50a'), ('mean', 'f4'), ('stdev', 'f4'), ('intervalType', '50a')])


def createStatsRecord(team, runname, intervalLow, unjudgedAs, judgmentLevel, metricname, mean, stdev, intervalType):
    return np.array([(team, runname, intervalLow, unjudgedAs, judgmentLevel, metricname, mean, stdev, intervalType)],
                    dtype=stats_dtype)


records = []

allIntervalRunfiles = {'all': allRunfiles, 'week': weekRunfiles, 'day': dayRunfiles}

fig = plt.figure()

allteams = kbaconfig.ALLTEAMS
teamColors = {team: cm.hsv(1. * i / len(allteams), 1) for i, team in enumerate(np.unique(allteams))}

print teamColors


def teamColor(team):
    if team in teamColors:
        return teamColors[team]
    else:
        cm.hsv(0.0, 0)


teamss = []


def createPlot(prefix, intervalRunfiles, metric, entityList):
    fig = plt.figure(figsize=(8.0, 4.0))
    for idx, (intervalType, runfiles) in enumerate(intervalRunfiles.items()[:]):
        if args.subplot:
            fig.add_subplot(3, 2, (idx * 2 + 1))
        else:
            fig.add_subplot(1, 2, 1)
        plt.locator_params(axis='both', nbins=5)
        plt.title(intervalType)
        for runIdx, evalFile in enumerate(sorted(runfiles[:])):
            print ' processing evalFile', evalFile
            df = np.genfromtxt(evalFile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
            team = df[0]['team']
            teamss.append(team)
            runname = df[0]['runname']
            ys = []
            xs = []
            seriesLabel = team + ' ' + runname

            for (intervalLow, intervalUp) in intervalBounds[judgmentLevel][intervalType]:
                data = df[np.logical_and(df['intervalLow'] == intervalLow,
                                         np.logical_and(df['metric'] == metric, df['judgmentLevel'] == judgmentLevel))]

                if len(data) > 0:
                    allvalues = [data[data['query'] == entity]['value']
                                 for entity in entityList
                    ]

                    # print 'allvalues', allvalues

                    values = [data[data['query'] == entity]['value'][0]
                              if np.count_nonzero(data['query'] == entity) > 0 else 0.0
                              for entity in entityList
                              if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
                    ]


                    #compute numPos / totalPos * numScoredIntervals * values 

                    correctedValues = [correctWeighting(data[data['query'] == entity]['value'][0]
                        , posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp)
                        , posTruths(judgmentLevel, entity)
                        , numPosIntervals(judgmentLevel, entity, intervalType))
                                       if np.count_nonzero(data['query'] == entity) > 0 else 0.0
                    if np.count_nonzero(data['query'] == entity) > 0 else 0.0
                                       for entity in entityList
                                       if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
                    ]

                    team = data[0]['team']
                    runname = data[0]['runname']
                    unjudgedAs = data[0]['unjudged']
                    uniformWeighting = values

                    correctedWeighting = correctedValues
                    weightedValues = uniformWeighting if not CORRECTED else correctedWeighting
                    #print 'weightedValues',weightedValues
                    #print 'uniform =',np.mean(uniformWeighting), ' corrected=',np.mean(correctedWeighting),' choosing ',np.mean(weightedValues)
                    records.append(createStatsRecord(team, runname, intervalLow, unjudgedAs, judgmentLevel, metric,
                                                     np.mean(weightedValues), np.std(weightedValues), intervalType))
                    ys.append(np.mean(weightedValues))
                    xs.append(intervalLow)

            if (ys) and intervalType == 'all':
                xs.append(evalTRend)
                ys.append(ys[-1])

            #print 'xs',xs
            #print 'ys', ys
            plotcolor = teamColors[team]
            plt.plot(epochsToDate(np.array(xs)), ys, label=seriesLabel, color=plotcolor, alpha=0.5, ls='-', marker='.')
            if args.subplot and idx == 0:
                plt.legend(loc='center left', bbox_to_anchor=(1. + (idx * 0.5), 0.5), fontsize='small')
            if not args.subplot:
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
            plt.ylabel(renameMetric(metric))
            plt.xlabel('ETR days')

        plt.xlim(0, kbaconfig.MAX_DAYS)
        if not args.subplot:
            plt.savefig("%s%s_%s_teams_over_time_%s_%s.pdf" % (
            prefix, intervalType, metric, judgmentLevelToStr(judgmentLevel), correctedToStr()), bbox_inches='tight')
            plt.clf()
    if args.subplot: fig.subplots_adjust(hspace=0.5, wspace=0.5)
    if args.subplot: plt.savefig(
        "%s%s_teams_over_time_%s_%s.pdf" % (prefix, metric, judgmentLevelToStr(judgmentLevel), correctedToStr()),
        bbox_inches='tight')
    plt.clf()


def plotAll(prefix):
    for metric in metrics:
        createPlot(evalDir + plotDir + prefix + '_', allIntervalRunfiles, metric, entityList)


def plotTeams():
    if plot_teams:
        for team in allteams[:]:
            print 'processing team', team
            tweekRunfiles = [(evalDir) + file for file in os.listdir(os.path.expanduser(evalDir)) if
                             file.endswith('week.tsv') and team in file]
            tdayRunfiles = [(evalDir) + file for file in os.listdir(os.path.expanduser(evalDir)) if
                            file.endswith('day.tsv') and team in file]
            tallRunfiles = [(evalDir) + file for file in os.listdir(os.path.expanduser(evalDir)) if
                            file.endswith('all.tsv') and team in file]

            intervalRunfiles = {'all': tallRunfiles[:], 'week': tweekRunfiles[:], 'day': tdayRunfiles[:]}
            for metric in metrics:
                createPlot(evalDir + plotDir + team + '_', intervalRunfiles, metric, entityList)


plotAll('overview')
plotTeams()

