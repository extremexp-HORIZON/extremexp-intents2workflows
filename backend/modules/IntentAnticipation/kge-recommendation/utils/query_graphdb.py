import requests
import urllib.parse
import json
import pandas as pd
import rdflib
from rdflib import Graph, URIRef, XSD, Literal, Namespace
from rdflib.namespace import RDF, RDFS
import math
import os


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

def store_graph(graph, format = 'tsv'):

    if format == 'ttl':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.ttl")
        file_path = os.path.normpath(ontology_path)

        graph.serialize(destination=file_path, format='ttl')
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ontology_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
        file_path = os.path.normpath(ontology_path)
        tsv_data = []
        for subj, pred, obj in graph:
            tsv_data.append((subj, pred, obj))
        df = pd.DataFrame(tsv_data)
        df.to_csv(file_path, sep="\t", index=False, header=False)



def execute_sparql_query(graph, query):
    
    try:
        results = graph.query(query)

        return results
        
    except requests.exceptions.RequestException as e:
        # Log the exception details and re-raise it
        print(f"Failed to execute SPARQL query. Error: {str(e)}")
        raise



def get_all_metrics():
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>
    
    SELECT DISTINCT ?object
    WHERE {{
      ?subject ml:specifies ?object .
    }}
    ORDER BY ASC(?object)
    """
    graph = load_graph()
    results = execute_sparql_query(graph, query)
    metrics = []
    if results:
        for row in results:
            metrics.append(row.object.split('#')[-1])

    return metrics


def get_all_algorithms():
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>
    
    
    SELECT DISTINCT ?algorithm
    WHERE {{
            ?algorithm a <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#ClassificationModelingAlgorithm>
        }}
    ORDER BY ASC(?algorithm)
    """

    graph = load_graph()
    results = execute_sparql_query(graph, query)
    algorithms = []
    if results:
        for row in results:
            algorithms.append(row.algorithm.split('#')[-1])

    return algorithms


def get_all_preprocessing_algorithms():
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <http://localhost/8080/intentOntology#>
    
    
    SELECT DISTINCT ?algorithm
    WHERE {{
            ?algorithm a <http://www.e-lico.eu/ontologies/dmo/DMOP/DMOP.owl#DataProcessingAlgorithm>
        }}
    ORDER BY ASC(?algorithm)
    """

    graph = load_graph()
    results = execute_sparql_query(graph, query)
    preprocessing_algorithms = []
    if results:
        for row in results:
            preprocessing_algorithms.append(row.algorithm.split('#')[-1])

    return preprocessing_algorithms