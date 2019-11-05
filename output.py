'''
Created on 16 Oct 2019

@author: alexdma@apache.org

'''

from SPARQLWrapper import SPARQLExceptions, SPARQLWrapper, JSON


def write(graph, update_endpoint, user=None, pw=None):
    sparql = SPARQLWrapper(update_endpoint)
    nt = graph.serialize(format='ntriples').decode('UTF-8')
    query = f"""
INSERT DATA {{ {nt} }}
"""
    sparql.setQuery(query)
    sparql.setCredentials(user, pw)
    sparql.method = 'POST'
    sparql.query()
    
    