#!/usr/bin/env python
# -*- coding: utf-8 -*-

# example usage
# python real.py --intervalType week --judgmentLevel 1 -f ~/kba-evaluation/taia/data/umass-runs/UMass_CIIR-PC_RM20_1500.gz


import os.path
import numpy as np
from numpy.lib import recfunctions
import gzip
from metrics import *
import sys
import string
from utils import *
from truthutil import *
from argparse import ArgumentParser

        
DEBUG=False        
DUMP_TREC_EVAL=False        
        
metrics = {
'nDCG@R': ndcgREval,'Prec@R': precREval, 'correctedAUC':normalizeAUC, 'MAP':mapEval, 'extendedAUC':normalizeExtendedAUC}

#intervalType = 'all'
#judgmentLevel = 1

runFile = '~/kba-evaluation/taia/data/umass-runs/UMass_CIIR-PC_RM20_1500.gz'        
    #runFile = '/media/dietz/bob/taia/all-runs/input.UMass_CIIR-PC_RM20_1500.gz'



parser = ArgumentParser()
parser.add_argument('--intervalType', default='all')
parser.add_argument('--judgmentLevel', type=int, help='Judgement level', default=1)
parser.add_argument('-f', '--runFile', metavar='FILE', default=runFile)
args = parser.parse_args()

judgmentLevel = args.judgmentLevel
intervalType = args.intervalType
runFile = args.runFile


        
        
entry_dtype = np.dtype([('runname','50a'),('docid', '50a'), ('query', '50a'),
                        ('confidence', 'd4')])
judg_dtype = np.dtype([('docid', '50a'), ('query', '50a'),
                        ('label', 'd4')])
eval_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('intervalLow','d4'),('intervalUp','d4'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('value','f4')])                        
#trec_eval_dtype = np.dtype([('query','50a'),('runname','50a'),('docid','50a'),('rank','d4'),('score','f4'),('desc','50a')])                        

def read_predictions(fname):
    a = np.genfromtxt(fname, dtype=entry_dtype,comments='#', usecols=[1,2,3,4])
    print 'read %d predictions' % len(a)
    times = [int(t) for t in np.core.defchararray.partition(a['docid'], '-')[:,0]]
    return recfunctions.append_fields(a, 'time', times)
        

def read_judgments(fname):
    a = np.genfromtxt(fname, dtype=judg_dtype,usecols=[2,3,5])
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
    

team, runname = readPredictionsHeader(os.path.expanduser(runFile))
print team, runname

a = read_zipped_predictions(os.path.expanduser(runFile))

testEntityList = [     'Boris_Berezovsky_(businessman)',    'Boris_Berezovsky_(pianist)',    'Alex_Kapranos',    'James_McCartney' ]
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

#epochsPerWeek = int(6.048E5)
#epochsPerDay = 86400
#epochsPerInterval = epochsPerWeek
#evalTR = 1325376000
#evalTRend = 1338508800

if DEBUG: entityList = testEntityList

#starts = range(evalTR, evalTRend, epochsPerInterval)
#intervalList = [(start, start + epochsPerInterval) for start in starts]
#intervalList = [(1325379600,1328058000)]#, (0, 1371517333)]


sliceBy = ('day' if epochsPerDay == epochsPerInterval else 'week' if epochsPerWeek == epochsPerInterval else 'other')

#j= read_judgments(os.path.expanduser('~/kba-evaluation/taia/data/trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt'))
#judgments = { (entity, intervalLow): j[np.logical_and(j['query'] == entity, 
#                     np.logical_and(j['time'] >= intervalLow, j['time'] < intervalUp))]
#          for entity in entityList
#          for (intervalLow, intervalUp) in intervalList
#        } 

#resultsPerIntervall = [{} for interval in intervalList]


records = []

print runFile

def createEvalRecord(entity, intervalLow, intervalUp, unjudgedAs, judgmentLevel, metricname, score):
    return np.array([(team, runname, entity, intervalLow, intervalUp, unjudgedAs,judgmentLevel,metricname, score)],  dtype=eval_dtype)


runOutputFile = None
if DUMP_TREC_EVAL :
    runOutputFilename="%s-%s.run"%(os.path.expanduser(runFile),sliceBy)
    runOutputFile = open(runOutputFilename,'w')


