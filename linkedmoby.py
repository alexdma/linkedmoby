'''
Created on 17 Sep 2019

@author: alexdma@apache.org

'''
import logging, requests, time
from urllib.error import HTTPError
from urllib.parse import urldefrag, urlparse

from SPARQLWrapper import SPARQLExceptions, SPARQLWrapper, JSON
from rdflib import Graph, Literal, URIRef, RDF, RDFS, XSD
from rdflib.namespace import FOAF, DCTERMS, SKOS
from requests.auth import HTTPBasicAuth

from rdf.config import args, config as cfg
from rdf.factories import LDMoby, Gaming, genre_mappings
import rdf.factories as maker

FORMAT = '[%(levelname)s] %(asctime)s. %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('dsidata')
logger.setLevel(logging.DEBUG)

API_KEY = cfg['moby']['api_key']
ENDPOINT = cfg['moby']['endpoint']
API_STEP = 100
REQ_RATE = cfg['moby']['rate']

print('Using RDF prefix for data: ' + LDMoby)
print('Extracting data of types: ' + str(args.types))
if 'all' in args.types and len(args.types) > 1 : 
    logger.warning("Value 'all' takes precedence over others when declared.")
print('HTTP request rate is set to {} requests per second'.format(REQ_RATE))
if REQ_RATE > 0.1 : 
    logger.warning("HTTP request rate is set to %s" + 
                                ", which is above the 0.1 limit (one request every ten seconds) set by MobyGames.", REQ_RATE)
    logger.warning("If you do not have special access permissions, your client could be throttled or banned.")


def moby_uri(moby_id, short_type, name=None):
    u = LDMoby
    u += short_type + '/'
    u += str(moby_id) if moby_id else name.lower().replace(' ', '_')
    return maker.preprocess(u)


def validate(uri):
    sep = ' '
    uri = uri.split(sep, 1)[0]
    u = urlparse(uri)
    if not u.scheme or not u.netloc :
        return False
    fixed, throwaway = urldefrag(uri)
    return fixed


def write(nt):
    sparql = SPARQLWrapper(cfg['storage']['sparql_update'])
    query = f"""
INSERT DATA {{ {nt} }}
"""
    sparql.setQuery(query)
    sparql.setCredentials(cfg['storage']['auth']['user'], cfg['storage']['auth']['password'])
    sparql.method = 'POST'
    sparql.query()


def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rateLimitedFunction(*args, **kargs):
            elapsed = time.perf_counter() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.perf_counter()
            return ret

        return rateLimitedFunction

    return decorate


@RateLimited(REQ_RATE)  # Default is one in ten seconds
def callMoby(resource, auth, filename=None):
    print('calling <{}> ... '.format(resource), end='')
    response = requests.get('/'.join((ENDPOINT, resource)), auth=auth)
    return response.json()


def match_wikidata(graph, game_map): 
    query = """SELECT DISTINCT ?game ?wd WHERE { VALUES( ?game ?slug) {"""
    for row in game_map:
        slug = row['moby_url'].rsplit('/', 1)[-1]
        query += """ ( <{}> "{}" )""".format(row['uri'], slug)
    query += """ } ?wd <http://www.wikidata.org/prop/direct/P1933> ?slug"""
    query += """ }"""
    wdsparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    wdsparql.method = 'POST'
    wdsparql.setQuery(query)
    wdsparql.setReturnFormat(JSON)
    try:
        results = wdsparql.query().convert()
        for bind in results['results']['bindings']:
            graph.add((URIRef(bind['game']['value']), SKOS.closeMatch, URIRef(bind['wd']['value'])))
    except HTTPError as e:
        logger.error('Failed check for Wikidata link: ' + str(e))
        logger.error('Query was: %s', query)
    return graph


def games(details=False, start_page=0):
    lastNoRes = 1
    page = start_page
    auth = HTTPBasicAuth(API_KEY, '')
    key = 'games'
    path = key
    while lastNoRes > 0 and lastNoRes <= API_STEP:
        json = callMoby(path + '?offset=' + str(API_STEP * page) + '&format=' + ('normal' if details else 'id'), auth)
        page += 1
        if key not in json:
            print('No key "' + key + '" in JSON! Printout follows')
            print(json)
        lastNoRes = len(json[key])
        print('page {} : {} {}'.format(page, lastNoRes, key))
        graph = Graph()
        id_map = []
        if details:
            for g in json[key] :
                guri = LDMoby + 'game/' + str(g['game_id'])
                game, gameplay, ui, narrative = maker.game(graph, guri, g['title'])
                if 'description' in g :
                    graph.add((game, DCTERMS.description, Literal(g['description'], datatype=RDF.HTML)))
                if 'moby_url' in g :
                    ourl = g['moby_url'].strip()
                    ourl = validate(ourl)
                    if ourl:
                        mpage = URIRef(ourl)
                        graph.add((game, FOAF.page, mpage))
                        graph.add((mpage, RDF.type, FOAF.Document))
                        id_map.append({ 'uri': guri, 'moby_url' : ourl })
                if 'official_url' in g and g['official_url'] :
                    ourl = g['official_url'].strip()
                    ourl = validate(ourl)
                    if ourl:
                        home = URIRef(ourl)
                        graph.add((game, FOAF.homepage, home))
                        graph.add((home, RDF.type, FOAF.Document))
                if 'platforms' in g :
                    for gp in g['platforms']:
                        gameplat = URIRef(guri + '/platform/' + str(gp['platform_id']))
                        plat, splat = moby_uri(str(gp['platform_id']), 'platform', gp['platform_name'])
                        graph.add((gameplat, RDF.type, Gaming.GamePlatformVersion))
                        graph.add((gameplat, RDFS.label, Literal(f""""{g['title']}" on {gp['platform_name']}""", lang='en')))
                        graph.add((gameplat, Gaming.game, game))
                        graph.add((gameplat, Gaming.platform, plat))
                        if 'first_release_date' in gp and gp['first_release_date']:
                            graph.add((gameplat, DCTERMS.date, Literal(gp['first_release_date'], datatype=XSD.date)))
                if 'genres' in g :
                    for ge in g['genres']:
                        gcdata = genre_mappings[ge['genre_category_id']]
                        if 'game' == gcdata['subject']:
                            subject = game
                        elif 'gameplay' == gcdata['subject']:
                            subject = gameplay
                        elif 'ui' == gcdata['subject']:
                            subject = ui
                        elif 'narrative' == gcdata['subject']:
                            subject = narrative
                        elif 'package' == gcdata['subject']:
                            subject = game
                        else:
                            raise Exception("Cannot handle subject type " + gcdata['subject'])
                        genre = maker.genre(graph, ge['genre_id'], ge['genre_category_id'], ge['genre_name'], ge['genre_category'])
                        graph.add((subject, gcdata['property'], genre))
        else :
            for gid in json[key] :
                guri = LDMoby + 'game/' + str(gid)
                game = maker.game(graph, guri, g['title'])
        if id_map:
            match_wikidata(graph, id_map)
        try:
            nt = graph.serialize(format='ntriples').decode('UTF-8')
            write (nt)
        except Exception as e:
            # for s,p,o in graph:
            #    print(f"""{s} {p} {o}""")
            raise e


