<head>
    <meta charset="utf-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vega</title>
    <meta name="description" content="Vega is a declarative format for creating, saving, and sharing visualization designs. With Vega, visualizations are described in JSON, and generate interactive views using either HTML5 Canvas or SVG.">

    <!-- Twitter card -->
    <meta name="twitter:card" value="summary_large_image">
    <meta name="twitter:site" value="@uwdata">
    <meta name="twitter:creator" value="@uwdata">
    <meta name="twitter:url" value="https://vega.github.io/">
    <meta name="twitter:title" value="Vega: A Visualization Grammar">
    <meta name="twitter:description" value="Vega is a declarative format for creating, saving, and sharing visualization designs. With Vega, visualizations are described in JSON, and generate interactive views using either HTML5 Canvas or SVG.">
    <meta name="twitter:image" value="https://vega.github.io/images/vg.png">

    <!--facebook open graph-->
    <meta property="og:type" content="article">
    <meta property="og:title" content="Vega: A Visualization Grammar">
    <meta property="og:url" content="https://vega.github.io/">
    <meta property="og:description" content="Vega is a declarative format for creating, saving, and sharing visualization designs. With Vega, visualizations are described in JSON, and generate interactive views using either HTML5 Canvas or SVG.">
    <meta property="og:site_name" content="Vega">
    <meta property="og:image" content="https://vega.github.io/images/vg.png">

    <link rel="shortcut icon" href="favicon.ico" />
    <link rel="stylesheet" type="text/css" href="css/main.css" />
</head>


<div class="container-fluid p-0">

    <section class="resume-section p-3 p-lg-5 d-flex d-column" id="about">
        <div class="my-auto">
            <div class="subheading mb-5">Shruthi Chari, Miao Qi, Nkcheniyere N. Agu, Oshani Seneviratne, James P. McCusker, Kristin P. Bennett, Amar K. Das and Deborah L. McGuinness<br/>
                <b><a href="https://science.rpi.edu/biology/news/ibm-and-rensselaer-team-research-chronic-diseases-cognitive-computing"> HEALS</a></b>
            </div>

            <article class="mb-5">
                <content>
                    <h3>Publications</h3>
                    <ul>
                        <li><strong>The Semantic Data Dictionary Approach to Data Annotation & Integration</strong>, International Semantic Web Conference 2017 Semantic Science (SemSci) <a href="https:http://ceur-ws.org/Vol-1931/paper-07.pdf">workshop paper</a>      
                        </li>
                    </ul>
                 </content>
             <div class="my-auto">
            <p>A standard approach to describing datasets is through the
use of data dictionaries: tables which contain information about the content, description, and format of each data variable. While this approach is helpful for a human readability, it is difficult for a machine to understand the meaning behind the data. Consequently, tasks involving the combination of data from multiple sources, such as data integration or schema merging, are not easily automated. In response, we present the Semantic Data Dictionary (SDD) specification, which allows for extension and integration of data from multiple domains using a common metadata standard. We have developed a structure based on the Semanticscience Integrated Ontology’s (SIO) high-level, domain-agnostic conceptualization of scientific data, which is then annotated with more specific terminology from domain-relevant ontologies. The SDD format will make the specification, curation and search of data much easier than direct search of data dictionaries through terminology alignment, but also through the use of "compositional" classes for column descriptions, rather than needing a 1:1 mapping from column to class.
            </p>
        </div>
            </article>
            
            
            <!-- <h3>Abstract</h3> -->
            <p class="mb-5">
            <blockquote>
                The Semantic Data Dictionary is a specification formalizing how to assign a semantic representation of data by annotating dataset variables and their values using concepts from best practice vocabularies and ontologies. It is a collection of individual documents that each play a role in creating a concise and consistent knowledge representation, including the Dictionary Mapping, Codebook, Timeline, and Code Mapping specifications, and the Infosheet, which is used to link these Semantic Data Dictionary elements together. Throughout this website, each of these elements are described.
            </blockquote>
            </p>
        </div>
    </section>
</div>
<div class="post-list">
    {% for post in site.posts %}
    
        <a class="post-title" href="{{site.baseurl}}{{post.url}}"><h2>{{ post.title }}</h2></a>
        <p class="date">{{ post.date | date: "%b %-d, %Y" }}</p>
        <p>{{post.excerpt | strip_html}}</p>
    
    {% endfor %}

</div>
