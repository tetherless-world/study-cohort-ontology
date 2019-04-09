[Scenario Queries](#scenarioquery) [Value Retrieval Query for Visualization](#visualization) 

<article class="mb-5" id="scenarioquery">
<content>
<h2>Scenario Queries</h2>
<ul>
    <h3> Study Match: Is there a study that matches this patient on a feature (s)? </h3>
    <strong> Query 1: PARQL Query to fetch study titles that match a patient's race and gender </strong>
   <pre>
    PREFIX resource: <http://semanticscience.org/resource/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX chear: <http://hadatac.org/ont/chear#>
    PREFIX ncit: <http://purl.obolibrary.org/obo/NCIT_>

	SELECT DISTINCT ?studyTitle ?study WHERE 
	{
  		?study a sco:ClinicalTrial .
  		?study dct:title ?studyTitle .
  		?study sio:hasParticipant ?studyArm .
  		?studyArm sio:hasProperty ?studyIntervention .
  
  		{

  			?subPatient rdfs:subClassOf ?studyArm .
  			?subPatient rdfs:subClassOf ?restriction .
  			?restriction a owl:Restriction .
  			?restriction owl:someValuesFrom ncit:C16352 .
  
	}
  	{

  		?subPatient1 rdfs:subClassOf ?studyArm .
  		?subPatient1 rdfs:subClassOf ?restriction1 .
  		?restriction1 a owl:Restriction .
  		?restriction1 owl:someValuesFrom sio:Male .
  
	}
 
    }
  </pre>
    
   <h3> Study Limitations: Are there absence or underrepresentation of population groups in this study? </h3>
   <h3> Study Quality Evaluation: Are there adequate population sizes and is there a heterogeneity of treatment effect among arms? </h3> 
 </ul>
 </content>
 
 
 <article class="mb-5" id="visualization">
<content>
<h2> Value Retrieval Query for Visualization </h2>
<ul>
   <h3>  Star Plot Code </h3>
    <p>We present a query below that is used to retrieve the central value,  and upper and lower bounds for continuous characteristics of a study arm. The characteristics are those that overlap with the patient features that we gather for diabetic patients in NHANES, i.e. age, body mass index, systolic blood pressure, diastolic blood pressure, Hemoglobin A1C. This query is triggered in the faceted browser to generate the visualization.<br>
    This query can flexibly retrieve values for both mean +/- standard deviation, median and interquartile range representations with being agnostic of the expression of the characteristic. Also, if we were to constrain the query for values of other parameters, we would just included them in the filter clause. Hence, this query is a generalized faceted browser query.</p> 
    <p>The star plot code can be browsed at: <a href="https://raw.githubusercontent.com/tetherless-world/study-cohort-ontology/master/Code/starplot.py"><small>https://raw.githubusercontent.com/tetherless-world/study-cohort-ontology/master/Code/starplot.py</small></a></p>
    <pre>
PREFIX sco: <small><https://idea.tw.rpi.edu/projects/heals/studycohort/></small>
PREFIX resource: <http://semanticscience.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX chear: <http://hadatac.org/ont/chear#>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX stato: <http://purl.obolibrary.org/obo/STATO_>
PREFIX ncit: <http://purl.obolibrary.org/obo/NCIT_>

SELECT DISTINCT ?studyTitle ?propType ?lowerBound ?propVal
?upperBound WHERE {

  ?study a sco:ClinicalTrial .
  ?study dct:title ?studyTitle .
  ?study sio:hasParticipant ?studyArm .
  ?studyArm sio:hasAttribute | sio:hasProperty ?prop .
     { 
       ?prop a ?propType .
       ?prop sio:hasAttribute ?attr .
       ?attr a sio:Mean .
       ?attr sio:hasValue ?propVal .  
       ?prop sio:hasAttribute ?attr2 .
       ?attr2 a sio:StandardDeviation .
       ?attr2 sio:hasValue ?propVal2 .   
       BIND((?propVal2  + ?propVal) AS ?upperBound) .
       BIND((?propVal  - ?propVal2) AS ?lowerBound) . 
     } 
      UNION 
    { 
       ?prop a ?propType .
  	   ?prop sio:hasAttribute ?attr .
       ?attr a sio:Median .
       ?attr sio:hasValue ?propVal .  
       ?prop sio:hasAttribute ?attr2 .
      ?attr2 a stato:0000164 .
      ?prop sio:hasAttribute sio:MaximalValue .
      ?attr2 sio:hasValue ?upperBound .
      ?prop sio:hasAttribute sio:MinimalValue .
      ?attr2 sio:hasValue ?lowerBound .   
    }
   FILTER  (
    ?propType IN (
       sio:Age,
       ncit:C64796,
       sco:SystolicBloodPressure, 
       sco:DiastolicBloodPressure
   ) ).
   
}
    </pre>
 </ul>
 </content>
