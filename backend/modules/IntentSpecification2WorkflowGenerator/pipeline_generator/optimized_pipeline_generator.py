import itertools
import os
import sys
import uuid
from typing import Tuple, Any, List, Dict, Optional, Union
import random
import math
import ast

from pyshacl import validate
from tqdm import tqdm
from urllib.parse import quote

sys.path.append(os.path.join(os.path.abspath(os.path.join('..'))))

from common import *
import pipeline_generator.graph_queries as graph_queries

def get_intent_name(plan_graph:Graph) -> str:
    intent_iri = graph_queries.get_intent_iri(plan_graph)
    return intent_iri.fragment

def reinforce_constraint(ontology:Graph, shape_graph:Graph, node_shape:URIRef, unconstrained_nodes:List[URIRef]):
    constrained_nodes = []

    for node in unconstrained_nodes:
        if satisfies_shape(ontology, shape_graph, shape=node_shape, focus=node):
            constrained_nodes.append(node)
    
    return constrained_nodes

def get_algorithms_from_task_constrained(ontology:Graph, shape_graph:Graph, task: URIRef) -> URIRef:
    algs_unconstr = graph_queries.get_algorithms_from_task(ontology, task)
    return reinforce_constraint(ontology, shape_graph, ab.AlgorithmConstraint, algs_unconstr)




def get_intent_info(intent_graph: Graph, intent_iri: Optional[URIRef] = None) -> \
        Tuple[URIRef, URIRef, List[Dict[str, Any]], URIRef]:
    if not intent_iri:
        intent_iri = graph_queries.get_intent_iri(intent_graph)

    dataset, task, algorithm = graph_queries.get_intent_dataset_task(intent_graph, intent_iri) 

    return dataset, task, algorithm, intent_iri 



def get_potential_implementations_constrained(ontology:Graph, shape_graph:Graph, algorithm: URIRef, exclude_appliers=True) -> \
        List[URIRef]:
    pot_impl_unconstr = graph_queries.get_potential_implementations(ontology, algorithm, exclude_appliers)
    return reinforce_constraint(ontology, shape_graph, ab.ImplementationConstraint, pot_impl_unconstr)



def get_implementation_components_constrained(ontology: Graph, shape_graph: Graph, implementation: URIRef) -> List[URIRef]:
    pot_comp_unconstr = graph_queries.get_implementation_components(ontology, implementation)
    return reinforce_constraint(ontology, shape_graph, ab.ComponentConstraint, pot_comp_unconstr)



def find_implementations_to_satisfy_shape_constrained(ontology: Graph, shape_graph:Graph, shape: URIRef, exclude_appliers: bool = False) -> List[URIRef]:
    pot_impl_unconstr = graph_queries.find_implementations_to_satisfy_shape(ontology,shape,exclude_appliers)
    return reinforce_constraint(ontology,shape_graph,ab.ImplementationConstraint,pot_impl_unconstr)



def satisfies_shape(data_graph: Graph, shacl_graph: Graph, shape: URIRef, focus: URIRef) -> bool:
    conforms, g, report = validate(data_graph, shacl_graph=shacl_graph, validate_shapes=[shape], focus=focus)

    #if not conforms:
    #    tqdm.write(report)

    return conforms


def get_component_parameters(ontology: Graph, component: URIRef) -> Dict[URIRef, Tuple[Literal, Literal, Literal]]:
    component_params = graph_queries.get_component_non_overriden_parameters(ontology, component)
    return component_params



