from typing import Dict, List, Set, Tuple, Type, Union
from rdflib import Graph, URIRef


from common import *


def get_intent_iri(intent_graph: Graph) -> URIRef:
    intent_iri_query = f"""
PREFIX tb: <{tb}>
SELECT ?iri
WHERE {{
    ?iri a tb:Intent .
}}
"""
    result = intent_graph.query(intent_iri_query).bindings
    assert len(result) == 1
    return result[0]['iri']


def get_intent_dataset_task(intent_graph: Graph, intent_iri: URIRef) -> Tuple[URIRef, URIRef, URIRef]:
    dataset_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT ?dataset ?task ?algorithm
    WHERE {{
        {intent_iri.n3()} a tb:Intent .
        {intent_iri.n3()} tb:overData ?dataset .
        ?task tb:tackles {intent_iri.n3()} .
        OPTIONAL {{{intent_iri.n3()} tb:specifies ?algorithm}}
    }}
"""
    result = intent_graph.query(dataset_task_query).bindings[0]
    return result['dataset'], result['task'], result.get('algorithm', None)


def get_intent_parameters(intent_graph: Graph):
    intent_parameters_query = f"""
    PREFIX tb:<{tb}>
    SELECT ?exp_param ?param_val
    WHERE{{
        ?param_val tb:forParameter ?exp_param .
    }}
"""
    result = intent_graph.query(intent_parameters_query).bindings
    return {param['exp_param']:param['param_val'] for param in result}


def get_algorithms_from_task(ontology: Graph, task: URIRef) -> URIRef:

    algorithm_task_query = f"""
    PREFIX tb: <{tb}>
    SELECT DISTINCT ?algorithm
    WHERE{{
        ?algorithm a tb:Algorithm ;
                   tb:solves {task.n3()} .
        ?impl tb:implements ?algorithm .
        FILTER NOT EXISTS{{
            ?algorithm a tb:Algorithm ;
                   tb:solves {task.n3()} .
            ?impl a tb:ApplierImplementation.
        }}
    }}
"""
    result = ontology.query(algorithm_task_query).bindings
    algos = [algo['algorithm'] for algo in result]
    return algos


def get_exposed_parameters(ontology: Graph, task: URIRef, algorithm: URIRef):

    expparams_query = f"""
    PREFIX tb: <{tb}>
    SELECT DISTINCT ?exp_param ?label ?value ?condition
    WHERE {{
        {task.n3()} a tb:Task .
        {{
            {"BIND(" + algorithm.n3() + " AS ?algorithm) ." if algorithm else f"?algorithm tb:solves {task.n3()} ."}
        }}
        # {'?algorithm' if algorithm is None else algorithm.n3()} tb:solves {task.n3()} .
        ?imp tb:implements ?algorithm .
        ?com tb:hasImplementation ?imp ;
            tb:exposesParameter ?exp_param .
        ?exp_param tb:has_defaultvalue ?value;
                tb:has_condition ?condition ;
                rdfs:label ?label .
    }}
    """
    
    result = ontology.query(expparams_query).bindings
    return result 

def get_implementation_input_specs(ontology: Graph, implementation: URIRef, maxImportanceLevel: int = 3) -> List[List[URIRef]]:
    input_spec_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?position (GROUP_CONCAT(?shape; SEPARATOR=",") AS ?shapes)
        WHERE {{
            {implementation.n3()} tb:specifiesInput ?spec .
            ?spec a tb:DataSpec ;
                tb:hasSpecTag ?sptg ;
                tb:has_position ?position .
            ?sptg 
                tb:hasImportanceLevel ?imp ;
                tb:hasDatatag ?shape . 
            FILTER(?imp <= {int(maxImportanceLevel)}) .

        }}
		GROUP BY ?position
        ORDER BY ?position
    """ #TODO check shape type datatag
    results = ontology.query(input_spec_query).bindings

    if results == [{}]:
        return []
    shapes = [unpack_shapes(result['shapes']) for result in results]
    return shapes


