import os.path
import numpy as np
import math
from argparse import ArgumentParser

from matplotlib import dates

from truthutil import *
import targetentities


DEBUG = False
evalDir = '~/kba-evaluation/taia/data/umass-runs/'

tableDir = 'overall_stats/'
entityTableDir = 'entity_stats/'

parser = ArgumentParser()
parser.add_argument('--judgmentLevel', type=int, help='Judgement level', default=1)
parser.add_argument('--weighted', action='store_true', default=False)
parser.add_argument('-d', '--dir', metavar='DIR', default=evalDir)
args = parser.parse_args()

judgmentLevel = args.judgmentLevel
CORRECTED = args.weighted
evalDir = os.path.expanduser(args.dir)
if not os.path.exists(evalDir + tableDir):
    os.makedirs(evalDir + tableDir)
if not os.path.exists(evalDir + entityTableDir):
    os.makedirs(evalDir + entityTableDir)
print "writing tables to ", (evalDir + tableDir)

print "CORRECTED ", CORRECTED, "judgmentLevel", judgmentLevel

metrics = kbaconfig.METRICS

weekRunfiles = [(os.path.expanduser(evalDir) + file) for file in os.listdir(os.path.expanduser(evalDir)) if
                file.endswith('week.tsv')]
dayRunfiles = [(os.path.expanduser(evalDir) + file) for file in os.listdir(os.path.expanduser(evalDir)) if
               file.endswith('day.tsv')]
allRunfiles = [(os.path.expanduser(evalDir) + file) for file in os.listdir(os.path.expanduser(evalDir)) if
               file.endswith('all.tsv')]

fullEntityList = targetentities.loadEntities()
entityList = fullEntityList

eval_dtype = np.dtype(
    [('team', '50a'), ('runname', '50a'), ('query', '50a'), ('intervalLow', 'd4'), ('intervalUp', 'd4'),
     ('unjudged', '50a'), ('judgmentLevel', 'd4'), ('metric', '50a'), ('value', 'f4')])


def correctedToStr():
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'


stats_dtype = np.dtype(
    [('team', '50a'), ('runname', '50a'), ('query', '50a'), ('unjudged', '50a'), ('judgmentLevel', 'd4'),
     ('metric', '50a'), ('mean', 'f4'), ('stdev', 'f4'), ('intervalType', '50a')])


def createStatsRecord(team, runname, entity, unjudgedAs, judgmentLevel, metricname, mean, stdev, intervalType):
    return np.array([(team, runname, entity, unjudgedAs, judgmentLevel, metricname, mean, stdev, intervalType)],
                    dtype=stats_dtype)


records = []

intervalRunfiles = {'all': allRunfiles, 'week': weekRunfiles, 'day': dayRunfiles}


