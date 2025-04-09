import os
import sys
import tempfile
import zipfile
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Tuple, Dict, List
import jinja2

from tqdm import tqdm

translator_dir = os.path.join(os.path.abspath(os.path.join('..')))
sys.path.append(translator_dir)

root_dir = os.path.join(os.path.abspath(os.path.join('../..')))
sys.path.append(root_dir)

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(["pipeline_translator/knime/templates", "templates"])) #the double path ensures expected performance on terminal and api execution
from pipeline_translator.core.translator_common_functions import *

from rdflib import Graph, URIRef, RDF, XSD

try:
    import easygui # type: ignore
except ImportError:
    easygui = None



def get_knime_properties(ontology: Graph, implementation: URIRef) -> Dict[str, str]:
    results = {}
    for p, o in ontology.predicate_objects(implementation):
        if p.fragment.startswith('knime'):
            results[p.fragment[6:]] = o.value
            # print(f"THIS: {p.fragment[6:]} ---> {o.value}")
    return results

def update_param_hierarchy(param_dict:Dict, path: List[str], element):

    if len(path) == 0:
        if element[0] != "$$SKIP$$":
            param_dict['elements'].append(element)
    else:
        level = path.pop(0)
        if level not in param_dict['folders']:
            param_dict['folders'][level] = {
                'folders': {},
                'elements': []
            }
        param_dict[level] = update_param_hierarchy(param_dict['folders'][level], path, element)
    
    return param_dict


def get_config_parameters(ontology: Graph, workflow_graph: Graph, step: URIRef):
    types = {
        XSD.string: 'xstring',
        cb.term('char'): 'xchar',
        XSD.int: 'xint',
        XSD.integer: 'xint',
        XSD.long: 'xlong',
        XSD.float: 'xdouble',
        XSD.double: 'xdouble',
        XSD.boolean: 'xboolean',
        RDF.List: ''
    }

    parameters = get_step_parameters(ontology, workflow_graph, step)
    param_dict = {'folders': {},
                  'elements': []}
    

    for key, value, path, value_type in parameters:
        if value_type == RDF.List:
            param_value = value.replace("[", "").replace("]", "").replace("\'", "").replace(" ","").split(',')
            arrayPath = path+'/'+key
            parameters.append( ("array-size", str(len(param_value)), arrayPath, XSD.int) )
            for i,param in enumerate(param_value):
                parameters.append((str(i),param,arrayPath,XSD.string))
        else:
            if value is None or (isinstance(value, str) and value.lower() == 'none'):
                param_value = None
            else:
                param_value = value

            param_dict = update_param_hierarchy(param_dict, path.split('/'),(str(key),param_value,types[value_type]))
    return param_dict


def create_step_file(ontology: Graph, workflow_graph: Graph, step: URIRef, folder, iterator: int) -> str:

    component, implementation = get_step_component_implementation(ontology, workflow_graph, step)
    properties = get_knime_properties(ontology, implementation)

    
    conf_params = get_config_parameters(ontology, workflow_graph, step)
    num_ports = get_number_of_output_ports(ontology, workflow_graph, step)

    step_template = environment.get_template("step.py.jinja")
    step_file = step_template.render(properties = properties,
                                     parameters = conf_params,
                                     num_ports = num_ports)
    
    path_name = properties["node-name"].replace('(', '_').replace(')', '_')
    
    subfolder_name = f'{path_name} (#{iterator})'
    subfolder = os.path.join(folder, subfolder_name)
    os.mkdir(subfolder)

    with open(os.path.join(subfolder, 'settings.xml'), encoding='UTF-8', mode='w') as file:
        file.write(step_file)

    return subfolder_name


def create_workflow_metadata_file(workflow_graph: Graph, folder: str) -> None:
    author = 'ODIN'
    date = datetime.today().strftime('%d/%m/%Y')
    workflow_name = next(workflow_graph.subjects(RDF.type, tb.Workflow, True)).fragment
    title = f'{get_workflow_intent_name(workflow_graph)} (Workflow {get_workflow_intent_number(workflow_graph)})'
    description = f'This workflow was automatically created from the logical workflow {workflow_name}.'
    url = 'ExtremeXP https://extremexp.eu/'
    tags = 'model training, training, testing'

    metadata_template = environment.get_template("metadata.py.jinja")
    workflow_metadata_file = metadata_template.render(author = author,
                                                      date = date,
                                                      workflow_name = workflow_name,
                                                      title = title,
                                                      description = description,
                                                      url = url,
                                                      tags = tags) 
    
    with open(os.path.join(folder, 'workflowset.meta'), 'w') as f:
        f.write(workflow_metadata_file)

