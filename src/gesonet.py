#Generate a random graph, trying to model a social network graph

import networkx as nx
import random as rand,random
import math
import operator
import numpy as np
from names import names
import rdflib
from rdflib import Graph, RDF, RDFS, Literal
from rdflib.namespace import FOAF, DC
import uuid
import argparse
import time

#Seed the random generator
rand_s=rand.SystemRandom('seed s')
rand_t=rand.SystemRandom('t seed')

#pick two random nodes
def pick_edge(NBNODES):
    s=rand_s.randrange(0,NBNODES-1)
    t=rand_t.randrange(0,NBNODES-1)
    return (s,t)

#returns a random graph with n nodes and d edges
def randomize(n,d):
    g=nx.Graph()
    g.add_nodes_from(range(n))
    # Add random Edges
    for i in range(d):
        g.add_edge(*pick_edge(n))
    return g

#adds reflexive edges to the input graph
def make_reflexive(g):
    for n in g.nodes():
        g.add_edge(n,n)
    return g
    
# generates a density index for nodes. Nodes are ranked according to their density and associated to the cummulative ranking nodes in function of the sum of previous nodes degrees
def generate_density_index(g):  
    degrees=nx.degree(g)
    density_index=np.array([0])
    for index in range(1,g.number_of_nodes()-1):
        density_index=np.append(density_index,density_index[index-1]+degrees[index-1])
    return density_index

# Add an edge and update the density index
def add_edge(g,e,density_index):
    g.add_edge(*e);
    for x in range(e[0],e[1]):
        density_index[x]=density_index[x]+1
    for x in range(e[1]+1,g.number_of_nodes()-1):
        density_index[x]=density_index[x]+2
    sum_degrees=density_index[len(density_index)-1]
  
#Densify the network by adding nbedges
#one node is randomly selected
#the other node is selected with a probablility weighted by its density
#This favorizes the emergence of hubs in the network
def densify(g,nbedges):
    h=g
    density_index=generate_density_index(h)
    for n in range(nbedges):        
        edge=pick_edge_to_hub(h,density_index)
        add_edge(h,edge,density_index)
    return h

#pick one random node and another randomly well connected node (weighted by the node degree)
def pick_edge_to_hub(g,density_index):
    s=rand_s.choice(range(0,g.number_of_nodes()-1))
    random_index=rand_t.randrange(1,len(density_index)-1)
    i=0
    while density_index[i]<random_index:
        i=i+1    
    return (s,i)


#Expand nodes with simili-cliques sub-communities
# Each node n is exploded in a number of highly connected nodes with a probability p_clique>0.99
# The number of nodes in the simili-clique (0..clique_size) should be based on the ratio of hubs in a social network. clique_size=g.number_of_nodes/x
# Each new node ni is related to n neighbors with a probability p_neighbor=1/nbnodes_in_clique 
def clique_expansion(g,p_explosion,clique_size_max, p_clique, p_neighbor):
    h=nx.Graph()
    for n in g.nodes():
        if p_explosion>random.random():
            nbnodes=random.randrange(clique_size_max)
            for i in range(1,nbnodes+1):
                h.add_node(n+i/10.)
                h.add_edge(n,n+i/10.)
                for (s,t) in g.edges_iter(n): 
                    if p_neighbor>random.random():
                        if(s==n):
                            h.add_edge(n+(i/10.),t)
                        else:
                            h.add_edge(s,n+i/10.)
            for i in range(1,nbnodes+1):
                for j in range(i+1,nbnodes+1):
                    if p_clique>random.random():
                        h.add_edge(n+i/10.,n+j/10.)
                        
    return nx.compose(g,h)            


#Label nodes with names
def populate(g):
    labels=[names.full_name() for i in range(G.number_of_nodes())]
    mapping=dict(zip(G.nodes(),labels))
    print mapping
    g=nx.relabel_nodes(g,mapping)
    return g