def get_implementation_output_specs(ontology: Graph, implementation: URIRef) -> List[List[URIRef]]:
    output_spec_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?position (GROUP_CONCAT(?shape; SEPARATOR=",") AS ?shapes)
        WHERE {{
            {implementation.n3()} tb:specifiesOutput ?spec .
            ?spec a tb:DataSpec ;
                tb:hasSpecTag ?sptg ;
                tb:has_position ?position .
            ?sptg tb:hasDatatag ?shape . 
        }}
		GROUP BY ?position
        ORDER BY ?position
    """ #TODO check shape type datatag

    results = ontology.query(output_spec_query).bindings
    if results == [{}]:
        return []
    shapes = [unpack_shapes(result['shapes']) for result in results]
    return shapes

def unpack_shapes(shapes:str) -> List[URIRef]:
    spec_shapes = shapes.split(',')
    spec_shapes_uris = [URIRef(s) for s in spec_shapes]

    # Logical planner is only executed correctly if traintabular shape goes first. TODO Change this behaviour
    if cb.TrainTabularDatasetShape in spec_shapes_uris:
        spec_shapes_uris.remove(cb.TrainTabularDatasetShape)
        spec_shapes_uris.insert(0,cb.TrainTabularDatasetShape)

    if cb.TestTabularDatasetShape in spec_shapes_uris:
        spec_shapes_uris.remove(cb.TestTabularDatasetShape)
        spec_shapes_uris.insert(0,cb.TestTabularDatasetShape)
    return spec_shapes_uris


# def get_all_implementations(ontology: Graph, task_iri: URIRef = None, algorithm: URIRef = None) -> \
#         List[Tuple[URIRef, List[URIRef]]]:
#     main_implementation_query = f"""
#     PREFIX tb: <{tb}>
#     SELECT DISTINCT ?implementation
#     WHERE {{
#         ?implementation a tb:Implementation ;
#             tb:implements {algorithm.n3() if algorithm is not None else '?algorithm'} .
#         ?algorithm a tb:Algorithm ;
#             tb:solves {task_iri.n3() if task_iri is not None else '?task'} .
#         ?subtask tb:subtaskOf* {task_iri.n3() if task_iri is not None else '?task'} .
#     }}
# """
#     results = ontology.query(main_implementation_query).bindings
#     implementations = [result['implementation'] for result in results]

#     implementations_with_shapes = [
#         (implementation, get_implementation_input_specs(ontology, implementation))
#         for implementation in implementations]

#     return implementations_with_shapes

def get_potential_implementations(ontology: Graph, algorithm: URIRef, exclude_appliers=True) -> \
        List[URIRef]:
    main_implementation_query = f"""
    PREFIX tb: <{tb}>
    SELECT DISTINCT ?implementation
    WHERE {{
        ?implementation a tb:Implementation ;
            tb:implements {algorithm.n3()} .
        {algorithm.n3()} a tb:Algorithm ;
        { "FILTER NOT EXISTS {?implementation a tb:ApplierImplementation . }" if exclude_appliers else ''}
    }}
"""
    results = ontology.query(main_implementation_query).bindings
    implementations = [result['implementation'] for result in results]

    return implementations

def get_component_implementation(ontology: Graph, component: URIRef) -> URIRef:
    implementation_query = f"""
        PREFIX tb: <{tb}>
        PREFIX cb: <{cb}>
        SELECT ?implementation
        WHERE {{
            {component.n3()} tb:hasImplementation ?implementation .
        }}
    """
    result = ontology.query(implementation_query).bindings
    assert len(result) == 1
    return result[0]['implementation']

def get_implementation_components(ontology: Graph, implementation: URIRef) -> List[URIRef]:
    components_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?component
        WHERE {{
            ?component tb:hasImplementation {implementation.n3()} .
        }}
    """
    results = ontology.query(components_query).bindings
    return [result['component'] for result in results]

def find_implementations_to_satisfy_shape(ontology: Graph, shape: URIRef, exclude_appliers: bool = False) -> List[URIRef]:
    implementation_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?implementation
        WHERE {{
            {{
                ?implementation a tb:Implementation;
                                tb:specifiesOutput ?spec .
            }}
            FILTER NOT EXISTS {{
                ?implementation a tb:{'Applier' if exclude_appliers else ''}Implementation .
                                # tb:specifiesOutput ?spec .
            }}
            ?spec tb:hasSpecTag ?sptg .
            ?sptg tb:hasDatatag {shape.n3()} .
        }}
    """
    result = ontology.query(implementation_query).bindings
    implementations = [x['implementation'] for x in result]

    return implementations


