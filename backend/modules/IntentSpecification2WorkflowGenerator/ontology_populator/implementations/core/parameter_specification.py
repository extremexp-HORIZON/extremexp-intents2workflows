from typing import Union

import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from common import *
from urllib.parse import quote


class ParameterSpecification:
    def __init__(self, parameter: URIRef, #this has Parameter type
                 value: Union[URIRef, Literal] = None,
                 namespace: Namespace = ab) -> None:
        super().__init__()
        self.parameter = parameter
        self.value = value
        self.namespace = namespace

        self.url_name = quote(f'{self.parameter.url_name}_{self.value}_specification'.replace(' ', '_').lower(), safe=":/-_")

        self.uri_ref = namespace[self.url_name]