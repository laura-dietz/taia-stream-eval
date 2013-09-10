import re
import os
import sys
import json
import time
import copy
import logging
from filenames import TOPIC_FILE

#filter_run = {
#    "$schema": "http://trec-kba.org/schemas/v1.1/filter-run.json",
#    "task_id": "kba-ccr-2013",
#    "topic_set_id": None, ## will set this below
#    "corpus_id": None, ## will set this below
#    "team_id": "CompInsights",
#    "team_name": "Computable Insights",
#    "poc_name": "TREC KBA Organizers",
#    "poc_email": "trec-kba@googlegroups.com",
#    "system_id": "toy_1",
#    "run_type": "automatic",
#    "system_description": "Entity title strings are used as surface form names, then any document containing one of the surface form names is ranked vital with confidence proportional to length of surface form name, and the longest sentence containing the longest surface form name is treated as a slot fill for all slot types for the given entity type.",
#    "system_description_short": "relevance=2, exact name match, longest sentence slot fills",
#    }

fullEntityListYear1 = [
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


def loadEntities():
    ## load entities

    filter_topics = json.load(open(TOPIC_FILE))

    ## set the topic set identifier in filter_run
    #filter_run["topic_set_id"] = filter_topics["topic_set_id"]

    ## init our toy algorithm
    allentities = [rec['target_id'] for rec in filter_topics["targets"]]
    # filter out year 1 entities
    entities = [entity for entity in allentities if not any(map(entity.endswith, fullEntityListYear1))]
    return entities