def get_component_overridden_paramspecs(ontology: Graph, workflow_graph: Graph, component: URIRef) -> Dict[URIRef, Tuple[URIRef, Literal]]:
    paramspecs_query = f"""

        PREFIX tb:<{tb}>
        SELECT ?parameterSpec ?parameter ?parameterValue ?position
        WHERE{{
            {component.n3()} tb:overridesParameter ?parameterSpec .
            ?parameterSpec tb:hasValue ?parameterValue .
            ?parameter tb:specifiedBy ?parameterSpec ;
                       tb:has_position ?position .
        }}
    """
    results = ontology.query(paramspecs_query).bindings

    overridden_paramspecs = {paramspec['parameterSpec']: (paramspec['parameter'], paramspec['parameterValue'], paramspec['position']) for paramspec in results}

    for paramspec, paramval_tup in overridden_paramspecs.items():
        param, value, _ = paramval_tup
        workflow_graph.add((paramspec, RDF.type, tb.ParameterSpecification))
        workflow_graph.add((param, tb.specifiedBy, paramspec))
        workflow_graph.add((paramspec, tb.hasValue, value))

    return overridden_paramspecs



def perform_param_substitution(graph: Graph, implementation: URIRef, parameters: Dict[URIRef, Tuple[Literal, Literal, Literal]],
                               inputs: List[URIRef], intent_graph: Graph = None) -> Dict[URIRef, Tuple[Literal, Literal, Literal]]:
    
    parameter_keys = list(parameters.keys())
    intent_parameters = graph_queries.get_intent_parameters(intent_graph) if intent_graph is not None else {}
    intent_parameter_keys = list(intent_parameters.keys())

    #tqdm.write("intentParams")
    #tqdm.write(str(intent_parameters))

    updated_parameters = parameters.copy()

    for parameter, (default_value, position, condition) in parameters.items():
        if parameter in intent_parameter_keys:
            intent_value = intent_parameters[parameter]
            updated_parameters[parameter] = (intent_value, position, condition)
    
    #tqdm.write(str(parameters))
    #tqdm.write(str(updated_parameters))

    parameters.update(updated_parameters)
            

    for param in parameter_keys:
        value, order, condition = parameters[param]
        if condition.value is not None and condition.value != '':
            feature_types = graph_queries.get_inputs_feature_types(graph, inputs)
            if condition.value == '$$INTEGER_COLUMN$$' and int not in feature_types:
                parameters.pop(param)
                continue
            if condition.value == '$$STRING_COLUMN$$' and str not in feature_types:
                parameters.pop(param)
                continue
            if condition.value == '$$FLOAT_COLUMN$$' and float not in feature_types:
                parameters.pop(param)
                continue
        if isinstance(value.value, str) and '$$LABEL$$' in value.value:
            new_value = value.replace('$$LABEL$$', f'{graph_queries.get_inputs_label_name(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '$$LABEL_CATEGORICAL$$' in value.value: #this allows target column to be defined withou exposed parameters
            new_value = value.replace('$$LABEL_CATEGORICAL$$', f'{graph_queries.get_inputs_label_name(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '$$NUMERIC_COLUMNS$$' in value.value:
            new_value = value.replace('$$NUMERIC_COLUMNS$$', f'{graph_queries.get_inputs_numeric_columns(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '$$CSV_PATH$$' in value.value:
            new_value = value.replace('$$CSV_PATH$$', f'{get_csv_path(graph, inputs)}')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and '&amp;' in value.value:
            new_value = value.replace('&amp;', '&')
            parameters[param] = (Literal(new_value), order, condition)
        if isinstance(value.value, str) and value.value != '':
            if condition.value == '$$BAR_EXCLUDED$$':
                possible_cols = graph_queries.get_inputs_numeric_columns(graph, inputs)
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)
            elif condition.value == '$$HISTOGRAM_EXCLUDED$$':
                possible_cols = graph_queries.get_inputs_numeric_columns(graph, inputs)
                cat_col = [str(parameters[param][0]) for param in intent_parameters.keys() if 'histogram_category' in str(param)][0]
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(cat_col) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)
            elif condition.value == '$$HEATMAP_EXCLUDED$$':
                possible_cols = graph_queries.get_inputs_numeric_columns(graph, inputs)
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)
            elif condition.value == '$$LINEPLOT_EXCLUDED$$':
                possible_cols = graph_queries.get_inputs_all_columns(graph, inputs) + ['<RowID>']
                com_col = [str(parameters[param][0]) for param in intent_parameters.keys() if 'lineplot_x' in str(param)]
                included_cols = [ast.literal_eval(str(parameters[param][0])) for param in intent_parameters.keys() if 'included' in str(param)][0]
                excluded_cols = list(set(possible_cols) - set(com_col) - set(included_cols))
                parameters[param] = (Literal(excluded_cols), order, condition)

    return parameters