def computePerformance():
    for intervalType, runfiles in intervalRunfiles.items():
        if not runfiles:
            print intervalRunfiles

    for intervalType, runfiles in intervalRunfiles.items():
        for runIdx, evalFile in enumerate(runfiles[:]):
            df = np.genfromtxt(evalFile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
            print ' processing evalFile', evalFile
            for entity in entityList:
                numberOfIntervals = {'all': numPosIntervals(judgmentLevel, entity, 'all'),
                                     'week': numPosIntervals(judgmentLevel, entity, 'week'),
                                     'day': numPosIntervals(judgmentLevel, entity, 'day')}

                for metric in metrics:
                    data = df[np.logical_and(df['query'] == entity,
                                             np.logical_and(df['metric'] == metric,
                                                            df['judgmentLevel'] == judgmentLevel))]

                    if len(data) > 0:
                        team = data[0]['team']
                        runname = data[0]['runname']
                        unjudgedAs = data[0]['unjudged']
                        unifValues = data['value']

                        ppdata = np.array(
                            [posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d
                             in data])

                        totalposvalues = posTruths(judgmentLevel, entity)
                        weightedValues = ppdata / totalposvalues * numberOfIntervals[intervalType] * unifValues
                        values = unifValues if not CORRECTED else weightedValues
                        values = values[np.nonzero(values)]
                        v = np.append(values, np.zeros(numberOfIntervals[intervalType] - len(values)))
                        records.append(
                            createStatsRecord(team, runname, entity, unjudgedAs, judgmentLevel, metric, np.mean(v),
                                              np.std(v), intervalType))

                    if (len(data) == 0):
                        print "no values found for " + entity + " " + metric + " in runfile " + evalFile


computePerformance()

if (records):
    statdf = np.hstack(records)


def teamsForRun(runname):
    return np.unique(statdf[statdf['runname'] == runname]['team'])


def allRunnames():
    return np.unique(statdf['runname'])


def selectMetricRunname(intervalType, metric, runname):
    return statdf[np.logical_and(statdf['runname'] == runname,
                                 np.logical_and(statdf['intervalType'] == intervalType, statdf['metric'] == metric))]


def selectMetricRunnameEntity(intervalType, metric, runname, entity):
    return statdf[np.logical_and(statdf['runname'] == runname,
                                 np.logical_and(statdf['query'] == entity,
                                                np.logical_and(statdf['intervalType'] == intervalType,
                                                               statdf['metric'] == metric)))]


def judgmentLevelToStr(judgementLevel):
    return 'central' if judgmentLevel == 2 else 'relevant+central'


def totalPerformance(metric):
    print '-------- Overall ', metric, '-----------'

    # compute performance per entity, then average
    macroPerf = {(team, runname):
                     [np.mean([
                         np.mean(selectMetricRunnameEntity(intervalType, metric, runname, entity)['mean']) if (
                         np.count_nonzero(
                             selectMetricRunnameEntity(intervalType, metric, runname, entity)['mean']) > 0)  else 0.0
                         for entity in entityList
                     ])
                      for intervalType in ['all', 'week', 'day']]
                 for runname in allRunnames()
                 for team in teamsForRun(runname)}

    sortedMacroPerformance = [x for x in
                              sorted(macroPerf.iteritems(), key=lambda (key, (v1, v2, v3)): v2, reverse=True)]
    for ((team, run), (v1, v2, v3)) in sortedMacroPerformance:
        print team, run, '\t', v1, v2, v3

    tableFile = "%s%s_total_stats_%s_%s.tsv" % (
    evalDir + tableDir, metric, judgmentLevelToStr(judgmentLevel), correctedToStr())
    table = [(k1, k2, v1, v2, v3) for ((k1, k2), (v1, v2, v3)) in sortedMacroPerformance]
    np.savetxt(tableFile, table, fmt='%s\t%s\t%s\t%s\t%s')
    print 'macro stats in table ', tableFile
    print tableFile


def entityPerformance(entity, metric):
    print '-------------------\n', entity, metric
    averageRunPerformancePerEntity = {(team, runname):
                                          [np.mean(
                                              selectMetricRunnameEntity(intervalType, metric, runname, entity)['mean'])
                                           for intervalType in ['all', 'week', 'day']]
                                      for runname in allRunnames()
                                      for team in teamsForRun(runname)}

    arppe = {key: (v1, v2, v3)
             for (key, (v1, v2, v3)) in averageRunPerformancePerEntity.iteritems()
             if not math.isnan(v2)}
    sortedPerformancePerEntity = [x for x in
                                  sorted(arppe.iteritems(), key=lambda ((k1, k2), (v1, v2, v3)): v2, reverse=True)]

    if (sortedPerformancePerEntity):
        for ((team, run), (v1, v2, v3)) in sortedPerformancePerEntity: print team, run, '\t', v1, v2, v3

        tableFile = "%s%s_entity_stats_%s_%s_%s.tsv" % (
        evalDir + entityTableDir, metric, targetentities.shortname(entity), judgmentLevelToStr(judgmentLevel),
        correctedToStr())
        table = [(k1, k2, v1, v2, v3) for ((k1, k2), (v1, v2, v3)) in sortedPerformancePerEntity]
        np.savetxt(tableFile, table, fmt='%s\t%s\t%s\t%s\t%s')
        print tableFile


print '-------------------'

for metric in metrics:
    totalPerformance(metric)

for metric in metrics:
    for entity in entityList:
        entityPerformance(entity, metric)


                    
