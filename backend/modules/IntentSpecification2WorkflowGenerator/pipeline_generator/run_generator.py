
import os
import time
from tqdm import tqdm
from datetime import datetime

from optimized_pipeline_generator import build_workflows, get_algorithms_and_implementations_to_solve_task, get_intent_info
from common import *
import graph_queries

def add_input_parameters(ontology:Graph, intent_graph:Graph):
    dataset, task, algorithm, intent_iri = get_intent_info(intent_graph)

    all_cols = graph_queries.get_inputs_all_columns(ontology, [dataset])
    cat_cols = graph_queries.get_inputs_categorical_columns(ontology, [dataset])
    num_cols = graph_queries.get_inputs_numeric_columns(ontology, [dataset])
    exp_params = graph_queries.get_exposed_parameters(ontology, task, algorithm)

    for exp_param in exp_params:
        option_columns = []
        if 'CATEGORICAL' in exp_param['value']:
            option_columns = cat_cols
        elif 'NUMERICAL' in exp_param['value']:
            option_columns = num_cols
        else:
            option_columns = all_cols

        if 'COMPLETE' in exp_param['value']:
            option_columns.append('<RowID>')

        if 'INCLUDED' in exp_param['condition']:
            param_val = []
            col_num = int(input(f"How many columns do you want to enter for {exp_param['label']} parameter?"))
            for i in range(col_num):
                param_val.append(input(f"Enter a value for {exp_param['label']} from the following: {option_columns}"))
        else:
            param_val = input(f"Enter a value for {exp_param['label']} from the following: {option_columns}")

        intent_graph.add((intent_iri, tb.specifiesValue, Literal(param_val)))
        intent_graph.add((Literal(param_val), tb.forParameter, exp_param['exp_param']))

def interactive():
    intent_graph = get_graph_xp()
    intent = input('Introduce the intent name [ClassificationIntent]: ') or 'VisualizationIntent' #or 'ClassificationIntent'
    data = input('Introduce the dataset name [titanic.csv]: ') or 'titanic.csv'
    task = input('Introduce the task name [Classification]: ') or 'Classification'


    intent_graph.add((ab.term(intent), RDF.type, tb.Intent))
    intent_graph.add((ab.term(intent), tb.overData, ab.term(data)))
    intent_graph.add((cb.term(task), tb.tackles, ab.term(intent)))


    ontology = get_ontology_graph()

    if task == 'DataVisualization':
        algos = [alg.fragment for alg in graph_queries.get_algorithms_from_task(ontology, cb.term(task))]
        vis_algorithm = str(input(f'Choose a visualization algorithm from the following (case-sensitive):{algos}'))
        if vis_algorithm is not None:
            intent_graph.add((ab.term(intent), tb.specifies, cb.term(vis_algorithm)))

    component_percentage = float(input('Choose a threshold component percentage (for the preprocessing components) [100, 75, 50, 25] (%): ') or 100)/100.0
    complexity = int(input("Choose the complexity of the generated workflows [0,1,2]: ") or 2)

    intent_graph.add((ab.term(intent), tb.has_component_threshold, Literal(component_percentage)))
    intent_graph.add((ab.term(intent), tb.has_complexity, Literal(complexity)))

    folder = input('Introduce the folder to save the workflows: ')
    if folder == '':
        folder = f'./workflows/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}/'
        tqdm.write(f'No folder introduced, using default ({folder})')
    if not os.path.exists(folder):
        tqdm.write('Directory does not exist, creating it')
        os.makedirs(folder)

    shape_graph = Graph()
    shape_graph.parse('./shapeGraph.ttl')
    add_input_parameters(ontology,intent_graph)
    t = time.time()
    solving_algs, solving_impls = get_algorithms_and_implementations_to_solve_task(ontology, shape_graph, intent_graph, log=True)
    workflows = build_workflows(ontology, shape_graph, intent_graph, solving_impls, log=True)
    t = time.time() - t

    print(f'Workflows built in {t} seconds')

    for wg in workflows:
        workflow_name = next(wg.subjects(RDF.type, tb.Workflow, unique=True)).fragment
        print(workflow_name)
        wg.serialize(os.path.join(folder, f'{workflow_name}.ttl'), format='turtle')
    print(f'Workflows saved in {folder}')

interactive()