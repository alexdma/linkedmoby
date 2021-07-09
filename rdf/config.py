#!/usr/bin/env python

import argparse, json


parser = argparse.ArgumentParser(description='Extracts MobyGames data and converts them to RDF.')
parser.add_argument("--config", metavar='C', default='config.json', help='configuration file (default: config.json)')
parser.add_argument("--page", metavar='P', default=0, type=int, help='starting offset for API calls, applies to games and groups alike (default: 0)')
parser.add_argument("types", metavar='T', default='all', nargs='*', choices=['all', 'game', 'genre', 'group', 'platform'], 
                    help='the types of entities to be extracted, in no relevant order (default: all)')
args = parser.parse_args()

with open(args.config) as f:
    print('Using configuration JSON file ' + args.config)
    config = json.load(f)
