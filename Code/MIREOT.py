from SPARQLWrapper import *
from owlready2 import *
import os

sparql_endpoint = "http://localhost:9999/bigdata/sparql"

query = '''
describe ?child ?superParent 
where {
   hint:Query hint:describeMode "CBD".
  ?child rdfs:subClassOf* ?super .
  ?super rdfs:subClassOf* ?superParent .
}
values ?super {<http://hadatac.org/ont/chear#ATIDU>}
'''

sparql_wrapper = SPARQLWrapper(sparql_endpoint)
sparql_wrapper.setQuery(query)
sparql_wrapper.setReturnFormat(RDF)
results = sparql_wrapper.query().convert()
results.serialize('output.owl', format="pretty-xml")
print("Writing results to a rdf-xml file")