def assign_to_parameter_specs(graph: Graph,
                              parameters: Dict[URIRef, Tuple[Literal, Literal, Literal]])-> Dict[URIRef, Tuple[URIRef, Literal]]:
    
    keys = list(parameters.keys())
    param_specs = {}
    
    for param in keys:

        value, order, _ = parameters[param]
        uri = param.split('#')[-1] if '#' in param else param.split('/')[-1]
        sanitized_value = quote(value, safe="-_")
        sanitized_uri = URIRef(f'{uri}_{sanitized_value}_specification'.replace(' ','_').lower())
        param_spec = ab.term(sanitized_uri)
        graph.add((param_spec, RDF.type, tb.ParameterSpecification))
        graph.add((param, tb.specifiedBy, param_spec))
        graph.add((param_spec, tb.hasValue, value))

        param_specs[param_spec] = (param, value, order)
    
    return param_specs


def add_step(graph: Graph, pipeline: URIRef, task_name: str, component: URIRef,
             parameter_specs: Dict[URIRef, Tuple[URIRef, Literal]],
             order: int, previous_task: Union[None, list, URIRef] = None, inputs: Optional[List[URIRef]] = None,
             outputs: Optional[List[URIRef]] = None) -> URIRef:
    if outputs is None:
        outputs = []
    if inputs is None:
        inputs = []
    step = ab.term(task_name)
    graph.add((pipeline, tb.hasStep, step))
    graph.add((step, RDF.type, tb.Step))
    graph.add((step, tb.runs, component))
    graph.add((step, tb.has_position, Literal(order)))
    for i, input in enumerate(inputs):
        in_node = BNode()
        graph.add((in_node, RDF.type, tb.Data))
        graph.add((in_node, tb.has_data, input))
        graph.add((in_node, tb.has_position, Literal(i)))
        graph.add((step, tb.hasInput, in_node))
    for o, output in enumerate(outputs):
        out_node = BNode()
        graph.add((out_node, RDF.type, tb.Data))
        graph.add((out_node, tb.has_data, output))
        graph.add((out_node, tb.has_position, Literal(o)))
        graph.add((step, tb.hasOutput, out_node))
    for param, *_ in parameter_specs.values():
        graph.add((step, tb.usesParameter, param))
    if previous_task:
        if isinstance(previous_task, list):
            for previous in previous_task:
                graph.add((previous, tb.followedBy, step))
        else:
            graph.add((previous_task, tb.followedBy, step))
    return step




def get_csv_path(graph: Graph, inputs: List[URIRef]) -> str:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    path = next(graph.objects(data_input, dmop.path), True)
    return path.value


def copy_subgraph(source_graph: Graph, source_node: URIRef, destination_graph: Graph, destination_node: URIRef,
                  replace_nodes: bool = True) -> None:
    visited_nodes = set()
    nodes_to_visit = [source_node]
    mappings = {source_node: destination_node}

    while nodes_to_visit:
        current_node = nodes_to_visit.pop()
        visited_nodes.add(current_node)
        for predicate, object in source_graph.predicate_objects(current_node):
            if predicate == OWL.sameAs:
                continue
            if replace_nodes and isinstance(object, IdentifiedNode):
                if predicate == RDF.type or object in dmop:
                    mappings[object] = object
                else:
                    if object not in visited_nodes:
                        nodes_to_visit.append(object)
                    if object not in mappings:
                        mappings[object] = BNode()
                destination_graph.add((mappings[current_node], predicate, mappings[object]))
            else:
                destination_graph.add((mappings[current_node], predicate, object))


