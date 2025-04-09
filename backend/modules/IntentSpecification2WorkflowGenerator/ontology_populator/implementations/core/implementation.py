import uuid
from typing import List, Union

from rdflib.collection import Collection

import os 
import sys
from .parameter import Parameter
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from common import *


LiteralValue = Union[str, bool, int, float, None]


class Implementation:
    def __init__(self, name: str, algorithm: URIRef,
                 parameters: List[Parameter],
                 input: List[Union[URIRef, List[URIRef]]] = None,
                 output: List[URIRef] = None,
                 implementation_type=tb.Implementation,
                 counterpart: 'Implementation' = None,
                 namespace: Namespace = cb,
                 ) -> None:
        super().__init__()
        self.name = name
        self.url_name = f'implementation-{self.name.replace(" ", "_").replace("-", "_").lower()}'
        self.namespace = namespace
        self.uri_ref = self.namespace[self.url_name]
        self.parameters = {param: param for param in parameters}
        self.algorithm = algorithm
        self.input = input or []
        self.output = output or []
        assert implementation_type in {tb.Implementation, tb.LearnerImplementation, tb.ApplierImplementation, tb.VisualizerImplementation}
        self.implementation_type = implementation_type
        self.counterpart = counterpart
        if self.counterpart is not None:
            assert implementation_type in {tb.LearnerImplementation, tb.ApplierImplementation, tb.VisualizerImplementation}
            if isinstance(self.counterpart, list):
                for c in self.counterpart:
                    print(c)
                    if c.counterpart is None:
                        c.counterpart = self
            elif self.counterpart.counterpart is None:
                self.counterpart.counterpart = self

        for parameter in self.parameters.values():
            parameter.uri_ref = self.namespace[f'{self.url_name}-{parameter.url_name}']

    def add_to_graph(self, g: Graph):

        # Base triples
        g.add((self.uri_ref, RDF.type, self.implementation_type))
        g.add((self.uri_ref, RDFS.label, Literal(self.name)))
        g.add((self.uri_ref, tb.implements, self.algorithm))
        g.add((self.uri_ref, tb.engine, Literal('Simple')))


        def add_dataspectag_node(shape, dataspec_node):
            dataspectag_node = BNode()
            g.add((dataspectag_node, RDF.type, tb.DataSpecTag))
            if isinstance(shape, tuple) and len(shape) >= 2: #user defined input shape importance level
                g.add((dataspectag_node, tb.hasDatatag,shape[0]))
                g.add((dataspectag_node, tb.hasImportanceLevel, Literal(shape[1]))) 
            else: #default importance level (critical)
                g.add((dataspectag_node, tb.hasDatatag, shape))
                g.add((dataspectag_node, tb.hasImportanceLevel, Literal(0)))
            g.add((dataspec_node, tb.hasSpecTag, dataspectag_node))


        # Input triples
        for i, input_tag in enumerate(self.input):
            input_node = BNode()
            g.add((input_node, RDF.type, tb.DataSpec)) 
            g.add((self.uri_ref, tb.specifiesInput, input_node))
            g.add((input_node, tb.has_position, Literal(i)))

            if isinstance(input_tag, list):
                for input in input_tag:
                    add_dataspectag_node(input, input_node)
            else:
                print(input_tag)
                add_dataspectag_node(input_tag, input_node)               

        # Output triples
        for i, output_tag in enumerate(self.output):
            output_node = BNode()
            g.add((output_node, RDF.type, tb.DataSpec)) 
            g.add((self.uri_ref, tb.specifiesOutput, output_node))
            g.add((output_node, tb.has_position, Literal(i)))
            add_dataspectag_node(output_tag,output_node)

        # Parameter triples
        for i, parameter in enumerate(self.parameters.values()):
            g.add((parameter.uri_ref, RDF.type, tb.Parameter))
            g.add((parameter.uri_ref, RDFS.label, Literal(parameter.label)))
            g.add((parameter.uri_ref, tb.has_datatype, parameter.datatype))
            g.add((parameter.uri_ref, tb.has_position, Literal(i)))
            g.add((parameter.uri_ref, tb.has_condition, Literal(parameter.condition)))
            if isinstance(parameter.default_value, URIRef):
                g.add((parameter.uri_ref, tb.has_defaultvalue, parameter.default_value))
            else:
                g.add((parameter.uri_ref, tb.has_defaultvalue, Literal(parameter.default_value)))
            g.add((self.uri_ref, tb.hasParameter, parameter.uri_ref))

        return self.uri_ref

    def add_counterpart_relationship(self, g: Graph):
        if self.counterpart is None:
            return
        counters = self.counterpart if isinstance(self.counterpart, list) else [self.counterpart]
        for c in counters:
            counterpart_query = f'''
            PREFIX tb: <{tb}>
            SELECT ?self ?counterpart
            WHERE {{
                ?self a <{self.implementation_type}> ;
                    rdfs:label "{self.name}" .
                ?counterpart a <{c.implementation_type}> ;
                    rdfs:label "{c.name}" .
            }}
            '''
            result = g.query(counterpart_query).bindings
            assert len(result) == 1
            self_node = result[0][Variable('self')]
            relationship = tb.hasApplier if self.implementation_type == tb.LearnerImplementation else tb.hasLearner
            counterpart_node = result[0][Variable('counterpart')]
            g.add((self_node, relationship, counterpart_node))
