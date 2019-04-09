[Concept Map](#conceptmap) [Ontology File](#ontologyfile) [Ontologies Reused](#ontologyreused) 

 <article class="mb-5" id="conceptmap">
<content>
<h2>Conceptual Model</h2>
 
   <img src="images/ConceptMap_SubjectModel.png" width="100%" height="100%">
   <p style="text-align:center;">An overview of the main classes and their property associations. Some property associations exist only upon representation of the Table 1 data, and so we highlight instances in pink</p>
 </content>

<article class="mb-5" id="ontologyfile">
<content>
<h2>Ontologies</h2>
<ul>
<h3> Study Cohort Ontology (SCO) </h3>
 <h4> Definitions </h4>
 <ul type = "disc">
 <li>Research Study 
  <ul type = "circle">
  <li> Definition: A scientific investigation that involves testing a hypothesis </li>
  <li> Immediate Superclass: None </li>
  <li> Example: "10-Year Follow-up of Intensive Glucose Control in Type 2 Diabetes"</li>
  <li> Reused From: Hasco</li>
  </ul>
  </li>

  
  <li>Clinical Trial
  <ul type = "circle">
  <li> Definition: A prospective study designed to evaluate whether one or more interventions are associated with an outcome</li>
  <li> Immediate Superclass: Research Study</li>
  <li> Example: "10-Year Follow-up of Intensive Glucose Control in Type 2 Diabetes"</li>
  <li> Reused From: National Cancer Institute Thesarus (NCIT) </li>
  </ul>
  </li>
  
    
  <li>Cohort
  <ul type = "circle">
  <li> Definition: A cohort is the group of subjects enrolled in a study</li>
  <li> Immediate Superclass: None</li>
  <li> Example: Randomized Cohort in "10-Year Follow-up of Intensive Glucose Control in Type 2 Diabetes"</li>
  <li> Reused From: The Statistical Methods Ontology (STATO)</li>
  </ul>
  </li>
  
  
  <li>Study Arm
  <ul type = "circle">
  <li> Definition: A group or subgroup of participants in a clinical trial that receives a specific intervention/treatment, or no intervention, according to the trial's protocol</li>
  <li> Immediate Superclass: Cohort</li>
  <li> Example: Metformin Conventional Therapy Arm</li>
  <li> Reused From: None</li>
  </ul>
  </li>
  
  <li>Study Subject
  <ul type = "circle">
  <li> Definition: A person who receives medical attention, care, or treatment, or who is registered with medical professional or institution with the purpose to receive medical care when necessary</li>
  <li> Immediate Superclass: None</li>
  <li> Example: African American Male Subject in "10-Year Follow-up of Intensive Glucose Control in Type 2 Diabetes"</li>
  <li> Reused From: SemanticScience Integrated Ontology (SIO)</li>
  </ul>
  </li>
  
  <li>Study Intervention
  <ul type = "circle">
  <li> Definition: A process or action that is the focus of a clinical study. Interventions include drugs, medical devices, procedures, vaccines, and other products that are either investigational or already available</li>
  <li> Immediate Superclass: None</li>
  <li> Example: Metformin</li>
  <li> Reused From: ProvCaRe </li>
  </ul>
  </li>
  
  <li>Subject Characteristic
  <ul type = "circle">
  <li> Definition: Property that summarizes important attributes of the participants enrolled in a study</li>
  <li> Immediate Superclass: None</li>
  <li> Example: Age</li>
  <li> Reused From: None</li>
  </ul>
  </li>
  
  <li>Statistical Measure
  <ul type = "circle">
  <li> Definition: a standard unit used to express the size, amount, or degree of something</li>
  <li> Immediate Superclass: None</li>
  <li> Example: Mean</li>
  <li> Reused From: ProvCaRe</li>
  </ul>
  </li>
  
 </ul>
 
 
<h3> Accompanying Suite of Ontologies </h3>

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
<ul>
 <h3><a href="https://raw.githubusercontent.com/tetherless-world/study-cohort-ontology/master/Code/MIREOT.py">MIREOT Script</a></h3>
  <p>Below we present a small Python script that can be used to fetch the child and parent hierarchy for a class, given its IRI. This script pulls in all the axioms defined on the classes as well. We leverage the powerful constructs of the <a href="https://www.w3.org/TR/rdf-sparql-query/#describe">SPARQL DESCRIBE</a> functionality to achieve this. This script outputs the RDF/XML version of the subset class tree.</p>
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
 