def genres():
    """
    Genres in MobyGames encode more than just genres
    """
    lastNoRes = 1
    page = 0
    auth = HTTPBasicAuth(API_KEY, '')
    key = 'genres'
    while lastNoRes > 0 and lastNoRes <= API_STEP:
        json = callMoby(key + '?offset=' + str(API_STEP * page), auth)
        page += 1
        if key not in json:
            print('No key "' + key + '" in JSON! Printout follows')
            print(json)
        lastNoRes = len(json[key])
        print('page {} : {} {}'.format(page, lastNoRes, key))
        graph = Graph()
        for p in json[key] :
            genre = maker.genre(graph, p['genre_id'], p['genre_category_id'],
                                p['genre_name'], p['genre_category'],
                                p['genre_description'])
            # The genre category pretty much determines the property
        write (graph.serialize(format='ntriples').decode('UTF-8'))


def groups(start_page=0):
    """Extracts information of MobyGames groups

    Args:
        start_id: the first page offset to start from.
            Defaults to 0
    """
    lastNoRes = 1
    page = start_page
    auth = HTTPBasicAuth(API_KEY, '')
    key = 'groups'
    while lastNoRes > 0 and lastNoRes <= API_STEP:
        json = callMoby(key + '?offset=' + str(API_STEP * page), auth)
        page += 1
        if key not in json:
            print('No key "' + key + '" in JSON! Printout follows')
            print(json)
        lastNoRes = len(json[key])
        print('page {} : {} {}'.format(page, lastNoRes, key))
        # General group data
        graph = Graph()
        for p in json[key] :
            guri = LDMoby + 'game_group/' + str(p['group_id'])
            group = maker.group(graph, guri, p["group_name"], p["group_description"])
        write (graph.serialize(format='ntriples').decode('UTF-8'))
        # Data for group member games
        for p in json[key] :
            lastNoResGiG = 1
            pageGiG = 0
            while lastNoResGiG > 0 and lastNoResGiG <= API_STEP:
                graph = Graph()
                guri = LDMoby + 'game_group/' + str(p['group_id'])
                group = maker.group(graph, guri, p["group_name"], p["group_description"])
                groupJson = callMoby('games?group=' + str(p['group_id']) + "&format=id" + '&offset=' + str(API_STEP * pageGiG), auth)
                pageGiG += 1
                lastNoResGiG = len(groupJson['games'])
                if 'games' in groupJson:
                    print('Group {} has {} games left to process.'.format(p['group_id'], len(groupJson['games'])))
                    for game_id in groupJson['games']:
                        game = URIRef(LDMoby + 'game/' + str(game_id))
                        maker.game2group(graph, game, group)
                write (graph.serialize(format='ntriples').decode('UTF-8'))
        

def platforms():
    lastNoRes = 1
    page = 0
    auth = HTTPBasicAuth(API_KEY, '')
    key = 'platforms'
    tPlatform = URIRef(LDMoby + 'term/' + 'GamingPlatform')
    while lastNoRes > 0 and lastNoRes <= API_STEP:
        json = callMoby(key + '?offset=' + str(API_STEP * page), auth)
        page += 1
        if key not in json:
            print('No key "' + key + '" in JSON! Printout follows')
            print(json)
        lastNoRes = len(json[key])
        print('page {} : {} {}'.format(page, lastNoRes, key))
        graph = Graph()
        for p in json[key] :
            platform = URIRef(LDMoby + 'platform/' + str(p['platform_id']))
            graph.add((platform, RDF.type, tPlatform))
            graph.add((platform, RDFS.label, Literal(p['platform_name'], lang='en')))
            graph.add((platform, FOAF.name, Literal(p['platform_name'])))
        write (graph.serialize(format='ntriples').decode('UTF-8'))      


allt = 'all' in args.types         
if allt or 'platform' in args.types: platforms()
if allt or 'genre' in args.types: genres()
if allt or 'game' in args.types: games(details=True, start_page=args.page)
if allt or 'group' in args.types: groups(start_page=args.page)
