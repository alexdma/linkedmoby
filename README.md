# MobyGames Linked Data generator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Tools to build an RDF dataset out of the MobyGames database, http://mobygames.com/

You are free to use, modify and redistribute this tool under the terms of the [License](LICENSE). However, you are __not permitted__ to redistribute the data generated using this tool unless otherwise authorised by MobyGames.

Please do __NOT__ contact us asking for the data or for a MobyGames API key: contact Simon Carless and the other MG folks instead, they're really nice guys.

## Features
* Extraction of data on games, game groups, platforms and genres
* Reverse linking with Wikidata
* Writing to SPARQL endpoints, even if behind Basic HTTP Authentication.

## Requirements
1. An API key for the MobyGames HTTP API. For more information on how to obtain one, check out https://www.mobygames.com/info/api
2. Python 3 and pip
3. A SPARQL endpoint where you can perform UPDATE operations

## Building
1. Clone this repo
2. `python setup.py install` or `pip install -r requirements.txt`

## Running
1. Create a `config.json` file where the [config.sample.json](config.sample.json) resides and complete it accordingly (especially by filling in the MobyGames API key and SPARQL UPDATE endpoint).
2. `python linkedmoby.py`

For additional options, check the output of `python linkedmoby.py -h`.
