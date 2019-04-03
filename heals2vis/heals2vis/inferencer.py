import autonomic
from rdflib import *
from slugify import slugify
from nanopub import Nanopublication
import json
import config
import rdflib

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
sioc_types = Namespace("http://rdfs.org/sioc/types#")
sioc = Namespace("http://rdfs.org/sioc/ns#")
sio = autonomic.sio
dc = autonomic.dc
np = autonomic.np
prov = autonomic.prov
whyis = autonomic.whyis
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
seerkb = Namespace("http://idea.rpi.edu/heals/kb/seer#")
ncit = Namespace("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#")
pr = Namespace("http://purl.obolibrary.org/obo/PR_")
cst = Namespace("http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#")
uberon = Namespace("http://purl.obolibrary.org/obo/UBERON_")
hasco = Namespace("http://hadatac.org/ont/hasco#")
setl = rdflib.Namespace("http://purl.org/twc/vocab/setl/")
pv = rdflib.Namespace("http://purl.org/net/provenance/ns#")
skos = rdflib.Namespace("http://www.w3.org/2008/05/skos#")

class Infer(autonomic.UpdateChangeService):
    activity_class = whyis.StagingAgent

    def getInputClass(self):
        return pv.File

    def getOutputClass(self):
        return setl.SETLedFile

    def get_query(self):
        return "SELECT ?resource WHERE {?resource ?p ?o .} LIMIT 1"

    def process(self, i, o):
        #npub = Nanopublication(store=o.graph.store) 
        for inferencer in config.Config['inferencers']:
            deductor_instance = config.Config['inferencers'][inferencer]
            #print deductor_instance
            if hasattr(deductor_instance,'construct') and hasattr(deductor_instance,'where')  : 
                 deductor_instance.process_graph(self.app.db)
                #npub = Nanopublication(store=deductor_instance.graph.store) 
        #        triples = self.app.db.query('''%s CONSTRUCT {\n%s\n} WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\n}''' %( deductor_instance.prefixes, deductor_instance.construct, deductor_instance.where, deductor_instance.construct ))
        #        for s, p, o, c in triples:
        #            print "Inferencer Adding ", s,p,o
        #            npub.assertion.add((s, p, o))
        #        npub.provenance.add((npub.assertion.identifier, skos.editorialNote, rdflib.Literal(deductor_instance.explanation)))
