"""
Collapse the official judgment file to a ground truth.

- Remove entries with 0 confidence
- Remove entries outside the evaluation time range
- For multiple entries, use the one with minimum value
- Multiple judgment entries can exist for the same document, but different entities.
- Only retain positive judgments (relevant + central)

"""
import os.path
import numpy as np
from numpy.lib import recfunctions
from utils import *


COLLAPSED_JUDGMENT_FILE = os.path.expanduser('~/kba-evaluation/taia-stream-eval/data/collapsed-onlypos-trec-kba-ccr-2013-judgments-2013-07-08.filter-run.txt') # year 2
ORIG_JUDGMENT_FILE ='~/kba-evaluation/kba-scorer-y2/data/trec-kba-ccr-judgments-2013-07-08.before-and-after-cutoff.filter-run.txt'  # year 2
#COLLAPSED_JUDGMENT_FILE ='~/kba-evaluation/taia/data/collapsed-onlypos-trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt'  # year 1
#ORIG_JUDGMENT_FILE ='~/kba-evaluation/taia/data/trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt'  # year 1



def read_judgments(fname):
    judg_dtype = np.dtype([('dummy1','50a'),('docid', '50a'), ('query', '50a'),
                         ('conf','d4'), ('label', 'd4')])
    a = np.genfromtxt(fname, dtype=judg_dtype,usecols=[1,2,3,4,5])
    times = [int(t) for t in np.core.defchararray.partition(a['docid'], '-')[:,0]]
    aa = recfunctions.append_fields(a, 'time', times)

    conftimeFiltered = aa[np.logical_and(aa['conf']>0, np.logical_and(aa['time']>=evalTR, aa['time']<evalTRend))]
    return conftimeFiltered

def filter_doublejudgments(a, onlyPos):   
    records = []
    entityList = np.unique(a['query'])
    for entity in entityList:
        a_ent = a[a['query']==entity]
        docids = np.unique(a_ent['docid'])
        counter = 0
        for docid in docids:
            a_doc = a_ent[a_ent['docid']==docid]
            if(np.count_nonzero(np.argmin(a_doc['label'])))> 1:
                print 'we might have more than one minimum index'
                print np.argmin(a_doc['label'])
                print a_doc
            single_doc = a_doc[np.argmin(a_doc['label'])]
            if not onlyPos or single_doc['label']>0 :
                records.append(single_doc)
                counter += 1
        print entity, counter        

    df = np.hstack(records)
    return df            
            
    

j = read_judgments(os.path.expanduser(ORIG_JUDGMENT_FILE))

print 'Read %d judgements' % len(j)

a = filter_doublejudgments(j, True)

print 'Filtered %d judgements' % len(a)

#truthFile="%s/collapsed-onlypos-trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt"%(os.path.expanduser('~/kba-evaluation/taia/data/'))
np.savetxt(COLLAPSED_JUDGMENT_FILE, a,fmt='%s\t%s\t%s\t%d\t%d\t%d')