def identify_data_io(ontology: Graph, ios: List[List[URIRef]], train: bool = False, test: bool = False, return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, io_shapes in enumerate(ios):
        for io_shape in io_shapes:
            if ((io_shape, SH.targetClass, dmop.TabularDataset) in ontology 
                or (io_shape, SH.targetClass, cb.TabularDatasetShape) in ontology 
                or io_shape.fragment == "TabularDatasetShape"):

                if test:
                    test_query = f'''
                    PREFIX sh: <{SH}>
                    PREFIX rdfs: <{RDFS}>
                    PREFIX cb: <{cb}>
                    PREFIX dmop: <{dmop}>

                    ASK {{
                        {{
                        {io_shape.n3()} a sh:NodeShape ;
                                        sh:targetClass dmop:TabularDataset ;
                                        sh:property [
                                            sh:path dmop:isTestDataset ;
                                            sh:hasValue true
                                        ] .
                        }}
                    }}
                    '''
                    result = ontology.query(test_query).askAnswer
                    if result:
                        return i if return_index else io_shapes
                    
                if train:
                    train_query = f'''
                    PREFIX sh: <{SH}>
                    PREFIX rdfs: <{RDFS}>
                    PREFIX cb: <{cb}>
                    PREFIX dmop: <{dmop}>

                    ASK {{
                        {{
                        {io_shape.n3()} a sh:NodeShape ;
                                        sh:targetClass dmop:TabularDataset ;
                                        sh:property [
                                            sh:path dmop:isTrainDataset ;
                                            sh:hasValue true
                                        ] .
                        }}
                    }}
                    '''
                    result = ontology.query(train_query).askAnswer
                    if result:
                        return i if return_index else io_shapes
                
                if not train and not test:
                    return i if return_index else io_shapes
            
def identify_model_io(ontology: Graph, ios: List[List[URIRef]], return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, io_shapes in enumerate(ios):
        for io_shape in io_shapes:
            query = f'''
    PREFIX sh: <{SH}>
    PREFIX rdfs: <{RDFS}>
    PREFIX cb: <{cb}>

    ASK {{
      {{
        {io_shape.n3()} sh:targetClass ?targetClass .
        ?targetClass rdfs:subClassOf* cb:Model .
      }}
      UNION
      {{
        {io_shape.n3()} rdfs:subClassOf* cb:Model .
      }}
    }}
'''
            if ontology.query(query).askAnswer:
                return i if return_index else io_shapes

def identify_visual_io(ontology: Graph, ios: List[List[URIRef]], return_index: bool = False) -> Union[int, List[URIRef]]:
    for i, io_shapes in enumerate(ios):
        for io_shape in io_shapes:
            query = f'''
    PREFIX sh: <{SH}>
    PREFIX rdfs: <{RDFS}>
    PREFIX cb: <{cb}>

    ASK {{
      {{
        {io_shape.n3()} sh:targetClass ?targetClass .
        ?targetClass rdfs:subClassOf* cb:Visualization .
      }}
      UNION
      {{
        {io_shape.n3()} rdfs:subClassOf* cb:Visualization .
      }}
    }}
'''
            if ontology.query(query).askAnswer:
                return i if return_index else io_shapes

def get_shape_target_class(ontology: Graph, shape: URIRef) -> URIRef:
    return ontology.query(f"""
        PREFIX sh: <{SH}>
        SELECT ?targetClass
        WHERE {{
            <{shape}> sh:targetClass ?targetClass .
        }}
    """).bindings[0]['targetClass']


def get_implementation_parameters(ontology: Graph, implementation: URIRef) -> Dict[
    URIRef, Tuple[Literal, Literal, Literal]]:
    parameters_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?parameter ?value ?order ?condition
        WHERE {{
            <{implementation}> tb:hasParameter ?parameter .
            ?parameter tb:has_defaultvalue ?value ;
                       tb:has_condition ?condition ;
                       tb:has_position ?order .
        }}
        ORDER BY ?order
    """
    results = ontology.query(parameters_query).bindings
    return {param['parameter']: (param['value'], param['order'], param['condition']) for param in results}


def get_component_non_overriden_parameters(ontology: Graph, component: URIRef) -> Dict[
    URIRef, Tuple[Literal, Literal, Literal]]:
    parameters_query = f"""
        PREFIX tb: <{tb}>
        SELECT ?parameter ?parameterValue ?position ?condition
        WHERE {{
            {component.n3()} tb:hasImplementation ?implementation .
            ?implementation tb:hasParameter ?parameter .
            ?parameter tb:has_defaultvalue ?parameterValue ;
                       tb:has_position ?position ;
                       tb:has_condition ?condition .
            FILTER NOT EXISTS {{
                ?parameter tb:specifiedBy ?parameterSpecification .
            }}
        }}
        ORDER BY ?position
    """
    results = ontology.query(parameters_query).bindings
    return {param['parameter']: (param['parameterValue'], param['position'], param['condition']) for param in results}


def get_component_transformations(ontology: Graph, component: URIRef) -> List[URIRef]:
    transformation_query = f'''
        PREFIX tb: <{tb}>
        SELECT ?transformation
        WHERE {{
            <{component}> tb:hasTransformation ?transformation_list .
            ?transformation_list rdf:rest*/rdf:first ?transformation .
        }}
    '''
    transformations = ontology.query(transformation_query).bindings
    return [x['transformation'] for x in transformations]


def get_inputs_all_columns(graph: Graph, inputs: List[URIRef]) -> List:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
        }}
    """
    columns = graph.query(columns_query).bindings
    return [x['label'].value for x in columns]


def get_inputs_label_name(graph: Graph, inputs: List[URIRef]) -> str:
    
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)

    label_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isLabel true ;
                    dmop:hasColumnName ?label .

        }}
    """
    
    results = graph.query(label_query).bindings
    
    if results is not None and len(results) > 0:
        return results[0]['label']
    

def get_exact_column(graph: Graph, inputs: List[URIRef], column_name: str) -> str:
    
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)

    column_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:hasColumnName ?label .
            FILTER(?label = "{column_name}")
        }}
    """
    
    results = graph.query(column_query).bindings
    
    if results is not None and len(results) > 0:
        return results[0]['label']


