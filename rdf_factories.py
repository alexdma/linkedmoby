'''
Created on 2 Oct 2019

@author: alexdma@apache.org

'''
from rdflib import Literal, Namespace, OWL, RDF, RDFS, URIRef, XSD
from rdflib.namespace import DCTERMS, SKOS

CRM = Namespace('http://erlangen-crm.org/current/')
Gaming = Namespace('http://data.datascienceinstitute.ie/ont/gaming/term/')
VGO = Namespace('http://purl.org/net/VideoGameOntology#')


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
	graph.add((game, Gaming.hasGameplay, gameplay))	
	graph.add((gameplay, RDF.type, Gaming.Gameplay))
	graph.add((gameplay, RDFS.label, Literal('Gameplay of "' + title + '"', lang='en')))	
	graph.add((game, Gaming.hasInterface, ui))	
	graph.add((ui, RDF.type, Gaming.UserInterface))
	graph.add((ui, RDFS.label, Literal('User interface of "' + title + '"', lang='en')))
	return game


def game2group(graph, game, group) :
	graph.add((game, DCTERMS.partOf, group))
	return group


def group(graph, uri, name, description=None):
	group, sgroup = preprocess(uri)
	graph.add((group, RDF.type, CRM.E78_Collection))
	graph.add((group, DCTERMS.title, Literal(name, lang='en')))
	graph.add((group, RDFS.label, Literal(name, lang='en')))
	if description : graph.add((group, DCTERMS.description, Literal(description, lang='en')))
	return group


def preprocess(uri_obj):
	if isinstance(uri_obj, URIRef) :
		sgame = str(uri_obj)
		game = uri_obj
	else :
		sgame = uri_obj
		game = URIRef(uri_obj)
	return game, sgame
