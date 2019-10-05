# MobyGames Linked Data generator

Tools to build an RDF dataset out of the MobyGames database.

Unless otherwise authorised by MobyGames, you are not allowed to republish the actual data.

Please do NOT contact us to ask for the data or a MobyGames API key: contact Simon and the MG folks instead, they're a smashing bunch of chaps.

# Requirements
1. An API key for the MobyGames HTTP API
2. Python 3 and pip
3. A SPARQL endpoint where you can perform UPDATE operations

# Building
1. Clone this repo
2. `pip install -r requirements.txt`

# Running
1. Create a `config.js file `here the `config.sample.js` resides and complete it accordingly (especially by filling in the MobyGames API key and SPARQL UPDATE endpoint).
2. `python mobyrdf.py`

