'''
Created on 2 Oct 2019

@author: alexdma@apache.org

'''
from rdflib import Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, FOAF, SKOS

from rdf.config import config as cfg


__all__ = ('CRM', 'DUL', 'Gaming', 'Schema', 'VGO', 'LDMoby',
		'game', 'game2group', 'genre', 'group', 'platform',
		'genre_mappings')

CRM = Namespace('http://erlangen-crm.org/current/')
DUL = Namespace('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#')
Gaming = Namespace('http://data.datascienceinstitute.ie/ont/gaming/term/')
Schema = Namespace('http://schema.org/')
VGO = Namespace('http://purl.org/net/VideoGameOntology#')
LDMoby = Namespace(cfg['rdf']['prefix'] if cfg['rdf']['prefix'] else 'http://example.org/linkedmoby/')

genre_mappings = {
     1 : { 
		"property" : VGO.has_game_genre,
		"subject" : "game",
		"class" : VGO.Genre,
		"shorthand" : "genre" },
     2 : { 
		"property" : Gaming.viewableFromPerspective,
		"subject" : "ui",
		"class" : Gaming.ViewingPerspective,
		"shorthand" : "view" },
     3 : { 
		"property" : Gaming.hasSport,
		"subject" : "gameplay",
		"class" : Gaming.Sport,
		"shorthand" : "sport" },
     4 : { 
		"property" : Gaming.hasGameplayType,
		"subject" : "gameplay",
		"class" : Gaming.GameplayType,
		"shorthand" : "gameplay" },
     5 : {
		"property" : Gaming.hasEducationalCapability,
		"subject" : "gameplay",
		"class" : VGO.Genre,
		"shorthand" : "genre_edu" },
     6 : { 
		"property" : Gaming.hasGameplayFeature,
		"subject" : "gameplay",
		"class" : Gaming.GameplayFeature,
		"shorthand" : "gameplay_feature" },
     7 : { 
		"property" : Gaming.hasInterfaceType,
		"subject" : "ui",
		"class" : Gaming.InterfaceType,
		"shorthand" : "interface" },
     8 : { 
		"property" : Gaming.hasNarrativeTheme,
		"subject" : "narrative",
		"class" : SKOS.Concept,
		"shorthand" : "theme" },
     9 : { 
		"property" : Gaming.hasPacing,
		"subject" : "gameplay",
		"class" : Gaming.Pacing,
		"shorthand" : "pacing" },
    10 : { 
		"property" : DUL.hasSetting,
		"subject" : "narrative",
		"class" : DUL.Setting,
		"shorthand" : "setting" },
    11 : { 
		"property" : Gaming.hasDrivableVehicleType,
		"subject" : "gameplay",
		"class" : Gaming.IngameVehicle,
		"shorthand" : "ingame_vehicle" },
    12 : { 
		"property" : Gaming.isVisuallyPresentedAs,
		"subject" : "ui",
		"class" : Gaming.VisualPresentation,
		"shorthand" : "visual" },
    13 : { 
		"property" : Gaming.hasArtStyle,
		"subject" : "game",
		"class" : Gaming.ArtStyle,
		"shorthand" : "art_style" },
    14 : { 
		"property" : Gaming.isAddonOfType,
		"subject" : "package",
		"class" : Gaming.AddonType,
		"shorthand" : "addon_type" },
    15 : { 
		"property" : Gaming.isEditionType,
		"subject" : "package",
		"class" : Gaming.EditionType,
		"shorthand" : "edition" }
}


def game(graph, uri, title, titleLocale='en-US') :
	"""
	TODO: multiple gameplays and UIs? (think about Ocean's movie licensees)
	"""
	game, sgame = preprocess(uri)
	graph.add((game, RDF.type, VGO.Game))
	lTitle = Literal(title, lang=titleLocale)
	# No dc:title yet, would rather give one to each release
	graph.add((game, RDFS.label, lTitle))
	graph.add((game, SKOS.prefLabel, lTitle))
	# Every game has a gameplay and a UI, not necessarily a narrative
	gameplay = URIRef(sgame + '/gameplay')
	ui = URIRef(sgame + '/ui')
	narrative = URIRef(sgame + '/narrative')
	graph.add((game, Gaming.hasGameplay, gameplay))	
	graph.add((gameplay, RDF.type, Gaming.Gameplay))
	graph.add((gameplay, RDFS.label, Literal(f'Gameplay of "{title}"', lang='en')))	
	graph.add((game, Gaming.hasUserInterface, ui))	
	graph.add((ui, RDF.type, Gaming.UserInterface))
	graph.add((ui, RDFS.label, Literal(f'User interface of "{title}"', lang='en')))
	graph.add((game, Gaming.hasNarrativeContext, narrative))	
	graph.add((narrative, RDF.type, Gaming.NarrativeContext))
	graph.add((narrative, RDFS.label, Literal(f'Narrative context of "{title}"', lang='en')))
	return game, gameplay, ui, narrative


def game2group(graph, game, group) :
	graph.add((game, DCTERMS.partOf, group))
	return group


def genre(graph, genre_id, cat_id, name=None, cat_name=None, desc=None) :
	if cat_id not in genre_mappings :
		raise Exception("I didn't know genre {} : {}".format(cat_id, cat_name))
	genre = URIRef(LDMoby + genre_mappings[cat_id]['shorthand'] + '/' + str(genre_id))
	graph.add((genre_mappings[cat_id]['class'], RDFS.label, Literal(cat_name, lang='en')))
	graph.add((genre, RDF.type, genre_mappings[cat_id]['class']))
	graph.add((genre, RDFS.label, Literal(name, lang='en')))
	if desc:
		graph.add((genre, DCTERMS.description, Literal(desc, lang='en')))
	# The genre category pretty much determines the property
	return genre


def group(graph, uri, name, description=None):
	group, sgroup = preprocess(uri)
	graph.add((group, RDF.type, CRM.E78_Collection))
	graph.add((group, DCTERMS.title, Literal(name, lang='en')))
	graph.add((group, RDFS.label, Literal(name, lang='en')))
	if description : graph.add((group, DCTERMS.description, Literal(description, lang='en')))
	return group


def platform(graph, uri, name) :
	plat, splat = preprocess(uri)
	tPlatform = Gaming.GamingPlatform
	graph.add((plat, RDF.type, tPlatform))
	graph.add((plat, RDFS.label, Literal(name, lang='en')))
	graph.add((plat, FOAF.name, Literal(name)))
	return plat


def preprocess(uri_obj):
	"""
	Takes an URI and generates a URIRef representation as well as a string 
	representation of it, which may be useful for making other URIs from it.

	Arguments:
		uri_obj {string or URIRef} -- the given URI for the RDF resource

	Returns:
		URIRef -- an actionable RDF resource
		string -- the string representation of the URIRef
	"""
	if isinstance(uri_obj, URIRef) :
		sgame = str(uri_obj)
		game = uri_obj
	else :
		sgame = uri_obj
		game = URIRef(uri_obj)
	return game, sgame
