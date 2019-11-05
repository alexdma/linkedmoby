# MobyGames Linked Data generator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Tools to build an RDF dataset out of the MobyGames database, http://mobygames.com/

You are free to use and redistribute this tool under the terms of the [License](LICENSE). However, unless otherwise authorised by MobyGames, you are __not allowed__ to redistribute the data generated using this tool.

Please do NOT contact us to ask for the data or a MobyGames API key: contact Simon Carless and the other MG folks instead, they're really nice guys.

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
2. `pip install -r requirements.txt`

## Running
1. Create a `config.js` file where the `config.sample.js` resides and complete it accordingly (especially by filling in the MobyGames API key and SPARQL UPDATE endpoint).
2. `python mobyrdf.py`

For additional options, check `python mobyrdf.py -h`.
