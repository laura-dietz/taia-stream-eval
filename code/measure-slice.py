#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Measure performance for a run file, an intervalType (day,week, all), and a judgmentLevel (1 or 2).

Creates the output next to the input file, appending "-eval-week.tsv" (for weeks)

 example usage
 python measure-slice.py --intervalType week --judgmentLevel 1 -f ~/kba-evaluation/taia/data/umass-runs/UMass_CIIR-PC_RM20_1500.gz
"""

import os.path
import numpy as np
from numpy.lib import recfunctions
import gzip
import string
from argparse import ArgumentParser
import csv
import tempfile

from metrics import *
from truthutil import *
from targetentities import *


DEBUG = False

metrics = {
    'nDCG@R': ndcgREval, 'Prec@R': precREval, 'MAP': mapEval}

runFile = '~/kba-evaluation/taia/data/umass-runs/UMass_CIIR-PC_RM20_1500.gz'

parser = ArgumentParser()
parser.add_argument('--intervalType', help='slice segmentation: day, week, or all', default='all')
parser.add_argument('--judgmentLevel', type=int, help='Judgement level', default=1)
parser.add_argument('--trec_eval', action='store_true', help='Also create output for evaluation with trec_eval',
                    default=False)
parser.add_argument('-f', '--runFile', metavar='FILE', default=runFile)
args = parser.parse_args()

judgmentLevel = args.judgmentLevel
intervalType = args.intervalType
runFile = args.runFile
DUMP_TREC_EVAL = args.trec_eval  # also create output for trec_eval.

entry_dtype = np.dtype([('runname', '50a'), ('docid', '50a'), ('query', '50a'),
                        ('confidence', 'd4')])
judg_dtype = np.dtype([('docid', '50a'), ('query', '50a'),
                       ('label', 'd4')])
eval_dtype = np.dtype(
    [('team', '50a'), ('runname', '50a'), ('query', '50a'), ('intervalLow', 'd4'), ('intervalUp', 'd4'),
     ('unjudged', '50a'), ('judgmentLevel', 'd4'), ('metric', '50a'), ('value', 'f4')])


class Annotations(object):
    """ represents a set of annotations that have been sorted by entity.
        We do this on disk to keep the memory footprint down. """

    def __init__(self, fname):
        #print 'generating prediction cache for', fname.filename
        self.entity_files = {}

        annotation_file = csv.reader(fname, delimiter='\t')
        for line in annotation_file:
            if len(line) < 4: continue
            entity = line[3]
            if entity not in self.entity_files:
                self.entity_files[entity] = tempfile.NamedTemporaryFile(prefix='kba', delete=True)
            self.entity_files[entity].write('\t'.join(line) + '\n')

        print 'indexed predictions for %d entities' % (len(self.entity_files))

    def get_predictions(self, entity):
        if entity not in self.entity_files:
            return None
        f = self.entity_files[entity]
        f.seek(0)
        a = np.genfromtxt(f, dtype=entry_dtype, usecols=[1, 2, 3, 4])
        #print 'read %d predictions' % len(a)
        times = [int(t) for t in np.core.defchararray.partition(a['docid'], '-')[:, 0]]
        return recfunctions.append_fields(a, 'time', times)


def read_judgments(fname):
    a = np.genfromtxt(fname, dtype=judg_dtype, usecols=[2, 3, 5])
    times = [int(t) for t in np.core.defchararray.partition(a['docid'], '-')[:, 0]]
    return recfunctions.append_fields(a, 'time', times)


def read_zipped_predictions(fname):
    with gzip.open(fname) as f:
        return Annotations(f)


def readPredictionsHeader(fname):
    f = gzip.open(fname, mode='r')
    firstline = f.readline()
    secondline = f.readline()
    team, runname, rest = string.split(secondline, maxsplit=2)
    f.close()
    return (team, runname)


team, runname = readPredictionsHeader(os.path.expanduser(runFile))
print team, runname

testEntityList = ['Boris_Berezovsky_(businessman)', 'Boris_Berezovsky_(pianist)', 'Alex_Kapranos', 'James_McCartney']

entityList = loadEntities()

if DEBUG: entityList = testEntityList

records = []

print runFile


def createEvalRecord(entity, intervalLow, intervalUp, unjudgedAs, judgmentLevel, metricname, score):
    return np.array([(team, runname, entity, intervalLow, intervalUp, unjudgedAs, judgmentLevel, metricname, score)],
                    dtype=eval_dtype)


runOutputFile = None
if DUMP_TREC_EVAL:
    runOutputFilename = "%s-%s.run" % (os.path.expanduser(runFile), intervalType)
    runOutputFile = open(runOutputFilename, 'w')

print 'measuring slices for ', os.path.expanduser(runFile)
annotations = read_zipped_predictions(os.path.expanduser(runFile))

for entity in entityList:
    #print 'fetching annotations for entity',entity

    a = annotations.get_predictions(entity)
    intervalList = intervalBounds[judgmentLevel][intervalType]

    for (i, (intervalLow, intervalUp)) in enumerate(intervalList):
        posGroundTruth = trueDocs(judgmentLevel, entity, intervalLow, intervalUp)

        numPos = len(posGroundTruth)

        if numPos > 0:
            # a is None if there are no judgments for this entity in this run
            if a is None:
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numPos', numPos))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numNeg', 0))
                records.append(
                    createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numPredictions', 0))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel,
                                                'numPosPredictions', 0))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'posTruthsInterval',
                                                posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp)))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel,
                                                'posTruthsTotal', posTruths(judgmentLevel, entity)))
                records.append(createEvalRecord(entity,
                                                intervalLow,
                                                intervalUp, '',
                                                judgmentLevel,
                                                'numPosIntervals',
                                                numPosIntervals(judgmentLevel, entity, intervalType)))

                for metricname in metrics:
                    records.append(
                        createEvalRecord(entity, intervalLow, intervalUp, 'neg', judgmentLevel, metricname, 0.0))


            else: # a is not None
                # segment data
                slice = a[np.logical_and(a['time'] >= intervalLow, a['time'] < intervalUp)]
                if (len(slice) > 0):
                # sort by confidence and revert (highest first)
                    slice = np.sort(slice, order=['confidence'])[::-1]

                if DUMP_TREC_EVAL:
                    for i, row in enumerate(slice):
                        score = float(row['confidence'])
                        rank = i + 1
                        runOutputFile.write(
                            "%s\t%s\t%s\t%d\t%f\t%s\n" % (
                            entity, intervalType, row['docid'], rank, score, row['runname']))

                judgedPosSlice = np.array(
                    [np.count_nonzero(posGroundTruth['docid'] == elem['docid']) > 0 for elem in slice])
                unjudgedAsNegSlice = judgedPosSlice
                numNeg = len(slice) - numPos
                if DEBUG: print entity, i, judgmentLevel, 'pos:', numPos, 'neg:', numNeg, 'data:', len(slice)

                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numPos', numPos))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numNeg', numNeg))
                records.append(
                    createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numPredictions', len(slice)))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel,
                                                'numPosPredictions', sum(judgedPosSlice)))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'posTruthsInterval',
                                                posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp)))
                records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel,
                                                'posTruthsTotal', posTruths(judgmentLevel, entity)))
                records.append(createEvalRecord(entity,
                                                intervalLow,
                                                intervalUp, '',
                                                judgmentLevel,
                                                'numPosIntervals',
                                                numPosIntervals(judgmentLevel, entity, intervalType)))

                if len(slice) > 0:
                    for metricname in metrics:
                        metric = metricsMap[metricname]
                        score = metric(unjudgedAsNegSlice, numPos, numNeg)
                        records.append(
                            createEvalRecord(entity, intervalLow, intervalUp, 'neg', judgmentLevel, metricname, score))
                else:
                    for metricname in metrics:
                        records.append(
                            createEvalRecord(entity, intervalLow, intervalUp, 'neg', judgmentLevel, metricname, 0.0))

print runFile

if DUMP_TREC_EVAL:
    runOutputFile.close()

df = np.hstack(records)

evalFile = "%s-eval-%s.tsv" % (os.path.expanduser(runFile), intervalType)
np.savetxt(evalFile, df, fmt='%s\t%s\t%s\t%d\t%d\t%s\t%d\t%s\t%f')

print runFile

for entity in entityList:
    for judgmentLevel in [1]:
        ndcgR = df[np.logical_and(df['query'] == entity,
                                  np.logical_and(df['unjudged'] == 'neg',
                                                 np.logical_and(df['judgmentLevel'] == judgmentLevel,
                                                                df['metric'] == 'MAP')))]['value']
        print entity, judgmentLevel
        print ndcgR
        if len(ndcgR) > 0:
            print np.mean(ndcgR)

for judgmentLevel in [1]:
    for metric in metrics:
        print 'all', 'judgmentLevel =', judgmentLevel
        ndcgR = df[np.logical_and(df['unjudged'] == 'neg',
                                  np.logical_and(df['judgmentLevel'] == judgmentLevel, df['metric'] == metric))][
            'value']
        print ndcgR
        if len(ndcgR) > 0:
            print metric, np.mean(ndcgR)
