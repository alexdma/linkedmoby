#!/usr/bin/env python

import argparse, json

parser = argparse.ArgumentParser()
parser.add_argument("-C", "--config", default='config.json', help='Select configuration file (default is config.json)')
args = parser.parse_args()

with open(args.config) as f:
    print('Using configuration JSON file ' + args.config)
    config = json.load(f)