---
title: Welcome
---

<header>
    <div class="header">
        <br/>
        <center><a class="title-a" href="#"><h1 class="title">{{page.title}}</h1></a></center>
    </div>
</header>


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

[Link to another page](./another-page.html).

There should be whitespace between paragraphs.

There should be whitespace between paragraphs. We recommend including a README, or a file with information about your project.

# Header 1 <a class="post-title" href="{{site.baseurl}}{{post.url}}"><h2>{{ post.title }}</h2></a>

This is a normal paragraph following a header. GitHub is a code hosting platform for version control and collaboration. It lets you and others work together on projects from anywhere.

## Header 2

> This is a blockquote following a header.
>
> When something is important enough, you do it even if the odds are not in your favor.

### Header 3

```js
// Javascript code with syntax highlighting.
var fun = function lang(l) {
  dateformat.i18n = require('./lang/' + l)
  return true;
}
```

```ruby
# Ruby code with syntax highlighting
GitHubPages::Dependencies.gems.each do |gem, version|
  s.add_dependency(gem, "= #{version}")
end
```

#### Header 4

*   This is an unordered list following a header.
*   This is an unordered list following a header.
*   This is an unordered list following a header.

##### Header 5

1.  This is an ordered list following a header.
2.  This is an ordered list following a header.
3.  This is an ordered list following a header.

###### Header 6

| head1        | head two          | three |
|:-------------|:------------------|:------|
| ok           | good swedish fish | nice  |
| out of stock | good and plenty   | nice  |
| ok           | good `oreos`      | hmm   |
| ok           | good `zoute` drop | yumm  |

### There's a horizontal rule below this.

* * *

### Here is an unordered list:

*   Item foo
*   Item bar
*   Item baz
*   Item zip

### And an ordered list:

1.  Item one
1.  Item two
1.  Item three
1.  Item four

### And a nested list:

- level 1 item
  - level 2 item
  - level 2 item
    - level 3 item
    - level 3 item
- level 1 item
  - level 2 item
  - level 2 item
  - level 2 item
- level 1 item
  - level 2 item
  - level 2 item
- level 1 item

### Small image

![Octocat](https://assets-cdn.github.com/images/icons/emoji/octocat.png)

### Large image

![Branching](https://guides.github.com/activities/hello-world/branching.png)


### Definition lists can be used with HTML syntax.

<dl>
<dt>Name</dt>
<dd>Godzilla</dd>
<dt>Born</dt>
<dd>1952</dd>
<dt>Birthplace</dt>
<dd>Japan</dd>
<dt>Color</dt>
<dd>Green</dd>
</dl>

```
Long, single-line code blocks should not wrap. They should horizontally scroll if they are too long. This line should be long enough to demonstrate this.
```

```
The final element.
```