def annotate_io_with_spec(ontology: Graph, workflow_graph: Graph, io: URIRef, io_spec: List[URIRef]) -> None:
    
    for spec in io_spec:
        
        io_spec_class = next(ontology.objects(spec, SH.targetClass, True), None)

        if io_spec_class is None or (io, RDF.type, io_spec_class) in workflow_graph:
            continue

        workflow_graph.add((io, RDF.type, io_spec_class))


def annotate_ios_with_specs(ontology: Graph, workflow_graph: Graph, data_io: List[URIRef],
                            specs: List[List[URIRef]]) -> None:
    assert len(data_io) == len(specs), 'Number of IOs and specs must be the same'
    for io, spec in zip(data_io, specs):
        annotate_io_with_spec(ontology, workflow_graph, io, spec)


def run_copy_transformation(ontology: Graph, workflow_graph: Graph, transformation: URIRef, inputs: List[URIRef],
                            outputs: List[URIRef]):
    input_index = next(ontology.objects(transformation, tb.copy_input, True)).value
    output_index = next(ontology.objects(transformation, tb.copy_output, True)).value
    #tqdm.write(f"Copy transformation: i:{str(input_index)} o:{str(output_index)}")
    input = inputs[input_index - 1]
    output = outputs[output_index - 1]

    copy_subgraph(workflow_graph, input, workflow_graph, output)


def run_component_transformation(ontology: Graph, workflow_graph: Graph, component: URIRef, inputs: List[URIRef],
                                 outputs: List[URIRef],
                                 parameters_specs: Dict[URIRef, Tuple[URIRef, Literal, Literal]]) -> None:
    transformations = graph_queries.get_component_transformations(ontology, component)
    #tqdm.write("run_component_transformation")
    
    for transformation in transformations:
        #tqdm.write(str(transformation))
        if (transformation, RDF.type, tb.CopyTransformation) in ontology:
            run_copy_transformation(ontology, workflow_graph, transformation, inputs, outputs)
        elif (transformation, RDF.type, tb.LoaderTransformation) in ontology:
            #tqdm.write("loader_transformation")
            continue
        else:
            prefixes = f'''
PREFIX tb: <{tb}>
PREFIX ab: <{ab}>
PREFIX rdf: <{RDF}>
PREFIX rdfs: <{RDFS}>
PREFIX owl: <{OWL}>
PREFIX xsd: <{XSD}>
PREFIX dmop: <{dmop}>
'''
            query = next(ontology.objects(transformation, tb.transformation_query, True)).value
            query = prefixes + query
            for i in range(len(inputs)):
                query = query.replace(f'$input{i + 1}', f'{inputs[i].n3()}')
            for i in range(len(outputs)):
                query = query.replace(f'$output{i + 1}', f'{outputs[i].n3()}')
            for param_spec, (param, value, order) in parameters_specs.items():
                #tqdm.write(param_spec)
                #tqdm.write(param)
                #tqdm.write(value)
                #tqdm.write(order)
                query = query.replace(f'$param{order + 1}', f'{value.n3()}')
                query = query.replace(f'$parameter{order + 1}', f'{value.n3()}')
            
            #tqdm.write("Query:")
            #tqdm.write(str(query))
            workflow_graph.update(query)


