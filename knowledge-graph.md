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
<h2> Link to Table 1 KG </h2>
<ul>
   <h3> MIREOT Script </h3>
 </ul>
 </content>


 <article class="mb-5" id="modelingexample">
<h2> Modeling Examples</h2>
<ul>
   <h3> Modeling of Collections of Study Subjects </h3>
 
 ```ruby
   sco-i:RamiprilArm
        a                      owl:Class, sco:InterventionArm; 
        rdfs:subClassOf        sio:StudySubject;
        sio:isParticipantIn    sco-i:TelmisartanRamiprilStudy;   
       sio:hasAttribute    
       [ a sco:PopulationSize; sio:hasValue 8576] .
  ```
   <h3> Modeling of Subject Characteristics </h3>
   <h3> Modeling of Aggregations on Subject Characteristics</h3>
 </ul>

