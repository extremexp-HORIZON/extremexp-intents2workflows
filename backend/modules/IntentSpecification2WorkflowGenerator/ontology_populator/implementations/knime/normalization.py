from .knime_implementation import KnimeImplementation, KnimeParameter, KnimeBaseBundle, KnimeDefaultFeature
from ..core import *
from common import *

normalizer_implementation = KnimeImplementation(
    name='Normalizer (PMML)',
    algorithm=cb.Normalization,
    parameters=[
        KnimeParameter('Normalization mode', XSD.int, None, 'mode'),
        KnimeParameter('New minimum', XSD.float, 0.0, 'newmin'),
        KnimeParameter('New maximum', XSD.float, 1.0, 'newmax'),
        KnimeParameter('Columns to normalize', RDF.List, '$$NUMERIC_COLUMNS$$', 'columns')
    ],
    input=[
        cb.TabularDataset,
    ],
    output=[
        cb.NormalizedTabularDatasetShape,
        cb.NormalizerModel,
    ],
    implementation_type=tb.LearnerImplementation,
    knime_node_factory='org.knime.base.node.preproc.pmml.normalize.NormalizerPMMLNodeFactory2',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)

min_max_scaling_component = Component(
    name='Min-Max Scaling',
    implementation=normalizer_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in normalizer_implementation.parameters.keys() if param.knime_key == 'mode'), None), 1),
    ],
    rules={
        (cb.Classification, 2):[
            {'rule': cb.NotOutlieredDatasetShape, 'weight': 2},
            {'rule': cb.NotNormalDistributionDatasetShape, 'weight': 1}
        ],
        (cb.DataVisualization, 1): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    exposed_parameters=[
        next((param for param in normalizer_implementation.parameters.keys() if param.knime_key == 'newmin'), None),
        next((param for param in normalizer_implementation.parameters.keys() if param.knime_key == 'newmax'), None),
    ],
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMinValue $parameter2;
            dmop:hasMaxValue $parameter3;
            dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output1 dmop:isNormalized true.
    $output2 cb:normalizationMode "MinMax";
             cb:newMin $parameter2;
             cb:newMax $parameter3.
}
            ''',
        ),
    ],
)

z_score_scaling_component = Component(
    name='Z-Score Scaling',
    implementation=normalizer_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in normalizer_implementation.parameters.keys() if param.knime_key == 'mode'), None), 2),
    ],
    rules={
        (cb.Classification, 3):[
            {'rule': cb.NormalDistributionDatasetShape, 'weight': 2},
            {'rule': cb.OutlieredDatasetShape, 'weight': 1}
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
    ?column ?valueProperty ?value.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMeanValue 0;
            dmop:hasStandardDeviation 1;
            dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output1 dmop:isNormalized true.
    $output2 cb:normalizationMode "ZScore".
}
            ''',
        ),
    ],
)

decimal_scaling_component = Component(
    name='Decimal Scaling',
    implementation=normalizer_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in normalizer_implementation.parameters.keys() if param.knime_key == 'mode'), None), 3),
    ],
    rules={
        (cb.Classification, 1):[
            {'rule': cb.NotNormalDistributionDatasetShape, 'weight': 1},
            {'rule': cb.OutlieredDatasetShape, 'weight': 1}
        ],
        (cb.DataVisualization, 2): [
            {'rule': cb.TabularDataset, 'weight': 1}
        ]
    },
    transformations=[
        CopyTransformation(1, 1),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output1 dmop:isNormalized true.
    $output2 cb:normalizationMode "Decimal".
}
            ''',
        ),
    ],
)

normalizer_applier_implementation = KnimeImplementation(
    name='Normalizer Apply (PMML)',
    algorithm=cb.Normalization,
    parameters=[
    ],
    input=[
        cb.NormalizerModel,
        cb.TestTabularDatasetShape,
    ],
    output=[
        cb.NormalizerModel,
        cb.NormalizedTabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=normalizer_implementation,
    knime_node_factory='org.knime.base.node.preproc.pmml.normalize.NormalizerPMMLApplyNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)

normalizer_applier_component = Component(
    name='Normalizer Applier',
    implementation=normalizer_applier_implementation,
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(2, 2),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMinValue $parameter2;
            dmop:hasMaxValue $parameter3;
            dmop:isNormalized true.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
    $input1 cb:normalizationMode "MinMax".
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMeanValue 0;
            dmop:hasStandardDeviation 1;
            dmop:isNormalized true.
}
WHERE {
    $output2 dmop:hasColumn ?column .
    ?column dmop:isFeature true .
    $input1 cb:normalizationMode "ZScore".
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:isNormalized true.
}
WHERE {
    $output1 dmop:hasColumn ?column.
    ?column dmop:isFeature true .
    $input1 cb:normalizationMode "Decimal".
}
            ''',
        ),
    ],
    counterpart=[
        min_max_scaling_component,
        z_score_scaling_component,
        decimal_scaling_component,
    ]
)


min_max_scaling_applier_component = Component(
    name='Min-Max Scaling Applier',
    implementation=normalizer_applier_implementation,
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(2, 2),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMinValue ?newMin;
            dmop:hasMaxValue ?newMax;
            dmop:isNormalized true.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    $input1 cb:minValue ?newMin;
            cb:maxValue ?newMax.
    ?column dmop:isFeature true ;
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output2 dmop:isNormalized true.
}
            ''',
        ),
    ],
    counterpart=min_max_scaling_component,
)

z_score_scaling_applier_component = Component(
    name='Z-Score Scaling Applier',
    implementation=normalizer_applier_implementation,
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(2, 2),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:hasMeanValue 0;
            dmop:hasStandardDeviation 1;
            dmop:isNormalized true.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?column dmop:isFeature true ;
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output2 dmop:isNormalized true.
}
            ''',
        ),
    ],
    counterpart=z_score_scaling_component,
)

decimal_scaling_applier_component = Component(
    name='Decimal Scaling Applier',
    implementation=normalizer_applier_implementation,
    transformations=[
        CopyTransformation(1, 1),
        CopyTransformation(2, 2),
        Transformation(
            query='''
DELETE {
    ?column ?valueProperty ?value.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?valuePropetry rdfs:subPropertyOf dmop:ColumnValueInfo.
    ?column ?valueProperty ?value.
}
            ''',
        ),
        Transformation(
            query='''
INSERT {
    ?column dmop:isNormalized true.
}
WHERE {
    $output2 dmop:hasColumn ?column.
    ?column dmop:isFeature true ;
}
            ''',
        ),
        Transformation(
            query='''
INSERT DATA {
    $output2 dmop:isNormalized true.
}
            ''',
        ),
    ],
    counterpart=decimal_scaling_component,
)

