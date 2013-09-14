import re
import os
import sys
import json
import time
import copy
import logging
from kbaconfig import TOPIC_FILE

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

#
#entity does not have judgments  http://en.wikipedia.org/wiki/Stuart_Powell_Field
#entity does not have judgments  http://en.wikipedia.org/wiki/Corn_Belt_Power_Cooperative
#entity does not have judgments  http://en.wikipedia.org/wiki/Fargo-Moorhead_Symphony_Orchestra
#entity does not have judgments  http://en.wikipedia.org/wiki/John_D._Odegard_School_of_Aerospace_Sciences
#entity does not have judgments  http://en.wikipedia.org/wiki/Star_Lite_Motel
#entity does not have judgments  http://en.wikipedia.org/wiki/Elysian_Charter_School
#entity does not have judgments  http://en.wikipedia.org/wiki/Stevens_Cooperative_School
#entity does not have judgments  http://en.wikipedia.org/wiki/Lewis_and_Clark_Landing
#entity does not have judgments  http://en.wikipedia.org/wiki/Appleton_Museum_of_Art
#entity does not have judgments  http://en.wikipedia.org/wiki/Don_Garlits_Museum_of_Drag_Racing
#entity does not have judgments  http://en.wikipedia.org/wiki/Eighth_Street_Elementary_School
#entity does not have judgments  http://en.wikipedia.org/wiki/Marion_Technical_Institute
#entity does not have judgments  http://en.wikipedia.org/wiki/The_Ritz_Apartment_(Ocala,_Florida)
#entity does not have judgments  http://en.wikipedia.org/wiki/Great_American_Brass_Band_Festival
#entity does not have judgments  http://en.wikipedia.org/wiki/Hoboken_Volunteer_Ambulance_Corps
#entity does not have judgments  http://en.wikipedia.org/wiki/Agroindustrial_Pomalca
#entity does not have judgments  http://en.wikipedia.org/wiki/Intergroup_Financial_Services
#entity does not have judgments  https://twitter.com/GandBcoffee
#entity does not have judgments  https://twitter.com/evvnt
#entity does not have judgments  https://twitter.com/AlexJoHamilton
#entity does not have judgments  https://twitter.com/danvillekyengr
#entity does not have judgments  http://en.wikipedia.org/wiki/Carey_McWilliams_(marksman)
#entity does not have judgments  http://en.wikipedia.org/wiki/Fargo_Moorhead_Derby_Girls
#entity does not have judgments  http://en.wikipedia.org/wiki/Ken_Fowler
#entity does not have judgments  http://en.wikipedia.org/wiki/Chiara_Nappi
#entity does not have judgments  http://en.wikipedia.org/wiki/Henry_Gutierrez
#entity does not have judgments  http://en.wikipedia.org/wiki/Klaus_Grutzka
#entity does not have judgments  http://en.wikipedia.org/wiki/William_H._Miller_(writer)
#entity does not have judgments  http://en.wikipedia.org/wiki/Chuck_Pankow
#entity does not have judgments  http://en.wikipedia.org/wiki/Lorenzo_Williams_(basketball)
#entity does not have judgments  https://twitter.com/redmondmusic
#entity does not have judgments  https://twitter.com/MissMarcel
unjudgedEntityListYear2 = [
    'http://en.wikipedia.org/wiki/Stuart_Powell_Field'
    , 'http://en.wikipedia.org/wiki/Corn_Belt_Power_Cooperative'
    , 'http://en.wikipedia.org/wiki/Fargo-Moorhead_Symphony_Orchestra'
    , 'http://en.wikipedia.org/wiki/John_D._Odegard_School_of_Aerospace_Sciences'
    , 'http://en.wikipedia.org/wiki/Star_Lite_Motel'
    , 'http://en.wikipedia.org/wiki/Elysian_Charter_School'
    , 'http://en.wikipedia.org/wiki/Stevens_Cooperative_School'
    , 'http://en.wikipedia.org/wiki/Lewis_and_Clark_Landing'
    , 'http://en.wikipedia.org/wiki/Appleton_Museum_of_Art'
    , 'http://en.wikipedia.org/wiki/Don_Garlits_Museum_of_Drag_Racing'
    , 'http://en.wikipedia.org/wiki/Eighth_Street_Elementary_School'
    , 'http://en.wikipedia.org/wiki/Marion_Technical_Institute'
    , 'http://en.wikipedia.org/wiki/The_Ritz_Apartment_(Ocala,_Florida)'
    , 'http://en.wikipedia.org/wiki/Great_American_Brass_Band_Festival'
    , 'http://en.wikipedia.org/wiki/Hoboken_Volunteer_Ambulance_Corps'
    , 'http://en.wikipedia.org/wiki/Agroindustrial_Pomalca'
    , 'http://en.wikipedia.org/wiki/Intergroup_Financial_Services'
    , 'https://twitter.com/GandBcoffee'
    , 'https://twitter.com/evvnt'
    , 'https://twitter.com/AlexJoHamilton'
    , 'https://twitter.com/danvillekyengr'
    , 'http://en.wikipedia.org/wiki/Carey_McWilliams_(marksman)'
    , 'http://en.wikipedia.org/wiki/Fargo_Moorhead_Derby_Girls'
    , 'http://en.wikipedia.org/wiki/Ken_Fowler'
    , 'http://en.wikipedia.org/wiki/Chiara_Nappi'
    , 'http://en.wikipedia.org/wiki/Henry_Gutierrez'
    , 'http://en.wikipedia.org/wiki/Klaus_Grutzka'
    , 'http://en.wikipedia.org/wiki/William_H._Miller_(writer)'
    , 'http://en.wikipedia.org/wiki/Chuck_Pankow'
    , 'http://en.wikipedia.org/wiki/Lorenzo_Williams_(basketball)'
    , 'https://twitter.com/redmondmusic'
    , 'https://twitter.com/MissMarcel'
    , 'http://en.wikipedia.org/wiki/Fernando_J._Corbat%C3%B3'
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
    #return entities  # uncomment this line, if you want to include entities without judgments.

    # filter out entities without any positive judgments
    judgedEntities = [entity for entity in entities if not entity in unjudgedEntityListYear2]
    return judgedEntities



def shortname(entity):
    short = entity[entity.rindex("/")+1:]
    return short