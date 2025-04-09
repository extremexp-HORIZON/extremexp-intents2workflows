from .knime_implementation import KnimeImplementation, KnimeParameter, KnimeBaseBundle, KnimeDefaultFeature
from ..core import *
from common import *

missing_value_implementation = KnimeImplementation(
    name='Missing Value',
    algorithm=cb.MissingValueRemoval,
    parameters=[
        KnimeParameter('Integer', XSD.string, None, 'factoryID',
                       path='model/dataTypeSettings/org.knime.core.data.def.IntCell', condition='$$INTEGER_COLUMN$$'),
        KnimeParameter('String', XSD.string, None, 'factoryID',
                       path='model/dataTypeSettings/org.knime.core.data.def.StringCell', condition='$$STRING_COLUMN$$'),
        KnimeParameter('Float', XSD.string, None, 'factoryID',
                       path='model/dataTypeSettings/org.knime.core.data.def.DoubleCell', condition='$$FLOAT_COLUMN$$'),

        KnimeParameter('Integer settings', XSD.string, None, '$$SKIP$$',
                       path='model/dataTypeSettings/org.knime.core.data.def.IntCell/settings',
                       condition='$$INTEGER_COLUMN$$'),
        KnimeParameter('String settings', XSD.string, None, '$$SKIP$$',
                       path='model/dataTypeSettings/org.knime.core.data.def.StringCell/settings',
                       condition='$$STRING_COLUMN$$'),
        KnimeParameter('Float settings', XSD.string, None, '$$SKIP$$',
                       path='model/dataTypeSettings/org.knime.core.data.def.DoubleCell/settings',
                       condition='$$FLOAT_COLUMN$$'),

        KnimeParameter('Column settings', XSD.string, None, '$$SKIP$$', path='model/columnSettings'),

    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.NonNullTabularDatasetShape,
        cb.MissingValueModel,
    ],
    implementation_type=tb.LearnerImplementation,
    knime_node_factory='org.knime.base.node.preproc.pmml.missingval.compute.MissingValueHandlerNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
)

mean_imputation_component = Component(
    name='Mean Imputation',
    implementation=missing_value_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.knime_key == 'factoryID' and param.label == 'Integer'), None),
                               'org.knime.base.node.preproc.pmml.missingval.handlers.DoubleMeanMissingCellHandlerFactory'),
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.knime_key == 'factoryID' and param.label == 'Float'), None),
                               'org.knime.base.node.preproc.pmml.missingval.handlers.DoubleMeanMissingCellHandlerFactory'),
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.knime_key == 'factoryID' and param.label == 'String'), None),
                               'org.knime.base.node.preproc.pmml.missingval.handlers.MostFrequentValueMissingCellHandlerFactory'),
    ],
    exposed_parameters=[],
    rules={
        (cb.Classification, 2):[
            {'rule': cb.TabularDataset, 'weight': 1}
        ],
        (cb.DataVisualization, 1): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column dmop:containsNulls false.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:containsNulls true.
}
'''),
    ],
)

drop_rows_component = Component(
    name='Drop Rows with Missing Values',
    implementation=missing_value_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.knime_key == 'factoryID' and param.label == 'Integer'), None),
                               'org.knime.base.node.preproc.pmml.missingval.pmml.RemoveRowMissingCellHandlerFactory'),
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.knime_key == 'factoryID' and param.label == 'Float'), None),
                               'org.knime.base.node.preproc.pmml.missingval.pmml.RemoveRowMissingCellHandlerFactory'),
        ParameterSpecification(next((param for param in missing_value_implementation.parameters.keys()
                                     if param.knime_key == 'factoryID' and param.label == 'String'), None),
                               'org.knime.base.node.preproc.pmml.missingval.pmml.RemoveRowMissingCellHandlerFactory'),
    ],
    exposed_parameters=[],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.LowMVTabularDatasetShape, 'weight': 2}
        ],
        (cb.DataVisualization, 1): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column dmop:containsNulls false.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:containsNulls true.
}
'''),
        Transformation(
            query='''
DELETE {
    $output1 dmop:numberOfRows ?rows1.
}
WHERE {
    $output1 dmop:numberOfRows ?rows1.
}
''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output2 cb:removesProperty dmop:numberOfRows.
}
''',
        ),
    ],
)

missing_value_applier_implementation = KnimeImplementation(
    name='Missing Value (Applier)',
    algorithm=cb.MissingValueRemoval,
    parameters=[
    ],
    input=[
        cb.MissingValueModel,
        cb.TestTabularDatasetShape,
    ],
    output=[
        cb.NonNullTabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    knime_node_factory='org.knime.base.node.preproc.pmml.missingval.apply.MissingValueApplyNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)

missing_value_applier_component = Component(
    name='Missing Value Management Applier',
    implementation=missing_value_applier_implementation,
    overriden_parameters=[],
    exposed_parameters=[],
    transformations=[
        CopyTransformation(2, 1),
        Transformation(
            query='''
DELETE {
    $output2 ?property ?value.
}
WHERE {
    $output1 cb:removesProperty ?property.
    $output2 ?property ?value.
}
''',
        ),
    ],
    counterpart=[
        mean_imputation_component,
        drop_rows_component,
    ]
)
