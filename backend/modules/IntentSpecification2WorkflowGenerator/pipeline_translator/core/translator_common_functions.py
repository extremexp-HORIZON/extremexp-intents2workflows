import os
from typing import List, Tuple
import sys

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

from common import *
from pipeline_generator.graph_queries import get_implementation_input_specs

def get_ontology() -> Graph:
    cwd = os.getcwd()
    os.chdir('..')
    ontology = common.get_ontology_graph()
    os.chdir(cwd)
    return ontology
    

def get_input_specs(ontology, implementation):
    return get_implementation_input_specs(ontology, implementation)


def get_implementation_task(ontology: Graph, implementation: URIRef):
    query = f""" PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?task
                WHERE {{ {implementation.n3()} tb:implements ?task .}} """
    print(query)
    
    results = ontology.query(query).bindings
    print(results)

    assert len(results) == 1

    return results[0]['task']


def load_workflow(path: str) -> Graph:
    graph = get_graph_xp()
    graph.parse(path, format='turtle')
    return graph


def get_workflow_steps(graph: Graph) -> List[URIRef]:
    steps = list(graph.subjects(RDF.type, tb.Step))

    connections = list(graph.subject_objects(tb.followedBy))
    disordered = True
    while disordered:
        disordered = False
        for source, target in connections:
            si = steps.index(source)
            ti = steps.index(target)
            if si > ti:
                disordered = True
                steps[si] = target
                steps[ti] = source
    return steps


def get_step_component_implementation(ontology: Graph, workflow_graph: Graph, step: URIRef) -> Tuple[URIRef, URIRef]:
    component = next(workflow_graph.objects(step, tb.runs, True))
    implementation = next(ontology.objects(component, tb.hasImplementation, True))
    return component, implementation

def get_number_of_output_ports(ontology: Graph, workflow_graph: Graph, step: URIRef) -> int:
    _, implementation = get_step_component_implementation(ontology, workflow_graph, step)
    return sum(1 for _ in ontology.objects(implementation, tb.specifiesOutput))

def get_step_parameters(ontology: Graph, workflow_graph: Graph, step: URIRef) -> List[Tuple[str, str, str, URIRef]]:
    # print(f'STEP: {step}')
    parameters = list(workflow_graph.objects(step, tb.usesParameter, True))
    # print(f'PARAMETERS: {len(parameters)}')
    param_specs = [next(workflow_graph.objects(param, tb.specifiedBy, True)) for param in parameters]
    # print(f'PARAM SPECS: {param_specs}')
    param_values = [next(workflow_graph.objects(ps, tb.hasValue, True)) for ps in param_specs]
    # print(f'VALUES: {param_values}')
    keys = [next(ontology.objects(p, tb.knime_key, True), None) for p in parameters]
    # print(f'KEYS: {len(keys)}')
    paths = [next(ontology.objects(p, tb.knime_path, True)).value for p in parameters]
    # print(f'PATHS: {paths}')
    types = [next(ontology.objects(p, tb.has_datatype, True)) for p in parameters]
    # print(f'TYPES: {types}')
    return list(zip(keys, param_values, paths, types))

def get_step_inputs(workflow_graph:Graph, step:URIRef):
    query = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?pos ?data 
                WHERE {{ 
                    {step.n3()} tb:hasInput ?inp .
                    ?inp 
                        tb:has_data ?data ;
                        tb:has_position ?pos .      
                }} 
                ORDER BY ?pos"""
    result = workflow_graph.query(query).bindings
    return [ inp['data'] for inp in result ]

def get_step_outputs(workflow_graph:Graph, step:URIRef):
    query = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                SELECT ?pos ?data 
                WHERE {{ 
                    {step.n3()} tb:hasOutput ?inp .
                    ?inp 
                        tb:has_data ?data ;
                        tb:has_position ?pos .      
                }} 
                ORDER BY ?pos"""
    result = workflow_graph.query(query).bindings
    return [ inp['data'] for inp in result ]

def is_applier_step(ontology: Graph, workflow_graph:Graph, step:URIRef):
    component = next(workflow_graph.objects(step, tb.runs,True))

    askquery = f"""PREFIX tb: <https://extremexp.eu/ontology/tbox#>
                    ASK {{
                        {component.n3()} a tb:ApplierComponent
                    }}"""
    result = ontology.query(askquery).askAnswer
    
    return result

def get_data_path(workflow_graph:Graph, data:URIRef):
    return next(workflow_graph.objects(data,dmop.path,True),None)


def get_workflow_intent_name(workflow_graph: Graph) -> str:
    return next(workflow_graph.subjects(RDF.type, tb.Intent, True)).fragment


def get_workflow_intent_number(workflow_graph: Graph) -> int:
    return int(next(workflow_graph.subjects(RDF.type, tb.Workflow, True)).fragment.split('_')[1])

def get_workflow_connections(workflow_graph: Graph) -> List[Tuple[URIRef, URIRef, URIRef, URIRef]]:
    query = f'''
    PREFIX tb: <{tb}>
    SELECT ?source ?destination ?sourcePort ?destinationPort
    WHERE {{
        ?source a tb:Step ;
                tb:followedBy ?destination ;
                tb:hasOutput ?output .
        ?output tb:has_position ?sourcePort ;
                tb:has_data ?link .
        ?destination a tb:Step ;
                    tb:hasInput ?input .
        ?input tb:has_position ?destinationPort ;
                tb:has_data ?link .
    }}
    '''
    results = workflow_graph.query(query).bindings
    # print(f'RESULTS: {results}')
    return [(r['source'], r['destination'], r['sourcePort'], r['destinationPort']) for r in results]