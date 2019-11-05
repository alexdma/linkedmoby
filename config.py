#!/usr/bin/env python

import argparse, json

parser = argparse.ArgumentParser(description='Extracts MobyGames data and converts them to RDF')
parser.add_argument("--config", default='config.json', help='Configuration file (default: config.json)')
parser.add_argument("--page", default=0, type=int, help='Starting offset for API calls -- applies to games and groups alike (default: 0)')
args = parser.parse_args()

with open(args.config) as f:
    print('Using configuration JSON file ' + args.config)
    config = json.load(f)
