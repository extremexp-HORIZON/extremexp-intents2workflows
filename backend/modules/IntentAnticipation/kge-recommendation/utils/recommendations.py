from rdflib import Graph, URIRef, XSD, Literal, Namespace
from pykeen.training import SLCWATrainingLoop
from pykeen.triples import TriplesFactory
from rdflib.namespace import RDF, RDFS
from pykeen.models import TransE
from torch.optim import Adam
import urllib.parse
import pandas as pd
import requests
import csv
import time
import rdflib
import os
import pickle
import torch






def annotate_tsv(user,intent,dataset):
    '''
    The KG structure that we follow is:

    ns = https://extremexp.eu/ontology#

    User ns:specifies Experiment
    Experiment ns:hasDataset Dataset
    Experiment ns:hasAlgorithm Algorithm
    Experiment ns:hasIntent Intent
    Experiment ns:hasFeedback Feedback (Good, Neutral, Bad)
    Experiment ns:hasMetric BlankMetric
    BlankMetric ns:onMetric Metric
    BlankMetric ns:hasValue MetricValue
    '''

    #TODO : HOW ARE USER,INTENT,DATASET PASSED HERE
    current_dir = os.path.dirname(os.path.abspath(__file__))
    new_path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "new_triples.tsv")
    new_triples_path = os.path.normpath(new_path)


    experiment = user+intent+dataset + str(time.time()).split('.')[0]

    #TODO ADDAPT TO THE ONTOLOGY: Change name space and relation names
    name_space = 'https://extremexp.eu/ontology#'
    triples = [
    (name_space+user, name_space+ 'specifies', name_space+experiment), 
    (name_space+experiment, name_space + 'hasIntent', name_space+intent),
    (name_space+experiment, name_space+ 'hasDataset', name_space+dataset)]

    with open(new_triples_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerows(triples)
    
    return experiment # Is just experiment what we want?


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

def execute_sparql_query(graph, query):
    
    try:
        results = graph.query(query)

        return results
        
    except requests.exceptions.RequestException as e:
        # Log the exception details and re-raise it
        print(f"Failed to execute SPARQL query. Error: {str(e)}")
        raise


'''
This file will provide the recommendations with explanations, combining SPARQL with KGE
'''

def recommendations(input_experiment,input_user,input_intent,input_dataset):

   
    ################################################################################
    ################################## UPDATE KGE ##################################
    ################################################################################

    seed = 8182
    embedding_dimension = 128
    learning_rate_fine_tune = 0.0001
    num_finetune_epochs = 5
    num_negs_per_pos = 20

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "new_triples.tsv")
    new_triples_path = os.path.normpath(path)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "..","..", "..", "api", "ontology", "KnowledgeBase.tsv")
    triples_path = os.path.normpath(path)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # LOAD ALL DICTIONARIES AND EMBEDDINGS

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_to_id.pkl")
    norm_path_e2i = os.path.normpath(path)
    with open(norm_path_e2i, "rb") as f:
        old_ent_to_id = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "relation_to_id.pkl")
    norm_path_r2i = os.path.normpath(path)
    with open(norm_path_r2i, "rb") as f:
        old_rel_to_id = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "entity_representations.pkl")
    norm_path_ee = os.path.normpath(path)
    with open(norm_path_ee, "rb") as f:
        old_ent_emb = pickle.load(f).to(device)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "relation_representations.pkl")
    norm_path_re = os.path.normpath(path)
    with open(norm_path_re, "rb") as f:
        old_rel_emb = pickle.load(f).to(device)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "algorithms_set.pkl")
    norm_path_as = os.path.normpath(path)
    with open(norm_path_as, "rb") as f:
        algorithms_set = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "datasets_set.pkl")
    norm_path_ds = os.path.normpath(path)
    with open(norm_path_ds, "rb") as f:
        datasets_set = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "users_set.pkl")
    norm_path_us = os.path.normpath(path)
    with open(norm_path_us, "rb") as f:
        users_set = pickle.load(f)

    path = os.path.join(current_dir, "..", "..","..", "..", "api", "kge_model", "experiments_set.pkl")
    norm_path_es = os.path.normpath(path)
    with open(norm_path_es, "rb") as f:
        experiments_set = pickle.load(f)


    df1 = pd.read_csv(triples_path, sep="\t", header= None)
    df2 = pd.read_csv(new_triples_path, sep="\t", header=None)

    values_to_remove = {"https://extremexp.eu/ontology#hasMetric", "https://extremexp.eu/ontology#onMetric", "https://extremexp.eu/ontology#hasValue"} 
    df1= df1[~df1[1].isin(values_to_remove)]
    df2= df2[~df2[1].isin(values_to_remove)]

    combined_df = pd.concat([df1, df2], ignore_index=True)
    combined_df.to_csv(triples_path, sep="\t", index=False, header=False)

    training_triples_factory = TriplesFactory.from_path(triples_path)

    # Initialize the model with all the entities/relations
    model = TransE(triples_factory=training_triples_factory, embedding_dim=embedding_dimension, random_seed = seed).to(device)

    new_ent_emb = model.entity_representations[0](indices= None).clone().detach().to(device)
    new_rel_emb = model.relation_representations[0](indices= None).clone().detach().to(device)

    # Get new mappings

    new_ent_to_id = training_triples_factory.entity_to_id
    new_rel_to_id = training_triples_factory.relation_to_id

    # Keep the embeddings of old entities/relations
    with torch.no_grad():
        for i in old_ent_to_id:
            old_idx = old_ent_to_id[i]
            new_idx = training_triples_factory.entity_to_id[i]

            old_vector = old_ent_emb[old_idx].to(device)
            new_ent_emb[new_idx] = old_vector
        for j in old_rel_to_id:
            old_idx = old_rel_to_id[j]
            new_idx = training_triples_factory.relation_to_id[j]

            old_vector = old_rel_emb[old_idx].to(device)
            new_rel_emb[new_idx] = old_vector

        model.entity_representations[0]._embeddings.weight.copy_(new_ent_emb)
        model.relation_representations[0]._embeddings.weight.copy_(new_rel_emb)

   # Initialization

    centroid_exp = torch.zeros([1,embedding_dimension]).to(device)
    centroid_data = torch.zeros([1,embedding_dimension]).to(device)
    centroid_user = torch.zeros([1,embedding_dimension]).to(device)
    centroid_algorithm = torch.zeros([1,embedding_dimension]).to(device)


    for exp in experiments_set:
        idx = old_ent_to_id[exp]
        centroid_exp += old_ent_emb[idx]
    centroid_exp /= len(experiments_set)


    for user in users_set:
        idx = old_ent_to_id[user]
        centroid_user += old_ent_emb[idx]
    centroid_user /= len(users_set)

    for dataset in datasets_set:
        idx = old_ent_to_id[dataset]
        centroid_data += old_ent_emb[idx]
    centroid_data /= len(datasets_set)

    for algorithm in algorithms_set:
        idx = old_ent_to_id[algorithm]
        centroid_algorithm += old_ent_emb[idx]
    centroid_algorithm /= len(algorithms_set)


    # Initialize experiments:

    for experiment in df2[df2[1]=='https://extremexp.eu/ontology#specifies'][2].values:
        if experiment not in experiments_set:
            idx = new_ent_to_id[experiment]
            new_ent_emb[idx] = centroid_exp
            experiments_set.add(experiment)

    for user in df2[df2[1]=='https://extremexp.eu/ontology#specifies'][0].values:
        if user not in users_set:
            idx = new_ent_to_id[user]
            new_ent_emb[idx] = centroid_user
            users_set.add(user)

    for algorithm in df2[df2[1]=='https://extremexp.eu/ontology#hasAlgorithm'][2].values:
        if algorithm not in algorithms_set:
            idx = new_ent_to_id[algorithm]
            new_ent_emb[idx] = centroid_algorithm
            algorithms_set.add(algorithm)

    for dataset in df2[df2[1]=='https://extremexp.eu/ontology#hasDataset'][2].values:
        if dataset not in datasets_set:
            idx = new_ent_to_id[dataset]
            new_ent_emb[idx] = centroid_data
            datasets_set.add(dataset)
    

    with open(norm_path_as, "wb") as f:
        pickle.dump(algorithms_set, f)

    with open(norm_path_us, "wb") as f:
        pickle.dump(users_set, f)

    with open(norm_path_es, "wb") as f:
        pickle.dump(datasets_set, f)

    with open(norm_path_es, "wb") as f:
        pickle.dump(experiments_set, f)


    model = model.to(device)

    df = pd.read_csv(new_triples_path, sep='\t', header=None) 
    df_filtered = df[~df[1].isin(values_to_remove)]
    triples_array = df_filtered.to_numpy()
    training_triples = TriplesFactory.from_labeled_triples(triples_array, entity_to_id=new_ent_to_id, relation_to_id=new_rel_to_id)

    optimizer = Adam(params=model.get_grad_params(),lr=learning_rate_fine_tune)

    training_loop = SLCWATrainingLoop(model=model,
                                    triples_factory=training_triples,
                                    optimizer=optimizer,
                                    negative_sampler_kwargs = {'num_negs_per_pos':num_negs_per_pos})

    tl = training_loop.train(triples_factory=training_triples,
                            num_epochs=num_finetune_epochs)
    
    with open(norm_path_ee, "wb") as f:
        pickle.dump(model.entity_representations[0](indices= None).clone().detach(), f)

    with open(norm_path_re, "wb") as f:
        pickle.dump(model.relation_representations[0](indices= None).clone().detach(), f)

    with open(norm_path_e2i, "wb") as f:
        pickle.dump(new_ent_to_id, f)

    with open(norm_path_r2i, "wb") as f:
        pickle.dump(new_rel_to_id, f)

    ################################################################################
    ############################## START SUGGESTIONS ##############################
    ################################################################################

    graph = load_graph()
    suggestions = {}

    ################################################################################
    ################################## ALGORITHM ###################################
    ################################################################################
    


    found = False
    algorithm_sparql = None
    algorithm_sparql_explanation = ''

    # Check if the user has used the dataset with a specific algorithm constraint
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ml: <https://extremexp.eu/ontology#>

    SELECT ?algorithm (COUNT(?algorithm) AS ?count)
    WHERE {{
        ml:{input_user} ml:specifies ?workflow.
        ?workflow ml:hasDataset ml:{input_dataset}.
        ?workflow ml:hasAlgorithm ?algorithm
    }}
    GROUP BY ?algorithm
    ORDER BY DESC(?count)
    LIMIT 1
    """

    results = execute_sparql_query(graph, query)

    if results:
        for row in results:
            algorithm_sparql = row.algorithm
            found = True
            algorithm_sparql_explanation = 'This is your most frequently used algorithm for this dataset.'
    

    # If not found, look for other users' usage of the dataset
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <https://extremexp.eu/ontology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ?workflow ml:hasDataset ml:{input_dataset}.
            ?workflow ml:hasAlgorithm ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm_sparql = row.algorithm
                found = True
                algorithm_sparql_explanation = 'This is the most frequently used algorithm for this dataset.'

    # If still not found, look for the user's usage of the same intent
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <https://extremexp.eu/ontology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ml:{input_user} ml:specifies ?workflow.
            ?workflow ml:hasIntent ml:{input_intent}.
            ?workflow ml:hasAlgorithm ?algorithm.

        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm_sparql = row.algorithm
                found = True
                algorithm_sparql_explanation = 'This is your most frequently used algorithm for '+input_intent+' experiments.'

    # If still not found, get the most used algorithm for the intent overall
    if not found:
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ml: <https://extremexp.eu/ontology#>

        SELECT ?algorithm (COUNT(?algorithm) AS ?count)
        WHERE {{
            ?workflow ml:hasIntent ml:{input_intent}.
            ?workflow ml:hasAlgorithm ?algorithm 
        }}
        GROUP BY ?algorithm
        ORDER BY DESC(?count)
        LIMIT 1
        """
        
        results = execute_sparql_query(graph, query)
        if results:
            for row in results:
                algorithm_sparql = row.algorithm
                found = True
                algorithm_sparql_explanation = 'This is you most frequently used algorithm for '+input_intent+' experiments.'
    
    if algorithm_sparql:
        algorithm_sparql = algorithm_sparql.split("#")[-1] if algorithm_sparql else None

    ################################################################################
    ##################################### KGE ######################################
    ################################################################################

    algorithm_kge = None
    algorithm_kge_explanation = 'Similar '+ input_intent + ' experiments have used this algorithm.'

    #TODO: Replace with a query to get the algorithms complying the intent THAT ARE in the ontology of experiments

    candidate_algorithms = ['https://extremexp.eu/ontology#sklearn-RandomForestClassifier','https://extremexp.eu/ontology#sklearn-KNeighborsClassifier']

    name_space = 'https://extremexp.eu/ontology#'
    relation = name_space + 'hasAlgorithm'
    head = name_space + input_experiment

    head_idx = new_ent_to_id[head]
    relation_idx = new_rel_to_id[relation]
    tail_indices = [new_ent_to_id[alg] for alg in candidate_algorithms]

    batch = [[head_idx, relation_idx, tail_idx] for tail_idx in tail_indices]
    batch_tensor = torch.tensor(batch, dtype=torch.long)

    scores = model.predict_hrt(batch_tensor)
    algorithm_scores = {candidate_algorithms[i]: scores[i].item() for i in range(len(candidate_algorithms))}
    algorithm_kge = max(algorithm_scores, key=algorithm_scores.get)

    if algorithm_sparql != algorithm_kge:
        suggestions['algorithm'] = {'SPARQL': [algorithm_sparql,algorithm_sparql_explanation], 'KGE': [algorithm_kge, algorithm_kge_explanation]}
    else:
        merged_explanation = algorithm_sparql_explanation + ' Moreover, ' + algorithm_kge_explanation.replace('Similar','similar')
        suggestions['algorithm'] = {'BOTH': [algorithm_kge, merged_explanation]}
    return suggestions