def get_best_components(graph: Graph, task: URIRef, components: List[URIRef], dataset: URIRef, percentage: float = None):

    preferred_components = {}
    sorted_components = {}
    for component in components:
        
        component_rules = graph_queries.retreive_component_rules(graph, task, component)
        score = 0

        preferred_components[component] = score

        for datatag, weight_rank in component_rules.items():
            rule_weight = weight_rank[0]
            component_rank = weight_rank[1]
            if satisfies_shape(graph, graph, datatag, dataset):
                score+=rule_weight
            else:
                score-=rule_weight
                
            preferred_components[component] = (score, component_rank)
        
    sorted_preferred = sorted(preferred_components.items(), key=lambda x: x[1][0], reverse=True)

    if len(sorted_preferred) > 0: ### there are multiple components to choose from
        best_scores = set([comp[1] for comp in sorted_preferred])
        if len(best_scores) == 1:
            sorted_preferred = random.sample(sorted_preferred, int(math.ceil(len(sorted_preferred)*percentage))) if percentage else sorted_preferred
        elif len(best_scores) > 1: ### checking if there is at least one superior component
            sorted_preferred = [x for x in sorted_preferred if x[1] >= sorted_preferred[0][1]]


    for comp, rules_nbr in sorted_preferred:
        sorted_components[comp] = rules_nbr 

    return sorted_components


def prune_workflow_combinations(ontology:Graph, shape_graph:Graph, combinations: List[Tuple[int,URIRef]], main_component:URIRef) -> List[Tuple[int,URIRef]]:
        
        temporal_graph = ontology #WARNING: temporal_graph is just an alias. Ontology is modified.
        combinations_constrained = []
        for i, tc in combinations:
            workflow_name = f'workflow_{main_component.fragment}_{i}'
            workflow = tb.term(workflow_name)
            temporal_graph.add((workflow, RDF.type, tb.Workflow))
            
            triples_to_add = []
            triples_to_add.append((workflow, tb.hasComponent, main_component, temporal_graph))

            for component in tc:
                triples_to_add.append((workflow, tb.hasComponent, component, temporal_graph))  
            
            temporal_graph.addN(triples_to_add)

            if satisfies_shape(temporal_graph, shape_graph, shape=ab.WorkflowConstraint, focus=workflow):
                combinations_constrained.append(tc)
        return list(enumerate(combinations_constrained))

    


def get_step_name(workflow_name: str, task_order: int, implementation: URIRef) -> str:
    return f'{workflow_name}-step_{task_order}_{implementation.fragment.replace("-", "_")}'


def add_loader_step(ontology: Graph, workflow_graph: Graph, workflow: URIRef, dataset_node: URIRef, loader_component:URIRef) -> URIRef:
    #loader_component = cb.term('component-csv_local_reader')
    loader_step_name = get_step_name(workflow.fragment, 0, loader_component)
    loader_parameters = get_component_parameters(ontology, loader_component)
    loader_overridden_paramspecs = get_component_overridden_paramspecs(ontology, workflow_graph, loader_component)
    loader_parameters = perform_param_substitution(workflow_graph, None, loader_parameters, [dataset_node])
    loader_param_specs = assign_to_parameter_specs(workflow_graph, loader_parameters)
    loader_param_specs.update(loader_overridden_paramspecs)
    return add_step(workflow_graph, workflow, loader_step_name, loader_component, loader_param_specs, 0, None, None,
                    [dataset_node])

def add_saver_step(ontology: Graph, workflow_graph: Graph, workflow: URIRef, test_dataset_node: URIRef, previous_test_step:URIRef, 
                   task_order, saver_component:URIRef) -> URIRef:
    #saver_component = cb.term('component-csv_local_writer')
    saver_step_name = get_step_name(workflow.fragment, task_order, saver_component)
    saver_parameters = get_component_parameters(ontology, saver_component)
    saver_implementation = graph_queries.get_component_implementation(ontology, saver_component)
    saver_parameters = perform_param_substitution(workflow_graph, saver_implementation, saver_parameters, [test_dataset_node])
    saver_overridden_paramspecs = get_component_overridden_paramspecs(ontology, workflow_graph, saver_component)
    saver_param_specs = assign_to_parameter_specs(workflow_graph, saver_parameters)
    saver_param_specs.update(saver_overridden_paramspecs)
    return add_step(workflow_graph, workflow, saver_step_name, saver_component, saver_param_specs,task_order, previous_test_step, [test_dataset_node], [])

