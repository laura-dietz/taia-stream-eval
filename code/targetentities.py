import json
import kbaconfig



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
    if not kbaconfig.ENTITIES is None:
        return kbaconfig.ENTITIES
    else :
        ## load entities

        filter_topics = json.load(open(kbaconfig.TOPIC_FILE))

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
    short = entity[entity.rindex("/") + 1:]
    return short