for entity in entityList:
    
    intervalList = intervalBounds[judgmentLevel][intervalType]
 
    for (i, (intervalLow, intervalUp)) in enumerate(intervalList):
        # segment data 
        all = a[a['query'] == entity]
        #slice = a[np.logical_and(a['query'] == entity, a['time'] >= intervalLow, a['time'] < intervalUp)]
        slice = all[np.logical_and(all['time'] >= intervalLow, all['time'] < intervalUp)]
        if(len(slice)>0):
            # sort by confidence and revert (highest first)        
          slice = np.sort(slice, order='confidence')[::-1]


        #groundtruth = j[np.logical_and(j['query'] == entity, np.logical_and(j['time'] >= intervalLow, j['time'] < intervalUp))]
        #posGroundTruth = groundtruth[groundtruth['label']>=judgmentLevel]
        posGroundTruth = trueDocs(judgmentLevel, entity, intervalLow, intervalUp)
        
        numPos = len(posGroundTruth)
        #numNeg = len(groundtruth) - numPos
        if DEBUG: print entity, i, judgmentLevel, 'pos:', numPos, 'neg:', numNeg, 'data:',len(slice), 'alldata', len(all)
        judgedPosSlice = np.array([np.count_nonzero(posGroundTruth['docid']==elem['docid']) > 0 for elem in slice])
        
        if DUMP_TREC_EVAL:
            for i,row in enumerate(slice):
                #score = np.log2(1.0/(i+2.0))
                score = float(row['confidence'])
                rank = i+1
                runOutputFile.write("%s\t%s\t%s\t%d\t%f\t%s\n"%(entity, intervalType, row['docid'],rank,score,row['runname']))

        
        #unjudgedSlice = np.array([np.count_nonzero(groundtruth['docid']==elem['docid']) == 0 for elem in slice])
        ##unjudgedAsPosSlice = np.logical_or(unjudgedSlice, judgedPosSlice)
        unjudgedAsNegSlice = judgedPosSlice
        numNeg = len(slice) - numPos        
        
        records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numPos', numPos))
        records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numNeg', numNeg))
        records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numPredictions', len(slice)))
        records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 
                                        'numPosPredictions', sum(judgedPosSlice)))
        records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'posTruthsInterval', posTruthsInterval(judgmentLevel,entity, intervalLow, intervalUp)))
        records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 
                                        'posTruthsTotal', posTruths(judgmentLevel, entity)))
        records.append(createEvalRecord(entity, 
                                        intervalLow, 
                                        intervalUp, '', 
                                        judgmentLevel, 
                                        'numPosIntervals',
                                        numPosIntervals(judgmentLevel, entity, intervalType)))
        
         
        #records.append(createEvalRecord(entity, intervalLow, intervalUp, '', judgmentLevel, 'numUnjudgedPredictions', sum(unjudgedSlice)))
        if numPos>0:
            if len(slice)>0:
                for metricname, metric in metrics.items():
                    score = metric(unjudgedAsNegSlice, numPos, numNeg)
                    #x = np.array([(team, runname, entity, intervalLow, intervalUp, 'neg',metricname, score)],  dtype=eval_dtype)            
                    records.append(createEvalRecord(entity, intervalLow, intervalUp, 'neg', judgmentLevel, metricname, score))
            else :
                for metricname in metrics:
                    records.append(createEvalRecord(entity, intervalLow, intervalUp, 'neg', judgmentLevel, metricname, 0.0))

# needs fixing, numPos is wrong
#            for metricname, metric in metrics.items():
#                score = metric(unjudgedAsPosSlice, numPos, numNeg)
#                x = np.array([(entity, intervalLow, intervalUp, 'pos',metricname, score)],  dtype=eval_dtype)            
#                records.append(x)

print runFile

if DUMP_TREC_EVAL: runOutputFile.close()

df= np.hstack(records)

evalFile="%s-eval-%s.tsv"%(os.path.expanduser(runFile),intervalType)
np.savetxt(evalFile, df,fmt='%s\t%s\t%s\t%d\t%d\t%s\t%d\t%s\t%f')


#ndcgRAll = df[np.logical_and(df['unjudged']=='neg', df['metric']=='nDCG@R')]['value']
print runFile

for entity in entityList:
  for judgmentLevel in [1]:
    ndcgR = df[np.logical_and(df['query']==entity,
                              np.logical_and(df['unjudged']=='neg',
                                             np.logical_and(df['judgmentLevel']==judgmentLevel, df['metric']=='MAP')))]['value']
    print entity, judgmentLevel
    print ndcgR
    if(len(ndcgR)>0):
        print np.mean(ndcgR)


for judgmentLevel in [1]:
  for metric in metrics:
    print 'all','judgmentLevel =',judgmentLevel
    ndcgR = df[np.logical_and(df['unjudged']=='neg',
                                             np.logical_and(df['judgmentLevel']==judgmentLevel, df['metric']==metric))]['value']
    print ndcgR
    if(len(ndcgR)>0):
        print metric, np.mean(ndcgR)
    