def add_component(ontology: Graph, intent_graph:Graph, workflow_graph: Graph, workflow: URIRef, workflow_name: str, 
                  max_imp_level: int, component:URIRef, task_order: int, previous_step: URIRef, input_data: URIRef, input_model: URIRef):

    step_name = get_step_name(workflow_name, task_order, component)
    component_implementation = graph_queries.get_component_implementation(ontology, component)
    engine = graph_queries.get_engine(ontology, component_implementation)
    input_specs = graph_queries.get_implementation_input_specs(ontology,component_implementation,max_imp_level)
    input_data_index = graph_queries.identify_data_io(ontology, input_specs, return_index=True)
    input_model_index = graph_queries.identify_model_io(ontology, input_specs, return_index=True)

    transformation_inputs = [ab[f'{step_name}-input_{i}'] for i in range(len(input_specs))]

    if input_data_index is not None:
        transformation_inputs[input_data_index] = input_data
    
    if input_model_index is not None:
        transformation_inputs[input_model_index] = input_model

    
    annotate_ios_with_specs(ontology, workflow_graph, transformation_inputs,
                            input_specs)
    
    output_specs = graph_queries.get_implementation_output_specs(ontology,component_implementation)
    transformation_outputs = [ab[f'{step_name}-output_{i}'] for i in range(len(output_specs))]
    annotate_ios_with_specs(ontology, workflow_graph, transformation_outputs,output_specs)
    
    parameters = get_component_parameters(ontology, component)

    overridden_parameters = get_component_overridden_paramspecs(ontology, workflow_graph, component)
    parameters = perform_param_substitution(graph=workflow_graph, parameters=parameters,
                                                        implementation=component_implementation,
                                                        inputs=transformation_inputs,
                                                        intent_graph=intent_graph)
    
    param_specs = assign_to_parameter_specs(workflow_graph, parameters)
    param_specs.update(overridden_parameters)


    step = add_step(workflow_graph, workflow,
                        step_name,
                        component,
                        param_specs,
                        task_order, previous_step,
                        transformation_inputs,
                        transformation_outputs)
    run_component_transformation(ontology, workflow_graph, component,
                                    transformation_inputs, transformation_outputs, param_specs)
    

    train_dataset_index = graph_queries.identify_data_io(ontology, output_specs, train=True, return_index=True)
    test_dataset_index = graph_queries.identify_data_io(ontology, output_specs, test=True, return_index=True)
    model_index = graph_queries.identify_model_io(ontology, output_specs, return_index=True)

    train_dataset_node = None
    test_dataset_node = None
    model_node = None

    if train_dataset_index is not None:
        train_dataset_node =  transformation_outputs[train_dataset_index]
    if test_dataset_index is not None:
        test_dataset_node = transformation_outputs[test_dataset_index]
    if model_index is not None:
        model_node = transformation_outputs[model_index]
    if train_dataset_index is None and test_dataset_index is None:
        output_data_index = graph_queries.identify_data_io(ontology, output_specs, return_index=True)
        if not output_data_index is None:
            train_dataset_node = transformation_outputs[output_data_index]
    
    return step, train_dataset_node, test_dataset_node, model_node, engine



