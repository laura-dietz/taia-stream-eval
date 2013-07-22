import os.path
import numpy as np
from numpy.lib import recfunctions
from utils import *

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
    #a = np.genfromtxt(fname, dtype=judg_dtype,usecols=[2,3,5,6], delimiter='\t') # old format
    a = np.genfromtxt(fname, dtype=judg_dtype,usecols=[1,2,4,5], delimiter='\t')
    # this code is not needed anymore
    #times = [int(t) for t in np.core.defchararray.partition(a['docid'], '-')[:,0]]
    #return recfunctions.append_fields(a, 'time', times)
    return a

j = read_judgments(os.path.expanduser('~/kba-evaluation/taia/data/collapsed-onlypos-trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt'))
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
    j2 = entityJudgments[entity]
    
    return np.any(np.logical_and(j2['label'] >= judgmentLevel,
                  np.logical_and(j2['time'] >= intervalLow,
                                 j2['time'] < intervalUp)))

def listOfPosIntervalsForEntity(judgmentLevel, entity, intervalBounds):        
    return [(intervalLow, intervalUp) 
            for (intervalLow,intervalUp) in intervalBounds
            if isPosIntervalForEntity(judgmentLevel, entity, intervalLow, intervalUp)
           ]

#def listOfPosIntervalsForEntity(judgmentLevel, entity, intervalBounds):        
#    return [(intervalLow, intervalUp) 
#            for (intervalLow,intervalUp) in intervalBounds
#            if np.count_nonzero( j[np.logical_and(j['query'] == entity, 
#                                   np.logical_and(j['label'] >= judgmentLevel,
#                                   np.logical_and(j['time'] >= intervalLow,
#                                                  j['time'] < intervalUp)))]) > 0                                                                    
#           ]


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
#print intervalBounds

numberOfIntervals = {judgmentLevel:
                     { intervalType : len(bounds)
                       for intervalType, bounds in intervalBounds[judgmentLevel].items() }
                     for judgmentLevel in np.unique(j['label'])
                    }

@memoize
def numPosIntervals(judgmentLevel, entity, intervalType):
    j2 = entityJudgments[entity]
    n = sum(np.any(np.logical_and(j2['label'] >= judgmentLevel,
                   np.logical_and(j2['time'] >= intervalLow,
                                  j2['time'] < intervalUp)))
            for (intervalLow,intervalUp) in intervalBounds[judgmentLevel][intervalType])
    return n
    
def loadIntervals(judgmentLevel, entityList, intervalBounds):
    return {entity:{   low:
            posTruthsInterval(judgmentLevel, entity, low,up) 
            for (low,up) in intervalBounds}
        for entity in entityList}


def test():
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
    for entity in fullEntityList:
        evalTR = 1325376000
        evalTRend = 1338508800
        
        intervalList = [(1325376000, 1338508800)]

#        for (low,up) in intervalList:
#            print 'posTruthsInterval', posTruthsInterval(1, 'Aharon_Barak', low,up)
    
        total = sum(posTruthsInterval(1, entity, low,up) for (low,up) in intervalList)        
        imm = posTruthsInterval(1, entity, evalTR, evalTRend)
        totalTruth = posTruths(1,entity)
        print (totalTruth-total),'totalTruths',totalTruth, 'summed total',total, imm, entity

#test()    
