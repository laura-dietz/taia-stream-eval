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
#COLLAPSED_JUDGMENT_FILE = os.path.expanduser(
#    '~/kba-evaluation/taia-stream-eval/data/collapsed-onlypos-trec-kba-ccr-2013-judgments-2013-09-26.filter-run.txt') # year 2
COLLAPSED_JUDGMENT_FILE = os.path.expanduser(
    '~/kba-evaluation/taia-stream-eval/data/collapsed-onlypos-trec-kba-ccr-2013-judgments-2013-09-26.filter-run-official.csv') # year 2

evalTR = 1330559999   # year 2
evalTRend = 1360368000  # year 2

#ALLTEAMS = ['CWI', 'LSIS', 'PRIS', 'SCIAITeam', 'UMass_CIIR', 'UvA', 'helsinki', 'hltcoe', 'igpi2012', 'udel_fang',
#            'uiucGSLIS']

ALLTEAMS = ['UMass_CIIR']

METRICS = ['MAP', 'nDCG@R', 'Prec@R', 'numPosPredictions', 'P10', 'P100']

MAX_DAYS = math.ceil((evalTRend - evalTR) / epochsPerDay)


ENTITIES_HAS_JUDG_NO_TWITTER = [
   "http://en.wikipedia.org/wiki/Geoffrey_E._Hinton",
   "http://en.wikipedia.org/wiki/Hoboken_Reporter",
   "http://en.wikipedia.org/wiki/Fargo-Moorhead_Symphony_Orchestra",
   "http://en.wikipedia.org/wiki/The_Ritz_Apartment_(Ocala,_Florida)",
   "http://en.wikipedia.org/wiki/Elysian_Charter_School",
   "http://en.wikipedia.org/wiki/Carla_Katz",
   "http://en.wikipedia.org/wiki/Sara_Bronfman",
   "http://en.wikipedia.org/wiki/Brenda_Weiler",
   "http://en.wikipedia.org/wiki/Olaus_Murie",
   "http://en.wikipedia.org/wiki/Jennifer_Baumgardner",
   "http://en.wikipedia.org/wiki/Jeff_Severson",
   "http://en.wikipedia.org/wiki/David_B._Danbom",
   "http://en.wikipedia.org/wiki/Carey_McWilliams_(marksman)",
   "http://en.wikipedia.org/wiki/Jamie_Parsley",
   "http://en.wikipedia.org/wiki/Innovis_Health",
   "http://en.wikipedia.org/wiki/Agroindustrial_Pomalca",
   "http://en.wikipedia.org/wiki/Corn_Belt_Power_Cooperative",
   "http://en.wikipedia.org/wiki/Susan_Krieg",
   "http://en.wikipedia.org/wiki/Barbara_Liskov",
   "http://en.wikipedia.org/wiki/Nicolas_Sch%C3%B6ffer",
   "http://en.wikipedia.org/wiki/Daniel_J._Crothers",
   "http://en.wikipedia.org/wiki/Paul_Marquart",
   "http://en.wikipedia.org/wiki/Gretchen_Hoffman",
   "http://en.wikipedia.org/wiki/Blair_Thoreson",
   "http://en.wikipedia.org/wiki/Joshua_Zetumer",
   "http://en.wikipedia.org/wiki/Jack_Lazorko",
   "http://en.wikipedia.org/wiki/William_P._Gerberding",
   "http://en.wikipedia.org/wiki/Ruben_J._Ramos",
   "http://en.wikipedia.org/wiki/Reid_Nichols",
   "http://en.wikipedia.org/wiki/Intergroup_Financial_Services",
   "http://en.wikipedia.org/wiki/Haven_Denney",
   "http://en.wikipedia.org/wiki/IDSIA",
   "http://en.wikipedia.org/wiki/Appleton_Museum_of_Art",
   "http://en.wikipedia.org/wiki/Chiara_Nappi",
   "http://en.wikipedia.org/wiki/Judd_Davis",
   "http://en.wikipedia.org/wiki/DeAnne_Smith",
   "http://en.wikipedia.org/wiki/Scot_Brantley",
   "http://en.wikipedia.org/wiki/Matt_Witten",
   "http://en.wikipedia.org/wiki/Lake_Weir_High_School",
   "http://en.wikipedia.org/wiki/L%C3%A9on_Bottou",
   "http://en.wikipedia.org/wiki/Richard_W._Goldberg",
   "http://en.wikipedia.org/wiki/Charles_Bronfman",
   "http://en.wikipedia.org/wiki/Carl_Chang_(tennis)",
   "http://en.wikipedia.org/wiki/George_Sinner",
   "http://en.wikipedia.org/wiki/Lorenzo_Williams_(basketball)",
   "http://en.wikipedia.org/wiki/Joanne_Borgella",
   "http://en.wikipedia.org/wiki/Frank_Winters",
   "http://en.wikipedia.org/wiki/Jeff_Tamarkin",
   "http://en.wikipedia.org/wiki/Stevens_Cooperative_School",
   "http://en.wikipedia.org/wiki/Bernard_Kenny",
   "http://en.wikipedia.org/wiki/Gwena%C3%ABlle_Aubry",
   "http://en.wikipedia.org/wiki/Clare_Bronfman",
   "http://en.wikipedia.org/wiki/Edgar_Bronfman,_Jr.",
   "http://en.wikipedia.org/wiki/Shafi_Goldwasser",
   "http://en.wikipedia.org/wiki/Benjamin_Bronfman",
   "http://en.wikipedia.org/wiki/Fargo_Moorhead_Derby_Girls",
   "http://en.wikipedia.org/wiki/John_D._Odegard_School_of_Aerospace_Sciences",
   "http://en.wikipedia.org/wiki/Travis_Mays",
   "http://en.wikipedia.org/wiki/Randy_Ewers",
   "http://en.wikipedia.org/wiki/Drew_Wrigley",
   "http://en.wikipedia.org/wiki/Eighth_Street_Elementary_School",
   "http://en.wikipedia.org/wiki/Zoubin_Ghahramani",
   "http://en.wikipedia.org/wiki/Red_River_Zoo",
   "http://en.wikipedia.org/wiki/SIMSA",
   "http://en.wikipedia.org/wiki/William_H._Miller_(writer)",
   "http://en.wikipedia.org/wiki/Mark_SaFranko",
   "http://en.wikipedia.org/wiki/Jasper_Schneider",
   "http://en.wikipedia.org/wiki/Hoboken_Volunteer_Ambulance_Corps",
   "http://en.wikipedia.org/wiki/Pat_Dapuzzo",
   "http://en.wikipedia.org/wiki/Fargo_Air_Museum",
   "http://en.wikipedia.org/wiki/Buddy_MacKay",
   "http://en.wikipedia.org/wiki/Dunkelvolk",
   "http://en.wikipedia.org/wiki/Atacocha",
   "http://en.wikipedia.org/wiki/Ken_Freedman",
   "http://en.wikipedia.org/wiki/John_H._Lang",
   "http://en.wikipedia.org/wiki/Hayden_Smelter",
   "http://en.wikipedia.org/wiki/Luz_del_Sur",
   "http://en.wikipedia.org/wiki/Ed_Bok_Lee",
   "http://en.wikipedia.org/wiki/Juris_Hartmanis",
   "http://en.wikipedia.org/wiki/Bob_Bert",
   "http://en.wikipedia.org/wiki/Joey_Mantia",
   "http://en.wikipedia.org/wiki/Tilo_Rivas",
   "http://en.wikipedia.org/wiki/Lewis_and_Clark_Landing",
   "http://en.wikipedia.org/wiki/Jeremy_McKinnon",
   "http://en.wikipedia.org/wiki/Phyllis_Lambert",
   "http://en.wikipedia.org/wiki/Osceola_Middle_School",
   "http://en.wikipedia.org/wiki/Klaus_Grutzka",
   "http://en.wikipedia.org/wiki/Clark_Blaise",
   "http://en.wikipedia.org/wiki/Eva_Silverstein",
   "http://en.wikipedia.org/wiki/Richard_Edlund",
   "http://en.wikipedia.org/wiki/Gran%C3%A3_y_Montero",
   "http://en.wikipedia.org/wiki/Yann_LeCun",
   "http://en.wikipedia.org/wiki/Maurice_Fitzgibbons",
   "http://en.wikipedia.org/wiki/Scotiabank_Per%C3%BA",
   "http://en.wikipedia.org/wiki/Cementos_Lima",
   "http://en.wikipedia.org/wiki/Paul_Johnsgard",
   "http://en.wikipedia.org/wiki/Joshua_Boschee",
   "http://en.wikipedia.org/wiki/Toquepala_mine",
   "http://en.wikipedia.org/wiki/Keri_Hehn",
   "http://en.wikipedia.org/wiki/Austral_Group",
   "http://en.wikipedia.org/wiki/Great_American_Brass_Band_Festival",
   "http://en.wikipedia.org/wiki/Stuart_Powell_Field",
   "http://en.wikipedia.org/wiki/Th%C3%A9o_Mercier",
   "http://en.wikipedia.org/wiki/Danny_Irmen",
   "http://en.wikipedia.org/wiki/Hjemkomst_Center",
   "http://en.wikipedia.org/wiki/Ana%C3%AFs_Croze",
   "http://en.wikipedia.org/wiki/Sean_Hampton",
   "http://en.wikipedia.org/wiki/Don_Garlits_Museum_of_Drag_Racing",
   "http://en.wikipedia.org/wiki/Copper_Basin_Railway",
   "http://en.wikipedia.org/wiki/Edgar_Bronfman,_Sr.",
   "http://en.wikipedia.org/wiki/Angelo_Savoldi",
   "http://en.wikipedia.org/wiki/Shamit_Kachru",
   "http://en.wikipedia.org/wiki/Weehawken_Cove",
   "http://en.wikipedia.org/wiki/Fernando_J._Corbat%C3%B3",
   "http://en.wikipedia.org/wiki/Derrick_Alston",
   "http://en.wikipedia.org/wiki/Jim_Poolman",
   "http://en.wikipedia.org/wiki/Marion_Technical_Institute"
]

#ENTITIES = judged100EntitiesListYear2
#ENTITIES = None # use all year2 entities with judgments
ENTITIES = ENTITIES_HAS_JUDG_NO_TWITTER
