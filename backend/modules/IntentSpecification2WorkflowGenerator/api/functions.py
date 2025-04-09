import zipfile
import sys
import os

from rdflib.term import Node

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from pipeline_generator.optimized_pipeline_generator import *
from pipeline_generator.graph_queries import *

def get_custom_ontology(path):
    graph = get_graph_xp()
    ontologies = [
        r'ontologies/tbox.ttl',
        r'ontologies/cbox.ttl',
        r'ontologies/abox.ttl',
        path
    ]
    for o in ontologies:
        graph.parse(o, format="turtle")

    DeductiveClosure(OWLRL_Semantics).expand(graph)
    return graph

def get_custom_ontology_only_problems():
    graph = get_graph_xp()
    ontologies = [
        r'ontologies/tbox.ttl',
        r'ontologies/cbox.ttl',
        r'ontologies/abox.ttl',
    ]
    for o in ontologies:
        graph.parse(o, format="turtle")

    DeductiveClosure(OWLRL_Semantics).expand(graph)
    return graph

def connect_algorithms(ontology, shape_graph, algos_list):
    impls_algos = {imp : algo + "-Train" if "learner" in imp.fragment else algo
                   for algo in algos_list for imp in get_potential_implementations_constrained(ontology, shape_graph, algo,exclude_appliers=False)}
    print(impls_algos)

    linked_impls = {}

    impls_list = list(impls_algos.keys())
    
    for preceding_impl in impls_list:
        following_impls = impls_list

        out_specs = get_implementation_output_specs(ontology, preceding_impl)
        out_spec_set = {out_sp for out_spec in out_specs for out_sp in out_spec}

        preceding_impl_key = impls_algos[preceding_impl]
        linked_impls.setdefault(preceding_impl_key, [])
        
        for following_impl in following_impls:

            in_specs = get_implementation_input_specs(ontology, following_impl)
            in_spec_set = {in_sp for in_spec in in_specs for in_sp in in_spec}

            if out_spec_set & in_spec_set:
                following_impl_key = impls_algos[following_impl]

                if following_impl_key not in linked_impls[preceding_impl_key]:
                    linked_impls[preceding_impl_key].append(following_impl_key)

    return linked_impls



def abstract_planner(ontology: Graph, shape_graph: Graph, intent: Graph) -> Tuple[
    Dict[Node, Dict[Node, List[Node]]], Dict[Node, List[Node]]]:

    algs, impls = get_algorithms_and_implementations_to_solve_task(ontology, shape_graph, intent, log=True)
    algs_shapes = {}
    alg_plans = {alg: [] for alg in algs}
    available_algs = [] # to make sure abstract plans are only made for algorithms with at least one available implementation
    for impl in impls:
        alg = next(ontology.objects(impl, tb.implements)), 
        (impl, RDF.type, tb.Implementation) in ontology and (tb.ApplierImplementation not in ontology.objects(impl, RDF.type))

        algs_shapes[alg[0]] = get_implementation_input_specs(ontology, impl)[0] #assuming data shapes is on input 0

        alg_plans[alg[0]].append(impl)

        available_algs.append(alg[0])
    
    plans = {}
    #print(algs_shapes)
    for alg in available_algs:
        if cb.TrainTabularDatasetShape in algs_shapes[alg]:
            plans[alg] = connect_algorithms(ontology, shape_graph,[cb.DataLoading, cb.Partitioning, alg, cb.DataStoring])
        else:
            plans[alg] = connect_algorithms(ontology, shape_graph, [cb.DataLoading, alg])
    #print(plans)
    return plans, alg_plans
    

def workflow_planner(ontology: Graph, shape_graph: Graph, implementations: List, intent: Graph):
    return build_workflows(ontology, shape_graph, intent, implementations, log=True)

def getKnimeCompatibility(workflow_graph: Graph):
    workflow_id = next(workflow_graph.subjects(RDF.type, tb.Workflow, unique=True),None)
    compatible = next(workflow_graph.objects(workflow_id,tb.knimeCompatible),False).value #Incompatible by default
    return compatible


def logical_planner(ontology: Graph, workflow_plans: List[Graph]):
    logical_plans = {}
    counter = {}

    for workflow_plan in workflow_plans:
        steps = list(workflow_plan.subjects(RDF.type, tb.Step))
        step_components = {step: next(workflow_plan.objects(step, tb.runs)) for step in steps}
        step_next = {step: list(workflow_plan.objects(step, tb.followedBy)) for step in steps}
        logical_plan = {
            step_components[step]: [step_components[s] for s in nexts] for step, nexts in step_next.items()
        }

        main_component = next((comp for comp in logical_plan.keys() 
                if logical_plan[comp] == [cb.term('component-csv_local_writer')]
                or logical_plan[comp] == [cb.term('component-data_writer_component')] #TODO main component transparent to specific component names
                or logical_plan[comp] == []), None)
        if (main_component, RDF.type, tb.ApplierImplementation) in ontology:
            options = list(ontology.objects(main_component, tb.hasLearner))
            main_component = next(o for o in options if (None, None, o) in workflow_plan)
        if main_component not in counter:
            counter[main_component] = 0
        plan_id = (f'{main_component.fragment.split("-")[1].replace("_", " ").replace(" learner", "").title()} '
                   f'{counter[main_component]}')
        counter[main_component] += 1
        logical_plans[plan_id] = {"logical_plan": logical_plan, "graph": workflow_plan.serialize(format="turtle"), "knimeCompatible": getKnimeCompatibility(workflow_plan)}

    return logical_plans

def compress(folder: str, destination: str) -> None:
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, folder)
                zipf.write(file_path, arcname=os.path.join(os.path.basename(folder), archive_path))
