#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import numpy as np
from numpy.lib import recfunctions
import gzip
from metrics import *
import sys
import string
        
DEBUG=False        
        
metrics = {
'nDCG@R': ndcgREval,'Prec@R': precREval, 'correctedAUC':normalizeAUC, 'MAP':mapEval}
        
        
entry_dtype = np.dtype([('docid', '50a'), ('query', '50a'),
                        ('confidence', 'd4')])
judg_dtype = np.dtype([('docid', '50a'), ('query', '50a'),
                        ('label', 'd4')])
eval_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('intervalLow','d4'),('intervalUp','d4'),('unjudged','50a'),('metric','50a'),('value','f4')])                        

def read_predictions(fname):
    a = np.genfromtxt(fname, dtype=entry_dtype,comments='#', usecols=[2,3,4])
    times = [int(t) for t in np.core.defchararray.partition(a['docid'], '-')[:,0]]
    return recfunctions.append_fields(a, 'time', times)
        

def read_judgments(fname):
    a = np.genfromtxt(fname, dtype=judg_dtype,usecols=[2,3,6])
    times = [int(t) for t in np.core.defchararray.partition(a['docid'], '-')[:,0]]
    return recfunctions.append_fields(a, 'time', times)
        

def read_zipped_predictions(fname):
    with gzip.open(fname) as f:
        return read_predictions(f)


def readPredictionsHeader(fname):
    f = gzip.open(fname, mode='r')
    firstline = f.readline()
    secondline = f.readline()
    team,runname, rest = string.split(secondline, maxsplit=2)
    f.close()
    return (team, runname)
    

if len(sys.argv)>1:
    runFile = sys.argv[1]
else:
    runFile = '~/kba-evaluation/taia/data/umass-runs/UMass_CIIR-FS_NV_6000.gz'        


team, runname = readPredictionsHeader(os.path.expanduser(runFile))
print team, runname

#a = read_zipped_predictions(os.path.expanduser(runFile))

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
entityList = fullEntityList

epochsPerWeek = int(6.048E5)
epochsPerDay = 86400
epochsPerInterval = epochsPerDay
evalTR = 1325376000
evalTRend = 1338508800

if DEBUG: entityList = testEntityList

starts = range(evalTR, evalTRend, epochsPerInterval)
intervalList = [(start, start + epochsPerInterval) for start in starts]
#intervalList = [(1325379600,1328058000)]#, (0, 1371517333)]

j= read_judgments(os.path.expanduser('~/kba-evaluation/taia/data/trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt'))
judgments = { (entity, intervalLow): j[np.logical_and(j['query'] == entity, 
                     np.logical_and(j['time'] >= intervalLow, j['time'] < intervalUp))]
          for entity in entityList
          for (intervalLow, intervalUp) in intervalList
        } 

resultsPerIntervall = [{} for interval in intervalList]


records = []

print runFile

def createEvalRecord(entity, intervalLow, intervalUp, unjudgedAs, metricname, score):
    return np.array([(team, runname, entity, intervalLow, intervalUp, unjudgedAs,metricname, score)],  dtype=eval_dtype)


for entity in entityList:
    for (i, (intervalLow, intervalUp)) in enumerate(intervalList):
            # sort by confidence and revert (highest first)        
            groundtruth = j[np.logical_and(j['query'] == entity, np.logical_and(j['time'] >= intervalLow, j['time'] < intervalUp))]
            posGroundTruth = groundtruth[groundtruth['label']>0]
            numPos = len(posGroundTruth)
            numNeg = len(groundtruth) - numPos
            print numPos, numNeg, len(groundtruth)
    print '\n\n\n\n\n\n'


