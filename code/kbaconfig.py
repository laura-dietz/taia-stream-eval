import os.path
import math

epochsPerWeek = int(6.048E5)
epochsPerDay = 86400

# ----- year 1 ---------
#COLLAPSED_JUDGMENT_FILE =os.path.expanduser('~/kba-evaluation/taia/data/collapsed-onlypos-trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt')  # year 1
#ORIG_JUDGMENT_FILE ='~/kba-evaluation/taia/data/trec-kba-ccr-2012-judgments-2012JUN22-final.filter-run.txt'  # year 1

#evalTR = 1325376000 # year 1
#evalTRend = 1338508800  # year 1
#ALLTEAMS = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang', 'uiucGSLIS']

#MAX_DAYS = 110

# ----- year 2 ------

TOPIC_FILE = '/home/dietz/kbbridge/code/kba-y2/data/trec-kba-ccr-and-ssf-2013-04-22/trec-kba-ccr-and-ssf-query-topics-2013-04-08.json'
ORIG_JUDGMENT_FILE = '/home/dietz/kba-evaluation/kba-scorer-y2/data/trec-kba-ccr-judgments-2013-09-26-expanded-with-ssf-inferred-vitals-plus-len-clean_visible.before-and-after-cutoff.filter-run.txt'  # year 2
COLLAPSED_JUDGMENT_FILE = os.path.expanduser(
    '~/kba-evaluation/taia-stream-eval/data/collapsed-onlypos-trec-kba-ccr-2013-judgments-2013-09-26.filter-run.txt') # year 2

evalTR = 1330559999   # year 2
evalTRend = 1360368000  # year 2

#ALLTEAMS = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang',
#            'uiucGSLIS']

ALLTEAMS = ['UMass_CIIR']

METRICS = ['MAP', 'nDCG@R', 'Prec@R', 'numPosPredictions']

MAX_DAYS = math.ceil((evalTRend - evalTR) / epochsPerDay)



#ENTITIES = judged100EntitiesListYear2
ENTITIES = None # use all year2 entities with judgments