def get_connections_config(workflow_graph: Graph, steps: List[URIRef]):
    connections = get_workflow_connections(workflow_graph)
    connections_ids = []
    for source, destination, source_port, destination_port in connections:
        connections_ids.append((steps.index(source), steps.index(destination), source_port+1, destination_port+1))
    
    return connections_ids


def create_workflow_file(ontology:Graph, workflow_graph: Graph, steps: List[URIRef], step_paths: List[str],
                         folder: str) -> None:
    
    is_applier = [ is_applier_step(ontology, workflow_graph, step) for step in steps]
    connections = get_connections_config(workflow_graph, steps)
    metadata_template = environment.get_template("workflow.py.jinja")
    workflow_file = metadata_template.render(steps = zip(step_paths,is_applier),
                                             connections = connections,
                                             date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %z'),
                                             author = "ODIN")

    with open(os.path.join(folder, 'workflow.knime'), encoding='UTF-8', mode='w') as f:
        f.write(workflow_file)


def package_workflow(folder: str, destination: str) -> None:
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                archive_path = os.path.relpath(file_path, folder)
                workflow_name = os.path.splitext(os.path.basename(destination))[0]
                zipf.write(file_path, arcname=os.path.join(workflow_name, archive_path))


def translate_graph(ontology: Graph, source_path: str, destination_path: str, keep_folder=False) -> None:
    tqdm.write('Creating new workflow')

    tqdm.write('\tCreating temp folder: ', end='')
    temp_folder = tempfile.mkdtemp()
    tqdm.write(temp_folder)

    tqdm.write('\tLoading workflow:', end=' ')
    graph = load_workflow(source_path)
    tqdm.write(next(graph.subjects(RDF.type, tb.Workflow, True)).fragment)

    tqdm.write('\tCreating workflow metadata file')
    create_workflow_metadata_file(graph, temp_folder)

    tqdm.write('\tBuilding steps')
    steps = get_workflow_steps(graph)
    step_paths = []
    for i, step in enumerate(steps):
        step_paths.append(create_step_file(ontology, graph, step, temp_folder, i))

    tqdm.write('\tCreating workflow file')
    create_workflow_file(ontology, graph, steps, step_paths, temp_folder)

    tqdm.write('\tCreating zip file')
    package_workflow(temp_folder, destination_path)

    if keep_folder:
        tqdm.write('\tCopying temp folder')
        shutil.copytree(temp_folder, destination_path[:-4])

    tqdm.write('\tRemoving temp folder')
    shutil.rmtree(temp_folder)
    tqdm.write('Done')
    tqdm.write('-' * 50)


def translate_graph_folder(ontology: Graph, source_folder: str, destination_folder: str, keep_folder=False) -> None:
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    assert os.path.exists(source_folder)

    workflows = [f for f in os.listdir(source_folder) if f.endswith('.ttl')]
    for workflow in tqdm(workflows):
        source_path = os.path.join(source_folder, workflow)
        destination_path = os.path.join(destination_folder, workflow[:-4] + '.knwf')
        translate_graph(ontology, source_path, destination_path, keep_folder)


def interactive():
    if easygui is None:
        source_folder = input('Source folder: ')
        destination_folder = input('Destination folder: ')
    else:
        source_folder = easygui.diropenbox('Source folder', 'Source folder', '.')
        print(f'Source folder: {source_folder}')
        destination_folder = easygui.diropenbox('Destination folder', 'Destination folder', '.')
        print(f'Destination folder: {destination_folder}')

    keep_folder = input('Keep workflows in folder format? [Y/n]: ').lower() not in ['n', 'no']

    translate_graph_folder(get_ontology(), source_folder, destination_folder, keep_folder=keep_folder)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        translate_graph_folder(get_ontology(), sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        translate_graph(get_ontology(), sys.argv[2], sys.argv[3], keep_folder=True)
    else:
        print('Interactive usage.')
        print('For non-interactive usage, use:')
        print('\tpython workflow_translator.py <source_folder> <destination_folder>')
        print('\tpython workflow_translator.py --keep <source_folder> <destination_folder>')
        interactive()