def build_general_workflow(workflow_name: str, ontology: Graph, dataset: URIRef, main_component: URIRef,
                           transformations: List[URIRef], intent_graph:Graph) -> Tuple[Graph, URIRef]:
    
    tqdm.write("\n\n BUILDING WORKFLOW")

    workflow_graph = get_graph_xp()
    workflow = ab.term(workflow_name)
    workflow_graph.add((workflow, RDF.type, tb.Workflow))
    task_order = 0

    intent_iri = graph_queries.get_intent_iri(intent_graph)
    max_imp_level = int(next(intent_graph.objects(intent_iri, tb.has_complexity), None))

    dataset_node = ab.term(f'{workflow_name}-original_dataset')

    copy_subgraph(ontology, dataset, workflow_graph, dataset_node)

    format = next(workflow_graph.objects(dataset_node,dmop.fileFormat,unique=True),Literal("unknown")).value

    knime_compatible = True

    if format == "CSV":
        loader_component = cb.term('component-csv_local_reader')
        saver_component = cb.term('component-csv_local_writer')
    else:
        loader_component = cb.term('component-data_reader_component')
        saver_component = cb.term('component-data_writer_component')
        knime_compatible = False

    loader_step = add_loader_step(ontology, workflow_graph, workflow, dataset_node,loader_component)
    task_order += 1

    previous_train_step = loader_step
    previous_test_step = None

    dataset_node = dataset_node
    test_dataset_node = None


    for train_component in [*transformations, main_component]:
        test_component = next(ontology.objects(train_component, tb.hasApplier, True), None)
        same = train_component == test_component

        step, dataset_node, output_test_dataset_node, model_node, engine = add_component(ontology, intent_graph, workflow_graph, workflow, workflow_name, max_imp_level, train_component, 
                             task_order, previous_train_step, dataset_node, None)
        previous_train_step = step
        if not output_test_dataset_node is None:
            test_dataset_node = output_test_dataset_node

        knime_compatible = knime_compatible & (engine == Literal('KNIME'))

        task_order += 1
        print(train_component, dataset_node, test_dataset_node, model_node)
         

        if test_component:
            print("same = ",same)
            previous_test_steps = [previous_test_step, step] if not same else [previous_test_step]
            print(test_component, previous_test_steps, test_dataset_node, model_node)

            test_step, test_dataset_node, _, _,engine  = add_component(ontology, intent_graph, workflow_graph, workflow, workflow_name, max_imp_level, test_component,
                            task_order, previous_test_steps, test_dataset_node, model_node)
            previous_test_step = test_step

            knime_compatible = knime_compatible & (engine == Literal('KNIME'))

            task_order += 1
            print(test_component, test_dataset_node)
        else:
            previous_test_step = step
    
    if test_dataset_node is not None:
        add_saver_step(ontology, workflow_graph, workflow, test_dataset_node, previous_test_step, task_order, saver_component)
        
        
    workflow_graph.add((workflow,tb.knimeCompatible,Literal(knime_compatible)))
                
    return workflow_graph, workflow

def get_algorithms_and_implementations_to_solve_task(ontology: Graph, shape_graph, intent_graph: Graph,log: bool = False):
    dataset, task, algorithm, intent_iri = get_intent_info(intent_graph)

    if log:
        tqdm.write(f'Intent: {intent_iri.fragment}')
        tqdm.write(f'Dataset: {dataset.fragment}')
        tqdm.write(f'Task: {task.fragment}')
        tqdm.write(f'Algorithm: {algorithm.fragment if algorithm is not None else [algo.fragment for algo in get_algorithms_from_task_constrained(ontology, shape_graph,task)]}')
        tqdm.write('-------------------------------------------------')

    algs = algorithm if not algorithm is None else get_algorithms_from_task_constrained(ontology,shape_graph,task)
    
    pot_impls = []
    for al in algs:
        pot_impls.extend(get_potential_implementations_constrained(ontology, shape_graph, al))
    
    return algs, pot_impls

