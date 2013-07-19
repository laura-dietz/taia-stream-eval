import os.path
import numpy as np
from metrics import *
import sys
import string
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime
from matplotlib.dates import DateFormatter, WeekdayLocator, MONDAY
import operator
import math
from truthutil import *
from utils import *

DEBUG = False
if len(sys.argv)>1:
    evalDir = sys.argv[1]
else:
    #evalDir = '~/kba-evaluation/taia/data/umass-runs/'
    #evalDir = '/media/dietz/bob/taia/all-runs/'
    evalDir = '~/kba-evaluation/taia/data/umass-runs/'


if len(sys.argv)>2:
    judgmentLevel = int(sys.argv[2])
else:
    print 'using judgmentLevel 2'
    judgmentLevel=1

if len(sys.argv)>3:
    CORRECTED=(sys.argv[3]=='True')
else:
    CORRECTED = False


metrics =  ['correctedAUC','MAP','nDCG@R','Prec@R','numPosPredictions']

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

hfmt = dates.DateFormatter('%m/%d')

entityColors='myb'
entityIdx=0

def correctedToStr():
    return 'WEIGHTED' if CORRECTED else 'UNIFORM'


#metric = 'nDCG@R'
#metric= 'Prec@R'

stats_dtype = np.dtype([('team','50a'),('runname','50a'),('query','50a'),('unjudged','50a'),('judgmentLevel','d4'),('metric','50a'),('mean','f4'),('stdev','f4'),('intervalType','50a')])                        



def createStatsRecord(team, runname, entity, unjudgedAs, judgmentLevel, metricname, mean, stdev, intervalType):
    return np.array([(team, runname, entity, unjudgedAs,judgmentLevel,metricname, mean, stdev, intervalType)],  dtype=stats_dtype)

records = []

intervalRunfiles = {'all':allRunfiles, 'week':weekRunfiles, 'day':dayRunfiles}

