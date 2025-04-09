import sys
import os
import jinja2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.translator_common_functions import *

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["pipeline_translator/dsl/templates", "templates"])) #the double path ensures expected performance on terminal and api execution

def get_task_implementations(ontology: Graph, workflow_graph:Graph) -> Tuple[List[URIRef],List[str]]:
    tasks = []
    task_implementations = {}

    steps = get_workflow_steps(workflow_graph)

    for step in steps:
        component, implementation = get_step_component_implementation(ontology,workflow_graph,step)
        task = get_implementation_task(ontology, implementation).fragment
        in_specs = get_input_specs(ontology, implementation)

        if any(cb.TrainTabularDatasetShape in spec for spec in in_specs):
            tasks.append("ModelTrain")
            task_implementations["ModelTrain"] = component.fragment
            tasks.append("ModelPredict")
            task_implementations["ModelPredict"] = component.fragment + "_predictor"
        elif tb.ApplierImplementation not in ontology.objects(implementation, RDF.type):
            tasks.append(task)
            task_implementations[task] = component.fragment
    
    return tasks, task_implementations

def get_steps_io(ontology:Graph, workflow_graph:Graph)->Tuple[List[List[URIRef]], List[List[URIRef]]]:
    steps = get_workflow_steps(workflow_graph)
    inputs = {}
    outputs = {}

    for step in steps:
        component, implementation = get_step_component_implementation(ontology,workflow_graph,step)
        task = get_implementation_task(ontology, implementation).fragment
        step_inputs = get_step_inputs(workflow_graph, step)
        step_outputs = get_step_outputs(workflow_graph, step)
        inputs[task] = step_inputs
        outputs[task] = step_outputs
    
    return inputs,outputs

def tranlate_graph_to_dsl(ontology: Graph, workflow_graph:Graph, header=True) -> str:
    tasks, task_implementations = get_task_implementations(ontology, workflow_graph)
    intent_name = get_workflow_intent_name(workflow_graph)
    workflow_name = 'Workflow_' + str(get_workflow_intent_number(workflow_graph))
    inputs, outputs = get_steps_io(ontology, workflow_graph)
    print(outputs[tasks[0]][0])
    or_dataset_path = get_data_path(workflow_graph, outputs[tasks[0]][0])

    workflow_template = environment.get_template("workflow.py.jinja")
    translation = workflow_template.render(intent_name = intent_name, 
                                           workflow_name = workflow_name,
                                           tasks = tasks,
                                           task_implementations = task_implementations,
                                           header = header,
                                           inputs = inputs,
                                           outputs = outputs,
                                           path = or_dataset_path)

    with open('test.txt', mode='w') as f:
        f.write(translation)

    return translation

def translate_graphs_to_dsl(ontology:Graph, workflow_graphs:List[Graph]) -> str:
    trans = []
    header = True
    for w in workflow_graphs:
        trans.append(tranlate_graph_to_dsl(ontology, w, header))
        header = False
    
    return "\n".join(trans)