def build_workflows(ontology: Graph, shape_graph: Graph, intent_graph: Graph, pot_impls, log: bool = False) -> List[Graph]:

    dataset, task, algorithm, intent_iri = get_intent_info(intent_graph)
    component_threshold = float(next(intent_graph.objects(intent_iri, tb.has_component_threshold), None))
    max_imp_level = int(next(intent_graph.objects(intent_iri, tb.has_complexity), None))

    if log:
        tqdm.write(f'Preprocessing Component Percentage Threshold: {component_threshold*100}%')
        tqdm.write(f'Maximum complexity level: {max_imp_level}')
        tqdm.write('-------------------------------------------------')

    impls_with_shapes = [
        (implementation, graph_queries.get_implementation_input_specs(ontology, implementation,max_imp_level))
        for implementation in pot_impls]
    
    components = [
        (c, impl, inputs)
        for impl, inputs in impls_with_shapes
        for c in get_implementation_components_constrained(ontology, shape_graph, impl)
    ]


    if log:
        for component, implementation, inputs in components:
            tqdm.write(f'Component: {component.fragment} ({implementation.fragment})')
            for im_input in inputs:
                tqdm.write(f'\tInput: {[x.fragment for x in im_input]}')
        tqdm.write('-------------------------------------------------')

    workflow_order = 0
    workflows = []


    for component, implementation, inputs in tqdm(components, desc='Components', position=1):
        if log:
            tqdm.write(f'Component: {component.fragment} ({implementation.fragment})')
        shapes_to_satisfy = graph_queries.identify_data_io(ontology, inputs)
        assert shapes_to_satisfy is not None and len(shapes_to_satisfy) > 0
        if log:
            tqdm.write(f'\tData input: {[x.fragment for x in shapes_to_satisfy]}')

        unsatisfied_shapes = [shape for shape in shapes_to_satisfy if
                              not satisfies_shape(ontology, ontology, shape, dataset)]
        print(f'UNSATISFIED SHAPES: {unsatisfied_shapes}')

        available_transformations = { shape: []
                                     for shape in unsatisfied_shapes}

        for shape in unsatisfied_shapes:
            for imp in find_implementations_to_satisfy_shape_constrained(ontology, shape_graph, shape, exclude_appliers=True):
                available_transformations[shape].extend(get_implementation_components_constrained(ontology,shape_graph,imp))
 
        print(f'AVAILABLE TRANSFORMATIONS: {available_transformations}')
        for tr, methods in available_transformations.items():
            tqdm.write(f'METHOD: {str(tr)}, {str(methods)}')
            tqdm.write(f'COMPONENT THRESHOLD: {str(component_threshold)}')

            best_components = get_best_components(ontology, task, methods, dataset, component_threshold)

            available_transformations[tr] = list(best_components.keys())

        print(f'REFINED TRANSFORMATIONS: {available_transformations}')
                    


        if log:
            tqdm.write(f'\tUnsatisfied shapes: ')
            for shape, transformations in available_transformations.items():
                tqdm.write(f'\t\t{shape.fragment}: {[x.fragment for x in transformations]}')

        transformation_combinations = list(
            enumerate(itertools.product(*available_transformations.values())))

        transformation_combinations_constrained = prune_workflow_combinations(ontology, shape_graph, transformation_combinations,component)
        #ontology.serialize('./tmp.ttl',format="turtle")
        if log:
            tqdm.write(f'\tTotal combinations: {len(transformation_combinations_constrained)}')

        for i, transformation_combination in tqdm(transformation_combinations_constrained, desc='Transformations', position=0,
                                                  leave=False):
            if log:
                tqdm.write(
                    f'\t\tCombination {i + 1} / {len(transformation_combinations_constrained)}: {[x.fragment for x in transformation_combination]}')

            workflow_name = f'workflow_{workflow_order}_{intent_iri.fragment}_{uuid.uuid4()}'.replace('-', '_')
            
            wg, w = build_general_workflow(workflow_name, ontology, dataset, component,
                                           transformation_combination, intent_graph = intent_graph)

            wg.add((w, tb.generatedFor, intent_iri))
            wg.add((intent_iri, RDF.type, tb.Intent))

            if log:
                tqdm.write(f'\t\tWorkflow {workflow_order}: {w.fragment}')

            workflows.append(wg)
            workflow_order += 1
    return workflows
    
