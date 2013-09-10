"""
Utilities for accessing the ground truth.

You need to change the COLLAPSED_JUDGMENT_FILE variable
"""

import os.path
import numpy as np
from utils import *
import targetentities
from filenames import COLLAPSED_JUDGMENT_FILE, evalTR, evalTRend

#COLLAPSED_JUDGMENT_FILE ='~/kba-evaluation/taia/data/collapsed-onlypos-trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt'  # year 1
#COLLAPSED_JUDGMENT_FILE ='~/kba-evaluation/taia-stream-eval/data/collapsed-onlypos-trec-kba-ccr-2013-judgments-2013-07-08.filter-run.txt' # year 2


# A decorator for memoization
def memoize(f):
    def go(*args):
        k = tuple(args)
        if k in go.cache:
            return go.cache[k]
        else:
            v = f(*args)
            go.cache[k] = v
            return v
    go.cache = {}
    return go

def read_judgments(fname):
    judg_dtype = np.dtype([('docid', '50a'), ('query', '50a'),
                        ('label', 'd4'), ('time','d4')])
    a = np.genfromtxt(fname, dtype=judg_dtype,usecols=[1,2,4,5], delimiter='\t')
    # this code is not needed anymore
    return a

j = read_judgments(os.path.expanduser(COLLAPSED_JUDGMENT_FILE))
print 'Read %d judgements' % len(j)


def trueDocs(judgmentLevel, entity, intervalLow, intervalUp):
    posTruth = j[np.logical_and(j['query'] == entity, 
                 np.logical_and(j['label'] >= judgmentLevel,
                 np.logical_and(j['time'] >= intervalLow,
                                j['time'] < intervalUp)))]
    return posTruth


@memoize
def posTruthsInterval(judgmentLevel, entity, intervalLow, intervalUp):
    posTruth = j[np.logical_and(j['query'] == entity, 
                 np.logical_and(j['label'] >= judgmentLevel,
                 np.logical_and(j['time'] >= intervalLow,
                                j['time'] < intervalUp)))]
   
    numPos = 1. * len(np.unique(posTruth['docid']))
    return numPos

entityJudgments = { entity: j[j['query'] == entity]
                    for entity in np.unique(j['query']) }
allIntervals = np.vstack([intervalRange(epochsPerWeek),
                       intervalRange(epochsPerDay),
                       [(evalTR, evalTRend)]
                     ])

def posTruths(judgmentLevel, entity):        
    return posTruthsInterval(judgmentLevel, entity, evalTR, evalTRend)

@memoize
def isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp):
    if(entity in entityJudgments):
        j2 = entityJudgments[entity]

        return np.any(np.logical_and(j2['label'] >= judgmentLevel,
                      np.logical_and(j2['time'] >= intervalLow,
                                     j2['time'] < intervalUp)))
    else:
        return False

def listOfPosIntervalsForEntity(judgmentLevel, entity, intervalBounds):        
    return [(intervalLow, intervalUp) 
            for (intervalLow,intervalUp) in intervalBounds
            if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
           ]


def listOfPosIntervals(judgmentLevel, intervalBounds):        
    return [(intervalLow, intervalUp) 
            for (intervalLow,intervalUp) in intervalBounds
            if np.any( np.logical_and(j['label'] >= judgmentLevel,
                       np.logical_and(j['time'] >= intervalLow,
                                      j['time'] < intervalUp)))
           ]

intervalBounds = { judgmentLevel:
                   {'all':  listOfPosIntervals(judgmentLevel,[(evalTR, evalTRend)]),
                    'week': listOfPosIntervals(judgmentLevel,intervalRange(epochsPerWeek)), 
                    'day':  listOfPosIntervals(judgmentLevel,intervalRange(epochsPerDay))
                   } 
                   for judgmentLevel in np.unique(j['label'])
                 }

numberOfIntervals = {judgmentLevel:
                     { intervalType : len(bounds)
                       for intervalType, bounds in intervalBounds[judgmentLevel].items() }
                     for judgmentLevel in np.unique(j['label'])
                    }

@memoize
def numPosIntervals(judgmentLevel, entity, intervalType):
    if(entity in entityJudgments):
        j2 = entityJudgments[entity]
        n = sum(np.any(np.logical_and(j2['label'] >= judgmentLevel,
                       np.logical_and(j2['time'] >= intervalLow,
                                      j2['time'] < intervalUp)))
                for (intervalLow,intervalUp) in intervalBounds[judgmentLevel][intervalType])
        return n
    else:
        print 'entity does not have judgments ',entity
        return 0
    
def loadIntervals(judgmentLevel, entityList, intervalBounds):
    return {entity:{   low:
            posTruthsInterval(judgmentLevel, entity, low,up) 
            for (low,up) in intervalBounds}
        for entity in entityList}


def test():
    fullEntityList =targetentities.fullEntityListYear1

    for entity in fullEntityList:
        ##evalTR = 1325376000 # year 1
        ##evalTRend = 1338508800  # year 1
        #evalTR = 1330559999000  # year 2
        #evalTRend = 1360368000  # year 2

        intervalList = [(evalTR, evalTRend)]


        total = sum(posTruthsInterval(1, entity, low,up) for (low,up) in intervalList)        
        imm = posTruthsInterval(1, entity, evalTR, evalTRend)
        totalTruth = posTruths(1,entity)
        print (totalTruth-total),'totalTruths',totalTruth, 'summed total',total, imm, entity

