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
ORIG_JUDGMENT_FILE = '~/kba-evaluation/kba-scorer-y2/data/trec-kba-ccr-judgments-2013-07-08.before-and-after-cutoff.filter-run.txt'  # year 2
COLLAPSED_JUDGMENT_FILE = os.path.expanduser(
    '~/kba-evaluation/taia-stream-eval/data/collapsed-onlypos-trec-kba-ccr-2013-judgments-2013-07-08.filter-run.txt') # year 2

evalTR = 1330559999   # year 2
evalTRend = 1360368000  # year 2

#ALLTEAMS = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang',
#            'uiucGSLIS']

ALLTEAMS = ['UMass_CIIR']

METRICS = ['MAP', 'nDCG@R', 'Prec@R', 'numPosPredictions']

MAX_DAYS = math.ceil((evalTRend - evalTR) / epochsPerDay)


judged100EntitiesListYear2 = [
'http://en.wikipedia.org/wiki/Atacocha',
'http://en.wikipedia.org/wiki/Barbara_Liskov',
'http://en.wikipedia.org/wiki/Blair_Thoreson',
'http://en.wikipedia.org/wiki/Bob_Bert',
'http://en.wikipedia.org/wiki/Buddy_MacKay',
'http://en.wikipedia.org/wiki/Carla_Katz',
'http://en.wikipedia.org/wiki/Charles_Bronfman',
'http://en.wikipedia.org/wiki/Corn_Belt_Power_Coope',
'http://en.wikipedia.org/wiki/David_B._Danbom',
'http://en.wikipedia.org/wiki/DeAnne_Smith',
'http://en.wikipedia.org/wiki/Drew_Wrigley',
'http://en.wikipedia.org/wiki/Ed_Bok_Lee',
'http://en.wikipedia.org/wiki/Edgar_Bronfman,_Jr.',
'http://en.wikipedia.org/wiki/Edgar_Bronfman,_Sr.',
'http://en.wikipedia.org/wiki/Fargo-Moorhead_Sympho',
'http://en.wikipedia.org/wiki/Fargo_Air_Museum',
'http://en.wikipedia.org/wiki/Geoffrey_E._Hinton',
'http://en.wikipedia.org/wiki/George_Sinner',
'http://en.wikipedia.org/wiki/Gretchen_Hoffman',
'http://en.wikipedia.org/wiki/Hjemkomst_Center',
'http://en.wikipedia.org/wiki/IDSIA',
'http://en.wikipedia.org/wiki/Jasper_Schneider',
'http://en.wikipedia.org/wiki/Jennifer_Baumgardner',
'http://en.wikipedia.org/wiki/Jim_Poolman',
'http://en.wikipedia.org/wiki/Joshua_Boschee',
'http://en.wikipedia.org/wiki/Joshua_Zetumer',
'http://en.wikipedia.org/wiki/Judd_Davis',
'http://en.wikipedia.org/wiki/Lewis_and_Clark_Landi',
'http://en.wikipedia.org/wiki/Paul_Marquart',
'http://en.wikipedia.org/wiki/Red_River_Zoo',
'http://en.wikipedia.org/wiki/Richard_Edlund',
'http://en.wikipedia.org/wiki/Ruben_J._Ramos',
'http://en.wikipedia.org/wiki/Scotiabank_Per%C3%BA',
'http://en.wikipedia.org/wiki/The_Ritz_Apartment_(O',
'http://en.wikipedia.org/wiki/Weehawken_Cove',
'http://en.wikipedia.org/wiki/Yann_LeCun',
'https://twitter.com/BlossomCoffee',
'https://twitter.com/FrankandOak',
'https://twitter.com/KentGuinn4Mayor',
'https://twitter.com/RonFunches',
'https://twitter.com/roryscovel',
'https://twitter.com/tonyg203',
'https://twitter.com/urbren00'
]

#ENTITIES = judged100EntitiesListYear2
ENTITIES = None # use all year2 entities with judgments
