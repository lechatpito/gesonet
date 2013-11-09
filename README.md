GESONET
=======

gesonet.py: a Python program to generate random social networks. Yes, random people having connections between them.
Connections are made to be realistic: my friends are often friends and we all follow famous people.
Install: python setup.py install

usage: gesonet.py [-h] [--nbnodes NBNODES] [--format FORMAT] [--file FILE]
                  [--ns NS] [--gephi]

optional arguments:
  -h, --help         show this help message and exit
  --nbnodes NBNODES  Specify the number of nodes to start with. Each node
                     will then be exploded into a small set of densely
                     connected nodes. (default value=10)
  --format FORMAT    Specify the desired output format. Can be one of rdf-n3
                     ,rdf-xml. (default: rdf-n3)
  --file FILE        Specify a file to write the output network. (default:
                     output.[format])
  --ns NS            Specify a namespace to use for the RDF graph (default:
                     http://data.lirmm.fr/foaf-network/).
  --gephi            Export the graph in GEXF format for drawing with Gephi.
                     File name may be passed as the argument value. Output file output.gexf (default:
                     false)

Description: This program generates social networks with a realistic touch. Personal information for each node of the network is generated using the Python module Names which generates names, and other personal information based on US census data. 
The structure of the network, that is the relations between individuals is generated according to the following algorithm:
 1) a random network of size NBNODES is generated
 2) a number of nodes is randomly selected and connected to another node. The most connected is a node, the most chances it has to be selected and connected with a randomly chosen node. This step enable the emergence of hubs or highly connected individuals in the network.
 3) each node has a probability to be exploded in a number of nodes. The new nodes have a very high probability to be linked to the other new nodes and are always connected to the source node. Each node also has a probability to be connected to the source node's neighbors.
This step enable the emergence of communities in the network. 

So far this process is not recursive and thus only generates realistic networks if the number of nodes is not to large, say between 10k and 100k source nodes.   

Disclaimer: See the Names module disclaimer. The network structure is random and never based on real personal data. 


