from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from flask import Flask, render_template
from rdflib import Graph
from rdflib.namespace import FOAF
from datetime import datetime
import os
import uuid

#url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:11002')
#username = 'yelpGraph'#os.environ.get('NEO4J_USERNAME')
#password = 'datascience'#os.environ.get('NEO4J_PASSWORD')

#graph = Graph(url + '/db/data/', user=username, password=password)

foaf = Graph()

class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        query = '''
        MATCH (u:User) WHERE u.name = {username} RETURN u.name
        '''
#        matcher = NodeMatcher(graph)
        user = graph.run(query, username=self.username)
#        user = graph.NodeSelection.first('User', 'username', self.username)
        return user

    def register(self, password):
        if not self.find():
            user = Node('User', username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def add_post(self, title, tags, text):
        user = self.find()
        post = Node(
            'Post',
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, 'PUBLISHED', post)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(',')]
        for name in set(tags):
            tag = Node('Tag', name=name)
            graph.merge(tag)

            rel = Relationship(tag, 'TAGGED', post)
            graph.create(rel)

    def like_post(self, post_id):
        user = self.find()
        post = graph.find_one('Post', 'id', post_id)
        graph.merge(Relationship(user, 'LIKED', post))

    def get_recent_posts(self):
        query = '''
        MATCH (u:User)-[:WROTE]->(r:Review)-[:REVIEWS]->(b:Business)
        WHERE u.name= {username}
        RETURN b.name AS BusinessName, r.date AS Date, r.stars as Stars
        ORDER BY r.date DESC LIMIT 5
        '''

        return graph.run(query, username=self.username)

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both blogged about.
        query = '''
        MATCH (u:User)-[:WROTE]->(:Review)-[:REVIEWS]->(b:Business),
        (ou:User)-[:WROTE]->(:Review)-[:REVIEWS]->(b)
        WHERE u.name= {username} AND exists(ou.name) AND u <> ou
        WITH ou, COLLECT(DISTINCT b.name) AS BusinessName
        ORDER BY SIZE(BusinessName) DESC LIMIT 3
        RETURN ou.name AS SimilarUser
        '''

        return graph.run(query, username=self.username)

    def get_commonality_of_user(self, other):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = '''
        MATCH (u:User)-[:WROTE]->(:Review)-[:REVIEWS]->(b:Business),
        (ou:User)-[:WROTE]->(:Review)-[:REVIEWS]->(b),
        (ou)-[:WROTE]->(:Review)-[:REVIEWS]->(bus:Business)
        WHERE u.name= {username} AND exists(ou.name) AND u <> ou AND b <> bus
        WITH ou, u, COLLECT(DISTINCT bus.name) AS Recommendation
        ORDER BY SIZE(Recommendation) DESC LIMIT 3
        RETURN ou.name AS SimilarUser, Recommendation
        '''

        return graph.run(query, username=self.username)

def provenance_Information():
    foaf.parse("blog/static/rdf/studycohort.owl",format="owl")
    foaf.parse("blog/static/rdf/Table1KG.ttl",format='turtle')
    
#    foaf.bind('bibo', URIRef('http://bibliontology.com/index.html#'))
#    foaf.bind('dct', URIRef('http://purl.org/dc/terms/'))
#    foaf.bind('gprov', URIRef('https://idea.tw.rpi.edu/projects/heals/gprov/'))
#    foaf.bind('prov', URIRef('http://www.w3.org/ns/prov#'))
#    foaf.bind('rdf', URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
#    foaf.bind('rdfs', URIRef('http://www.w3.org/2000/01/rdf-schema#'))    
#    foaf.bind('sio', URIRef('http://semanticscience.org/resource/'))
#    foaf.bind('xml', URIRef('http://www.w3.org/XML/1998/namespace'))
#    foaf.bind('xsd', URIRef('http://www.w3.org/2001/XMLSchema#'))    
#    
    query = '''
    PREFIX sco: <https://idea.tw.rpi.edu/projects/heals/studycohort/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sio: <http://semanticscience.org/resource/>

    SELECT DISTINCT ?propType ?attrType ?propVal WHERE {
      ?studyArm sio:hasAttribute ?prop .
      ?studyArm rdfs:subClassOf sco:StudyArm .
      ?prop a ?propType .
      ?prop sio:hasAttribute ?attr .
      {
      ?attr a ?attrType .
      ?attr sio:hasValue ?propVal .   
      }
     UNION
      {
        ?attr sio:hasAttribute ?intermediate .
        ?intermediate a ?attrType .
        ?intermediate sio:hasValue ?propVal .
        }
      
    }
    '''

    res = foaf.query(query)
    print("Query results", list(res))
    return list(res)[0]

def get_me():
    foaf.parse("blog/static/rdf/foaf.rdf")
    res = foaf.query("""SELECT DISTINCT ?fname
				 WHERE {
				 ?me a foaf:Person .
				 ?me foaf:givenname ?fname .
				 }
				 """, initNs={"foaf": FOAF})
    return list(res)[0]
	
def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%Y-%m-%d')


#city = 'Toronto'
#posts = get_higest_ranking_restaurant(city)
#print(posts) 
#username = 'John'
#if User(username).find():
#    print("Found User")