#Converts the graph into a FOAF Network
def foaf(g,base_uri):
    BIO=rdflib.Namespace('http://purl.org/vocab/bio/0.1/')
    VCARD=rdflib.Namespace('http://www.w3.org/2006/vcard/ns#')
    gr=rdflib.Graph()
    depth=10 #Used to obtain URI labels with integer numbers.
    for n in g.nodes():
        pid=int(depth*n) 
        p=gr.resource(base_uri+'/person/'+str(pid))        
        person=names.Person()
        p.set(RDF.type, FOAF.Person) 
        p.set(FOAF.firstName, Literal(person.firstname))
        p.set(FOAF.familyName, Literal(person.lastname))
        birth=gr.resource(base_uri+'/date/'+person.birth_date)
        birth.set(RDF.type, BIO.Birth)
        birth.set(DC.date, rdflib.Literal(person.birth_date))
        p.set(BIO.birth, birth)
        p.set(FOAF.mbox,rdflib.Literal(person.email))
        address=gr.resource(base_uri+'/address/'+str(uuid.uuid1()))
        address.set(VCARD.streetAddress,rdflib.Literal(person.address.street))
        address.set(VCARD.locality,rdflib.Literal(person.address.city))
        address.set(VCARD.region,rdflib.Literal(person.address.state))
        p.set(VCARD.hasAddress,address)
        for s,t in g.edges_iter(n):            
            p.add(FOAF.knows,gr.resource(base_uri+'/person/'+str(int(t*depth))))
    return gr

def label(g):
    l=nx.Graph()
    labels=[]
    for i in range(g.number_of_nodes()):        
        p=names.Person()
        labels.append(p.firstname+" "+p.lastname)
    mapping=dict(zip(g.nodes(),labels))
    l=nx.relabel_nodes(g,mapping)
    return l
 
# Main   
if __name__ == "__main__":
    t1=time.time()
    
    #----------- Parsing Arguments ---------------
    parser = argparse.ArgumentParser()
    parser.add_argument("--nbnodes", help="Specify the number of nodes to start with. Each node will then be exploded into a small set of densely connected nodes. (default value=10)")
    parser.add_argument("--format", help="Specify the desired output format. Can be one of rdf-n3,rdf-xml. (default: rdf-n3)")
    parser.add_argument("--file", help="Specify a file to write the output network. (default: output.format)")
    parser.add_argument("--ns", help="Specify a namespace to use for the RDF graph (default: http://data.lirmm.fr/foaf-network/).")
    parser.add_argument("--gephi", help="Export the graph in GEXF format for drawing with Gephi. Output file output.gexf (default: false)", action='store_true')
    args = parser.parse_args()
    
    #Initial nuber of nodes to generate
    NBNODES=10

    #Numer of edges to generate
    #D=math.trunc(N*math.log(N))
    D=2*NBNODES

    if args.nbnodes:
        assert(int(args.nbnodes)>=2)        
        NBNODES=int(args.nbnodes)
    
    #------------ Network generation -----------
    print "Generating graph..."
    G=nx.Graph()   
    G=randomize(NBNODES,D) # generate random graph
    G=make_reflexive(G) #ensure every node has a minimal degree of 1
    G=densify(G,D) # densify the network while favorizing the emergence of hubs
    g=clique_expansion(G,0.5,int(math.log(NBNODES)), 0.75, 0.5) #expand the network by replacing nodes with highly connected sets of nodes representing communities
    
    #--------------- Output the network -------------------
    print "Done.\nWriting output..."
    if args.format:
        if args.format=="rdf-n3" or args.format=="rdf-xml":
            if args.ns:
                rdf=foaf(g,args.ns)
            else:
                rdf=foaf(g,'http://data.lirmm.fr/foaf-network')
            if args.format=="rdf-n3":
                if args.file:
                    rdf.serialize(args.file,format="n3")
                else:    
                    rdf.serialize('output.rdf.n3',format="n3")
            if args.format=="rdf-xml":
                if args.file:
                    rdf.serialize(args.file,format="xml")
                else:    
                    rdf.serialize('output.rdf.xml',format="xml")
        if args.format=="gml":
            if args.file:
                nx.write_gml(G,args.file)
            else:
                nx.write_gml(G,'output.gml')
    else: # Default
        if args.ns:
            rdf=foaf(g,args.ns)
        else:
            rdf=foaf(g,'http://data.lirmm.fr/foaf-network')
        if args.file:
            rdf.serialize(args.file,format="n3")
        else:    
            rdf.serialize('output.rdf.n3',format="n3")
    if args.gephi:            
        nx.write_gexf(label(g),'output.gexf')    
    print "Done. "+str(g.number_of_nodes())+" persons generated."
    t2=time.time()
    print "execution time:"+str(t2-t1)+" seconds"
    print "Ratio: "+str(g.number_of_nodes()/(t2-t1))+" persons/second"