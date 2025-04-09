from common import *
from ontology_populator.implementations.core import *


data_reader_implementation = Implementation(
    name='Data Reader',
    algorithm=cb.DataLoading,
    parameters=[
        Parameter("Reader File", XSD.string, '$$PATH$$'),
    ],
    input=[],
    output=[
        cb.TabularDataset,
    ],
)

data_reader_component = Component(
    name='Data Reader component',
    implementation=data_reader_implementation,
    transformations=[
        LoaderTransformation(),
    ],
    overriden_parameters=[
    ],
    exposed_parameters=[
        # list(csv_reader_implementation.parameters.keys())[0]
        next((param for param in data_reader_implementation.parameters.keys() if param.label == 'Reader File'), None)
    ],
)

data_writer_implementation = Implementation(
    name='Data Writer',
    algorithm=cb.DataStoring,
    parameters=[
        Parameter('Writer File', XSD.string, r"./output.csv"),
    ],
    input=[cb.TabularDatasetShape],
    output=[],
)

data_writer_component = Component(
    name='Data Writer component',
    implementation=data_writer_implementation,
    transformations=[],
    overriden_parameters=[
    ],
    exposed_parameters=[
    ]

)