def all():
    for intervalType, runfiles in intervalRunfiles.items():
        if not runfiles:
            print intervalRunfiles
    
    for intervalType, runfiles in intervalRunfiles.items():
        for runIdx, evalFile in enumerate(runfiles[:]): 
            df = np.genfromtxt(evalFile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
            print ' processing evalFile',evalFile
            for entity in entityList:
             numberOfIntervals = {'all': numPosIntervals(judgmentLevel, entity, 'all'), 
                                  'week': numPosIntervals(judgmentLevel, entity, 'week'), 
                                  'day':  numPosIntervals(judgmentLevel, entity, 'day')} 
    
             for metric in metrics:   
                data = df[np.logical_and(df['query']==entity, 
                                         np.logical_and(df['metric']==metric, df['judgmentLevel']==judgmentLevel))]
                
                if len(data)>0:
                    #print data
                    team = data[0]['team']                                     
                    runname = data[0]['runname']
                    unjudgedAs = data[0]['unjudged']
                    unifValues = data['value']
                    
                    
                    ppdata = np.array([posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d in data])
                    
                    totalposvalues = posTruths(judgmentLevel, entity)
                    weightedValues = ppdata/totalposvalues*numberOfIntervals[intervalType]*unifValues
                    values = unifValues if not CORRECTED else weightedValues
                    #print 'used', np.mean(unifValues), np.mean(weightedValues), np.mean(values)
                    #print 'fillwithzeros',numberOfIntervals[intervalType],'-',len(values) 
                    values = values[np.nonzero(values)]
                    #print values
                    v = np.append(values, np.zeros(numberOfIntervals[intervalType]-len(values))) 
                    records.append(createStatsRecord(team, runname, entity, unjudgedAs, judgmentLevel, metric, np.mean(v), np.std(v), intervalType))
    
def test():
    for intervalType, runfiles in intervalRunfiles.items():
        if not runfiles:
            print intervalRunfiles
    
    intervalType='week'
    runfiles = intervalRunfiles[intervalType]
    for runIdx, evalFile in enumerate(runfiles[:1]): 
            df = np.genfromtxt(evalFile, dtype=eval_dtype, missing_values='', autostrip=False, delimiter='\t')
            print ' processing evalFile',evalFile
            for entity in entityList:
             numberOfIntervals = {'all':  numPosIntervals(judgmentLevel, entity, 'all'),
                                  'week': numPosIntervals(judgmentLevel, entity, 'week'), 
                                  'day':  numPosIntervals(judgmentLevel, entity, 'day')
                                 }
    
             for metric in metrics:   
                data = df[np.logical_and(df['query']==entity, 
                                         np.logical_and(df['metric']==metric, df['judgmentLevel']==judgmentLevel))]
                
                #pdata = df[np.logical_and(df['query']==entity, 
                #                         np.logical_and(df['metric']=='numPos', df['judgmentLevel']==judgmentLevel))]
                if len(data)>0:
                    #print data
                    team = data[0]['team']                                     
                    runname = data[0]['runname']
                    unjudgedAs = data[0]['unjudged']
                    unifValues = data['value']
                    
                    #print data
                    #print pdata
                    ppdata = np.array([posTruthsInterval(d['judgmentLevel'], d['query'], d['intervalLow'], d['intervalUp']) for d in data])
                    
                    totalposvalues = posTruths(judgmentLevel, entity)
                    weightedFactor = ppdata/totalposvalues*numberOfIntervals[intervalType]
                    #print ppdata, totalposvalues, numberOfIntervals[intervalType]
                    #print 'weightedFactor',np.mean(weightedFactor), weightedFactor
                    weightedValues = weightedFactor*unifValues
                    values = unifValues if not CORRECTED else weightedValues
                    #print 'used', np.mean(unifValues), np.mean(weightedValues), np.mean(values)
                    #print 'fillwithzeros',numberOfIntervals[intervalType],'-',len(values) 
                    values = values[np.nonzero(values)]
                    #print values
                    v = np.append(values, np.zeros(numberOfIntervals[intervalType]-len(values))) 
                    records.append(createStatsRecord(team, runname, entity, unjudgedAs, judgmentLevel, metric, np.mean(v), np.std(v), intervalType))
    

all()
#test()
if(records):
    statdf = np.hstack(records)


def teamsForRun(runname):
     return np.unique(statdf[statdf['runname']==runname]['team'])

def allRunnames():
    return np.unique(statdf['runname'])    

def selectMetricRunname(intervalType,metric,runname):
    return statdf[np.logical_and(statdf['runname']==runname,
                                 np.logical_and(statdf['intervalType']==intervalType,statdf['metric']==metric))]

def selectMetricRunnameEntity(intervalType,metric,runname, entity):
    return statdf[np.logical_and(statdf['runname']==runname,
                                 np.logical_and(statdf['query']==entity,
                                                np.logical_and(statdf['intervalType']==intervalType,statdf['metric']==metric)))]




        
def judgmentLevelToStr(judgementLevel):
    return 'central' if judgmentLevel==2 else 'relevant+central'


def performancePerEntityAsDict():
    averageRunPerformancePerEntity =  { (team,runname,entity): 
        [ np.mean(selectMetricRunnameEntity(intervalType,metric,runname,entity)['mean']) 
#            if ( np.count_nonzero(selectMetricRunnameEntity(intervalType,metric,runname,entity)['mean'])>0)  else 0.0 
            for intervalType in ['all','week','day']] 
        for runname in allRunnames() 
        for team in teamsForRun(runname)
        for entity in entityList}
    arppe = {key:(v1,v2,v3) 
        for (key,(v1,v2,v3)) in averageRunPerformancePerEntity.iteritems() 
        if not math.isnan(v2)}    
    sortedPerformancePerEntity = [x for x in sorted(arppe.iteritems(), key=lambda((k1,k2,k3),(v1,v2,v3)):v2, reverse=True)]

    
def macroPerformance(metric):
    print '------ Macro',metric,'-------------'

    # Micro-Performance: average across all entities, report number per team
    macroPerformance =  { (team,runname): 
        [ np.mean(selectMetricRunname(intervalType,metric,runname)['mean']) 
            if ( np.count_nonzero(selectMetricRunname(intervalType,metric,runname)['mean'])>0)  else 0.0 
            for intervalType in ['all','week','day']] 
        for runname in allRunnames() 
        for team in teamsForRun(runname) }
    sortedMacroPerformance = [x for x in sorted(macroPerformance.iteritems(), key=lambda(key,(v1,v2,v3)):v2, reverse=True)]
        
    for ((team,run),(v1,v2,v3)) in sortedMacroPerformance: print team,run,'\t',v1,v2,v3

    #print sortedPerformance


    tableFile="%s%s_macro_stats_%s_%s.tsv"%(os.path.expanduser(evalDir),metric,judgmentLevelToStr(judgmentLevel), correctedToStr())
    table = [(k1,k2,v1,v2,v3) for ((k1,k2),(v1,v2,v3)) in sortedMacroPerformance]
    np.savetxt(tableFile, table,fmt='%s\t%s\t%s\t%s\t%s')
    print tableFile


def microPerformance(metric):
    print '--------Micro ',metric,'-----------'

    # Macro-Performance: performance per team,entity, 
    microPerf=  { (team,runname): 
        [np.mean([
                np.mean(selectMetricRunnameEntity(intervalType,metric,runname,entity)['mean'])  if ( np.count_nonzero(selectMetricRunnameEntity(intervalType,metric,runname,entity)['mean'])>0)  else 0.0
                for entity in entityList
                ])
            for intervalType in ['all','week','day']] 
        for runname in allRunnames() 
        for team in teamsForRun(runname)}
    
    sortedMicroPerformance = [x for x in sorted(microPerf.iteritems(), key=lambda(key,(v1,v2,v3)):v2, reverse=True)]
    for ((team,run),(v1,v2,v3)) in sortedMicroPerformance: 
        print team,run,'\t',v1,v2,v3

    tableFile="%s%s_micro_stats_%s_%s.tsv"%(os.path.expanduser(evalDir),metric,judgmentLevelToStr(judgmentLevel), correctedToStr())
    table = [(k1,k2,v1,v2,v3) for ((k1,k2),(v1,v2,v3)) in sortedMicroPerformance]
    np.savetxt(tableFile, table,fmt='%s\t%s\t%s\t%s\t%s')
    print 'micro stats in table ',tableFile
    print tableFile


def entityPerformance(entity, metric):
    print '-------------------\n',entity, metric
    averageRunPerformancePerEntity =  { (team,runname): 
        [ np.mean(selectMetricRunnameEntity(intervalType,metric,runname,entity)['mean']) 
            for intervalType in ['all','week','day']] 
        for runname in allRunnames() 
        for team in teamsForRun(runname)}
    arppe = {key:(v1,v2,v3) 
        for (key,(v1,v2,v3)) in averageRunPerformancePerEntity.iteritems() 
        if not math.isnan(v2)}    
    sortedPerformancePerEntity = [x for x in sorted(arppe.iteritems(), key=lambda((k1,k2),(v1,v2,v3)):v2, reverse=True)]

    if(sortedPerformancePerEntity):
        for ((team,run),(v1,v2,v3)) in sortedPerformancePerEntity: print team,run,'\t',v1,v2,v3 
    
        tableFile="%s%s_entity_stats_%s_%s_%s.tsv"%(os.path.expanduser(evalDir),metric,entity,judgmentLevelToStr(judgmentLevel), correctedToStr())
        table = [(k1,k2,v1,v2,v3) for ((k1,k2),(v1,v2,v3)) in sortedPerformancePerEntity]
        np.savetxt(tableFile, table,fmt='%s\t%s\t%s\t%s\t%s')
        print tableFile



print '-------------------'



for metric in metrics:
    microPerformance(metric)

#for metric in metrics:
#    macroPerformance(metric)


for metric in metrics:
    for entity in entityList:
        entityPerformance(entity,metric)


                    