def get_inputs_numeric_columns(graph: Graph, inputs: List[URIRef]) -> str:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
            FILTER(?type IN (dmop:Float, dmop:Int, dmop:Number, dmop:Double, dmop:Long, dmop:Short, dmop:Integer))
        }}
    """
    columns = graph.query(columns_query).bindings
 
    return [x['label'].value for x in columns]


def get_inputs_categorical_columns(graph: Graph, inputs: List[URIRef]) -> str:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)

    categ_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?label
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isCategorical true ;
                    dmop:hasDataPrimitiveTypeColumn ?type ;
                    dmop:hasColumnName ?label .
        }}
    """
    columns = graph.query(categ_query).bindings

    return [x['label'].value for x in columns]

def get_inputs_feature_types(graph: Graph, inputs: List[URIRef]) -> Set[Type]:
    data_input = next(i for i in inputs if (i, RDF.type, dmop.TabularDataset) in graph)
    columns_query = f"""
        PREFIX rdfs: <{RDFS}>
        PREFIX dmop: <{dmop}>

        SELECT ?type
        WHERE {{
            {data_input.n3()} dmop:hasColumn ?column .
            ?column dmop:isFeature true ;
                    dmop:hasDataPrimitiveTypeColumn ?type .
        }}
    """
    columns = graph.query(columns_query).bindings
    mapping = {
        dmop.Float: float,
        dmop.Int: int,
        dmop.Integer: int,
        dmop.Number: float,
        dmop.Double: float,
        dmop.String: str,
        dmop.Boolean: bool,
    }
    return set([mapping[x['type']] for x in columns])

def retreive_component_rules(graph: Graph, task:URIRef, component: URIRef):
    preference_query = f"""
        PREFIX rdfs: <{RDFS}>

        SELECT ?datatag ?weight ?component_rank
        WHERE {{
            {component.n3()} tb:hasRule ?rule .
            ?rule tb:relatedtoDatatag ?datatag ;
                  tb:relatedtoTask {task.n3()} ;
                  tb:has_rank ?component_rank .
            ?datatag tb:has_weight ?weight .
        }}
    """
    results = graph.query(preference_query).bindings

    return {result['datatag']: (float(result['weight']), int(result['component_rank'])) for result in results}


def get_engine(graph: Graph, implementation:URIRef):
    return next(graph.objects(implementation, tb.engine, unique=True),None)