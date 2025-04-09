from common import *
from .knime_implementation import KnimeBaseBundle, KnimeParameter, KnimeImplementation, KnimeDefaultFeature
from ..core import *

partitioning_implementation = KnimeImplementation(
    name='Data Partitioning',
    algorithm=cb.Partitioning,
    parameters=[
        KnimeParameter("Size of First Partition", XSD.string, None, "method"),
        KnimeParameter("Sampling Method", XSD.string, None, "samplingMethod"),
        KnimeParameter("Fraction (Relative size)", XSD.double, 0.8, "fraction"),
        KnimeParameter("Count (Absolute size)", XSD.int, 100, "count"),
        KnimeParameter("Random seed", XSD.string, None, "random_seed"),
        KnimeParameter("Class columns", XSD.string, None, "class_column"),
    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.TrainTabularDatasetShape,
        cb.TestTabularDatasetShape,
    ],
    knime_node_factory='org.knime.base.node.preproc.partition.PartitionNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)

implementation_parameters = partitioning_implementation.parameters

random_relative_train_test_split_component = Component(
    name='Random Relative Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Relative"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "Random")
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[2],
        list(implementation_parameters.keys())[4],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(ROUND(?rows1 * (1 - $parameter3)) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)

random_absolute_train_test_split_component = Component(
    name='Random Absolute Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Absolute"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "Random")
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[3],
        list(implementation_parameters.keys())[4],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(IF( ?rows1 - $parameter4>0, ?rows1 - $parameter4, 0 ) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)

top_relative_train_test_split_component = Component(
    name='Top K Relative Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Relative"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "First"),
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[2],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(ROUND(?rows1 * (1 - $parameter3)) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)

top_absolute_train_test_split_component = Component(
    name='Top K Absolute Train-Test Split',
    implementation=partitioning_implementation,
    overriden_parameters=[
        ParameterSpecification(list(implementation_parameters.keys())[0], "Absolute"),
        ParameterSpecification(list(implementation_parameters.keys())[1], "First"),
    ],
    exposed_parameters=[
        list(implementation_parameters.keys())[3],
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(1, 2),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
    $output2 dmop:numberOfRows ?rows1.
}
INSERT {
    $output1 dmop:numberOfRows ?newRows1 .
    $output1 dmop:isTrainDataset True .
    $output2 dmop:numberOfRows ?newRows2 .
    $output2 dmop:isTestDataset True .
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
    BIND(IF( ?rows1 - $parameter4>0, ?rows1 - $parameter4, 0 ) AS ?newRows1)
    BIND(?rows1 - ?newRows1 AS ?newRows2)
}
''',
        ),
    ],
)
