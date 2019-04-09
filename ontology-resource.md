[Concept Map](#conceptmap) [Ontology File](#ontologyfile) [Ontologies Reused](#ontologyreused) 

 <article class="mb-5" id="conceptmap">
<content>
<h2>Conceptual Model</h2>
 
   <img src="images/ConceptMap_SubjectModel.png" width="100%" height="100%">
   <p style="text-align:center;">An overview of the main classes and their property associations. Some property associations exist only upon representation of the Table 1 data, and so we highlight instances in pink</p>
 </content>

<article class="mb-5" id="ontologyfile">
<content>
<h2>Ontology Files</h2>
<ul>
<h3> Study Cohort Ontology (SCO) </h3>
<h3> Accompaniment Files </h3>
  <ul>
<li> Medications</li>
<li> Diseases</li>
<li> Lab results</li>
<li> Measures</li>
<li> Units</li>
     </ul>
  
 </ul>
 </content>
 
 
 <article class="mb-5" id="ontologyreused">
<content>
<h2> Ontologies Reused</h2>
 <p>Below we present a small Python script that can be used to fetch the child and parent hierarchy for a class, given its IRI. This script pulls in all the axioms defined on the classes as well. We leverage the powerful constructs of the <a href="https://www.w3.org/TR/rdf-sparql-query/#describe">SPARQL DESCRIBE</a> functionality to achieve this. This script outputs the RDF/XML version of the subset class tree.</p>
<ul>
 <h3><a href="https://raw.githubusercontent.com/tetherless-world/study-cohort-ontology/master/Code/MIREOT.py">MIREOT Script</a></h3>
 <pre>
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

 </pre>
 </ul>
 </content>
 
