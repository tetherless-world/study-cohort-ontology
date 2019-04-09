[Annotated Table 1 Example](#annotatedtable) [Link to Table 1 KG ](#linktotable) [Modeling Examples](#modelingexample) 

<article class="mb-5" id="annotatedtable">
<content>
<h2>Annotated Table 1 Example</h2>
<img src="images/Table1Example2.png">
  <p style="text-align:center">An annotated example of Table 1 from a clinical trial "Telmisartan, ramipril, or
both in patients at high risk for vascular events" [50] cited in the Cardiovascular Complications (Chapter 9) of the ADA 2018 CPG</p>
<ul>
  
 </ul>
 </content>
 
 
 <article class="mb-5" id="linktotable">
<content>
<h2>Table 1 KG </h2>
<ul>
  <img src="images/rdfviewer.png">
  <p style="text-align:right">Image generated using the RDF Viewer tool hosted at <a href="http://jimmccusker.github.io/rdfviewer/"><small>http://jimmccusker.github.io/rdfviewer/</small></a></p>
  <p style="text-align:center">Visualizing the RDF representation for an age characteristic with the descriptive statistics for the Ramipril study arm, of the "Telmisartan, ramipril, or
both in patients at high risk for vascular events" clinical trial</p>
 </ul>
  <p><strong>Knowledge graph of Table 1s for the various papers -> <a href="https://raw.githubusercontent.com/tetherless-world/study-cohort-ontology/master/KnowledgeGraph/Table1KG"><small>https://raw.githubusercontent.com/tetherless-world/study-cohort-ontology/master/KnowledgeGraph/Table1KG</small></a></strong> </p>
 </content>


<article class="mb-5" id="modelingexample">
  <content>
<h2> Modeling Examples</h2>
<ul>
   <h3> Modeling of Collections of Study Subjects </h3>
  
   <strong> Listing 1: Sample RDF N-Triples representation snippet of the Ramipril intervention arm </strong>
   <pre>
   sco-i:RamiprilArm
        a                      owl:Class, sco:InterventionArm; 
        rdfs:subClassOf        sio:StudySubject;
        sio:isParticipantIn    sco-i:TelmisartanRamiprilStudy;   
       sio:hasAttribute    
       [ a sco:PopulationSize; sio:hasValue 8576] .
  </pre>
  
  <strong> Listing 2: Representation of a sub-population within a study arm </strong>
   <pre>
  sco-i:AsianSubPopulation a owl:Class;
        rdfs:subClassOf sco-i:RamiprilArm;
        rdfs:subClassOf 
        [ 
            a owl:Restriction; 
            owl:onProperty sio:hasAttribute;
            owl:someValuesFrom chear:Asian
        ];
     sio:hasAttribute
     [ 
        a sco:PopulationSize; 
        sio:hasValue 1182; 
        sio:hasAttribute 
        [ 
            a sio:Percentage; 
            sio:hasValue 13.8 
        ] 
    ] .
    </pre>

   <h3> Modeling of Subject Characteristics </h3>
   
   <strong> Listing 1: Representation of a continuous characteristic on  the Ramipril Study Arm </strong>
   <pre>
   sco-i:RamiprilArm
        a    owl:Class, sio:InterventionGroup; 
        rdfs:subClassOf        sio:StudySubject;
        sio:isParticipantIn    sco-i:TelmisartanRamiprilStudy;   
       sio:hasAttribute    
       [ a sco:PopulationSize; 
       sio:hasValue 8576],
        [ a sio:Age; sio:hasUnit sio:Year
        ] . 
  </pre>
  
  <strong> Listing 2: Representation of a categorical characteristic on  the Ramipril Study Arm</strong>
   <pre>
  sco-i:PeripheralArteryDiseaseSubPopulation a owl:Class;
        rdfs:subClassOf sco-i:RamiprilArm;
        rdfs:subClassOf [ a owl:Restriction; 
        owl:onProperty sio:hasAttribute;
         owl:someValuesFrom doid:PeripheralArteryDisease];
     sio:hasAttribute [ 
        a sco:PopulationSize; 
        sio:hasValue 1136; 
        sio:hasAttribute [
            a sio:Percentage; 
            sio:hasValue 13.2 
        ] 
    ] .
    </pre>
   
   
   <h3> Modeling of Aggregations on Subject Characteristics</h3>
    <strong> Listing 1: Representation of a descriptive statistics measures of mean +/- standard deviation on Age</strong>
     <pre>
  sco-i:RamiprilArm
        a    owl:Class, sio:InterventionGroup; 
        rdfs:subClassOf        sio:StudySubject;
        sio:isParticipantIn    sco-i:TelmisartanRamiprilStudy;   
       sio:hasAttribute    [ a sco:PopulationSize; sio:hasValue 8576],
        [ a sio:Age; sio:hasUnit sio:Year;
          sio:hasAttribute [ a sio:Mean; sio:hasValue 66.4],
           [a sio:StandardDeviation; sio:hasValue 7.2 ]  
        ] . 
        
   </pre>
  
  <strong> Listing 2: Representation of a descriptive statistics measure of median +/- interquartile range</strong>
   <pre>
  sco-i:XStudyArm
    a owl:Class, sio:InterventionGroup;
    rdfs:subClassOf sio:StudySubject; 
    sio:hasAttribute
        [
          a sio:Age; sio:hasUnit sio:Year;
          sio:hasAttribute [
            a sio:Median;
            sio:hasValue 56
          ], 
          [
            a obo:STATO_0000164; 
            sio:hasAttribute 
            [ a sio:MinimalValue; sio:hasValue 75],
            [ a sio:MaximalValue; sio:hasValue 45] 
          ] 
        ] .
    </pre>
   
   
   
 </ul>
 </content>
 
  


