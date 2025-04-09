from rdflib import Graph, URIRef, XSD, Literal, Namespace
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import requests
import rdflib
import pickle
import os


def execute_sparql_query(graph, query):
    
    try:
        results = graph.query(query)

        return results
        
    except requests.exceptions.RequestException as e:
        # Log the exception details and re-raise it
        print(f"Failed to execute SPARQL query. Error: {str(e)}")
        raise

def load_graph(format = 'tsv'):


    if format == 'ttl':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.ttl")
        file_path = os.path.normpath(ontology_path)

        g = Graph()
        g.parse(file_path, format='ttl')

    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
        file_path = os.path.normpath(ontology_path)
        df = pd.read_csv(file_path, sep="\t", header=None, dtype=str)
        data = df.values
        g = rdflib.Graph()
        g.addN((rdflib.URIRef(s), rdflib.URIRef(p), rdflib.URIRef(o), g) for s, p, o in data)

    return g

def identify_profiles(fix_k = True):

    #1: Get the list of the user profiles
    # TODO We can add filters to get users from one use case
    graph = load_graph()

    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <https://extremexp.eu/ontology#>

    SELECT DISTINCT ?user
    WHERE {{
        ?user ml:specifies ?workflow.
    }}
    """

    results = execute_sparql_query(graph, query)

    users = []
    if results:
        for row in results:
            users.append(str(row.user))

    #2: Get the embeddings of the profiles
    current_dir = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_to_id.pkl")
    norm_path_e2i = os.path.normpath(path)
    with open(norm_path_e2i, "rb") as f:
        ent_to_id = pickle.load(f)
    
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_representations.pkl")
    norm_path_ee = os.path.normpath(path)
    with open(norm_path_ee, "rb") as f:
        ent_emb = pickle.load(f)
    
    user_embeddings = []
    for user in users:
        user_id = ent_to_id[user]
        user_embedding = ent_emb[user_id]
        user_embeddings.append(user_embedding)
    
    data = np.array([t.numpy() for t in user_embeddings])

    #3: Perform clustering

    if fix_k:
        k = 1 #TODO change to 3 or whichever
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(data)
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_
    else:
        best_k = 2  
        best_score = -1 

        for k in range(2, 11):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(data)
            score = silhouette_score(data, kmeans.labels_)

            if score > best_score:
                best_k = k
                best_score = score

        k = best_k
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(data)
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_
        
    return centroids