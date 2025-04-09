import sys
import os

from rdflib.collection import Collection

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common import *
from ontology_populator.implementations.knime import implementations as implementations_k, components as components_k
from ontology_populator.implementations.simple import implementations as implementations_s, components as components_s

implementations = implementations_k + implementations_s
components = components_k + components_s


def init_cbox() -> Graph:
    cbox = get_graph_xp()

    cbox.add((URIRef(str(cb)), RDF.type, OWL.Ontology))
    cbox.add((URIRef(str(cb)), RDFS.label, Literal("ExtremeXP Ontology CBox")))

    return cbox


def add_problems(cbox):
    problems = [
        cb.Description,
        cb.Explanation,
        cb.Prediction,
        cb.DataCleaning,
        cb.DataManagement,
        cb.DataVisualization,
        cb.DataImport,
        cb.DataExport,

        cb.Classification,
        cb.Clustering,
        cb.AnomalyDetection,

        cb.MissingValueManagement,
        cb.DuplicationRemoval,
        cb.Normalization,
    ]
    subproblems = [
        (cb.Description, [cb.Classification, cb.Clustering, cb.AnomalyDetection, cb.DataVisualization],),
        (cb.DataCleaning, [cb.MissingValueManagement, cb.DuplicationRemoval, cb.Normalization],),
    ]

    for p in problems:
        cbox.add((p, RDF.type, tb.Task))

    for p, sps in subproblems:
        for sp in sps:
            cbox.add((sp, tb.subtaskOf, p))


def add_algorithms(cbox):
    algorithms = [
        # Clustering
        (cb.KMeans, cb.Clustering),
        (cb.DBSCAN, cb.Clustering),
        (cb.HierarchicalClustering, cb.Clustering),

        # Classification
        (cb.DecisionTree, cb.Classification),
        (cb.RandomForest, cb.Classification),
        (cb.NaiveBayes, cb.Classification),
        (cb.SVM, cb.Classification),
        (cb.KNN, cb.Classification),
        (cb.XGBoost, cb.Classification),
        (cb.NN, cb.Classification),

        # Anomaly Detection
        (cb.OneClassSVM, cb.AnomalyDetection),
        (cb.IsolationForest, cb.AnomalyDetection),
        (cb.LocalOutlierFactor, cb.AnomalyDetection),

        # Missing Value Management
        (cb.MeanImputation, cb.MissingValueManagement),
        (cb.MedianImputation, cb.MissingValueManagement),
        (cb.ModeImputation, cb.MissingValueManagement),
        (cb.KNNImputation, cb.MissingValueManagement),
        (cb.MissingValueRemoval, cb.MissingValueManagement),

        # Duplication Removal
        (cb.DuplicateRemoval, cb.DuplicationRemoval),

        # Normalization
        (cb.MinMaxScaling, cb.Normalization),
        (cb.ZScoreScaling, cb.Normalization),
        (cb.RobustNormalization, cb.Normalization),

        # Data Management
        (cb.Partitioning, cb.DataManagement),
        (cb.LabelExtraction, cb.DataManagement),

        # Data Visualization
        (cb.PieChart, cb.DataVisualization),
        (cb.BarChart, cb.DataVisualization),
        (cb.ScatterPlot, cb.DataVisualization),
        (cb.LinePlot, cb.DataVisualization),
        (cb.Histogram, cb.DataVisualization),
        (cb.HeatMap, cb.DataVisualization),

        # Data Import
        (cb.DataLoading, cb.DataImport),

        # Data Export
        (cb.DataStoring, cb.DataExport),
        
        
    ]

    for algorithm, problem in algorithms:
        cbox.add((algorithm, RDF.type, tb.Algorithm))
        cbox.add((algorithm, RDFS.label, Literal(algorithm.fragment)))
        cbox.add((algorithm, tb.solves, problem))


def add_implementations(cbox):
    for implementation in implementations:
        print(f'Adding implementation {implementation.name}')
        implementation.add_to_graph(cbox)

    for implementation in implementations:
         implementation.add_counterpart_relationship(cbox)

    for component in components:
        print(f'Adding component {component.name}')
        component.add_to_graph(cbox)

    for component in components:
        component.add_counterpart_relationship(cbox)


def add_models(cbox):
    models = [
        'SVMModel',
        'DecisionTreeModel',
        'NormalizerModel',
        'MissingValueModel',
        'XGBoostModel',
        'NNModel'
    ]

    cbox.add((cb.Model, RDFS.subClassOf, tb.Data))
    for model in models:
        cbox.add((cb.term(model), RDFS.subClassOf, cb.Model))

        cbox.add((cb.term(model + 'Shape'), RDF.type, SH.NodeShape))
        cbox.add((cb.term(model + 'Shape'), RDF.type, tb.DataSpec))
        cbox.add((cb.term(model + 'Shape'), SH.targetClass, cb.term(model)))


def add_visualizations(cbox):
    visualizations = [
        'PieChartVisualization',
        'BarChartVisualization',
        'ScatterPlotVisualization',
        'LinePlotVisualization',
        'HistogramVisualization',
        'HeatMapVisualization',
        
    ]

    cbox.add((cb.Visualization, RDFS.subClassOf, tb.Data))
    for visual in visualizations:
        cbox.add((cb.term(visual), RDFS.subClassOf, cb.Visualization))

        cbox.add((cb.term(visual + 'Shape'), RDF.type, SH.NodeShape))
        cbox.add((cb.term(visual + 'Shape'), RDF.type, tb.DataSpec))
        cbox.add((cb.term(visual + 'Shape'), SH.targetClass, cb.term(visual)))


# def add_datasets(cbox):
#     cbox.add((dmop.TabularDataset, RDFS.subClassOf, tb.Data))

#     cbox.add((cb.term('TabularDatasetShape'), RDF.type, SH.NodeShape))
#     cbox.add((cb.term('TabularDatasetShape'), RDF.type, tb.DataSpec))
#     cbox.add((cb.term('TabularDatasetShape'), SH.targetClass, dmop.TabularDataset))


def add_subproperties(cbox):
    subproperties = [
        # Column
        (dmop.hasColumnName, dmop.ColumnInfoProperty),
        (dmop.hasDataPrimitiveTypeColumn, dmop.ColumnInfoProperty),
        (dmop.hasPosition, dmop.ColumnInfoProperty),
        (dmop.isCategorical, dmop.ColumnInfoProperty),
        (dmop.isFeature, dmop.ColumnInfoProperty),
        (dmop.isLabel, dmop.ColumnInfoProperty),
        (dmop.isUnique, dmop.ColumnInfoProperty),
        (dmop.containsNulls, dmop.ColumnValueInfoProperty),
        (dmop.hasMeanValue, dmop.ColumnValueInfoProperty),
        (dmop.hasStandardDeviation, dmop.ColumnValueInfoProperty),
        (dmop.hasMaxValue, dmop.ColumnValueInfoProperty),
        (dmop.hasMinValue, dmop.ColumnValueInfoProperty),

        # Dataset
        (dmop.delimiter, dmop.DatasetPhysicalProperty),
        (dmop.doubleQuote, dmop.DatasetPhysicalProperty),
        (dmop.encoding, dmop.DatasetPhysicalProperty),
        (dmop.fileFormat, dmop.DatasetPhysicalProperty),
        (dmop.hasHeader, dmop.DatasetPhysicalProperty),
        (dmop.isNormalized, dmop.DatasetValueInfoProperty),
        (dmop.lineDelimiter, dmop.DatasetPhysicalProperty),
        (dmop.numberOfColumns, dmop.DatasetInfoProperty),
        (dmop.numberOfRows, dmop.DatasetInfoProperty),
        (dmop.path, dmop.DatasetPhysicalProperty),
        (dmop.quoteChar, dmop.DatasetPhysicalProperty),
        (dmop.skipInitialSpace, dmop.DatasetPhysicalProperty),
        (dmop.isTrainDataset, dmop.DatasetInfoProperty),
        (dmop.isTestDataset, dmop.DatasetInfoProperty)
    ]

    for s, o in subproperties:
        cbox.add((s, RDFS.subPropertyOf, o))


def add_shapes(cbox):
    # NonNullNumericFeatureColumnShape
    column_shape = cb.NonNullNumericFeatureColumnShape
    # column_shape = BNode()
    cbox.add((column_shape, RDF.type, SH.NodeShape))

    numeric_column_property = cb.NumericColumnProperty
    # numeric_column_property = BNode()
    cbox.add((numeric_column_property, SH.path, dmop.hasDataPrimitiveTypeColumn))
    cbox.add((numeric_column_property, SH['in'],
              Collection(cbox, BNode(), seq=[dmop.Integer, dmop.Float]).uri))

    non_null_column_property = cb.NonNullColumnProperty
    # non_null_column_property = BNode()
    cbox.add((non_null_column_property, SH.path, dmop.containsNulls))
    cbox.add((non_null_column_property, SH.datatype, XSD.boolean))
    cbox.add((non_null_column_property, SH.hasValue, Literal(False)))

    feature_column_property = cb.FeatureColumnProperty
    # feature_column_property = BNode()
    cbox.add((feature_column_property, SH.path, dmop.isFeature))
    cbox.add((feature_column_property, SH.datatype, XSD.boolean))
    cbox.add((feature_column_property, SH.hasValue, Literal(True)))

    feature_column = cb.FeatureColumnShape
    # feature_column = BNode()
    cbox.add((feature_column, RDF.type, SH.NodeShape))
    cbox.add((feature_column, SH.targetClass, dmop.Column))
    cbox.add((feature_column, SH.property, feature_column_property))

    cbox.add((column_shape, SH.property, numeric_column_property))
    cbox.add((column_shape, SH.property, non_null_column_property))
    cbox.add((column_shape, SH.targetClass, feature_column))

    # NonNullNumericFeatureTabularDatasetShape
    non_null_numeric_tabular_dataset_shape = cb.NonNullNumericFeatureTabularDatasetShape
    cbox.add((non_null_numeric_tabular_dataset_shape, RDF.type, SH.NodeShape))
    cbox.add((non_null_numeric_tabular_dataset_shape, SH.targetClass, dmop.TabularDataset))

    bnode = BNode()
    cbox.add((bnode, SH.path, dmop.hasColumn))
    cbox.add((bnode, SH.node, column_shape))

    cbox.add((non_null_numeric_tabular_dataset_shape, SH.property, bnode))

    # LabeledTabularDatasetShape

    label_column_property = cb.LabelColumnProperty
    cbox.add((label_column_property, SH.path, dmop.isLabel))
    cbox.add((label_column_property, SH.datatype, XSD.boolean))
    cbox.add((label_column_property, SH.hasValue, Literal(True)))

    label_column_shape = cb.LabelColumnShape
    cbox.add((label_column_shape, RDF.type, SH.NodeShape))
    cbox.add((label_column_shape, SH.targetClass, dmop.Column))
    cbox.add((label_column_shape, SH.property, label_column_property))

    labeled_dataset_shape = cb.LabeledTabularDatasetShape
    cbox.add((labeled_dataset_shape, RDF.type, SH.NodeShape))
    cbox.add((labeled_dataset_shape, SH.targetClass, dmop.TabularDataset))

    bnode_qualified = BNode()
    cbox.add((bnode_qualified, SH.path, dmop.isLabel))
    cbox.add((bnode_qualified, SH.hasValue, Literal(True)))

    bnode_column = BNode()
    cbox.add((bnode_column, SH.path, dmop.hasColumn))
    cbox.add((bnode_column, SH.qualifiedValueShape, bnode_qualified))
    cbox.add((bnode_column, SH.qualifiedMinCount, Literal(1)))
    cbox.add((bnode_column, SH.minCount, Literal(1)))

    cbox.add((labeled_dataset_shape, SH.property, bnode_column))

    non_null_column_shape = cb.NonNullColumnShape
    cbox.add((non_null_column_shape, RDF.type, SH.NodeShape))
    cbox.add((non_null_column_shape, SH.targetClass, dmop.Column))
    cbox.add((non_null_column_shape, SH.property, non_null_column_property))

    bnode = BNode()
    cbox.add((bnode, SH.path, dmop.hasColumn))
    cbox.add((bnode, SH.node, non_null_column_shape))

    non_null_tabular_dataset_shape = cb.NonNullTabularDatasetShape
    cbox.add((non_null_tabular_dataset_shape, RDF.type, SH.NodeShape))
    cbox.add((non_null_tabular_dataset_shape, SH.targetClass, dmop.TabularDataset))
    cbox.add((non_null_tabular_dataset_shape, SH.property, bnode))

    cbox.add((cb.TabularDataset, RDF.type, SH.NodeShape))
    cbox.add((cb.TabularDataset, RDF.type, tb.DataTag))
    cbox.add((cb.TabularDataset, SH.targetClass, dmop.TabularDataset))

    numeric_column_shape = cb.NumericColumnShape
    cbox.add((numeric_column_shape, RDF.type, SH.NodeShape))
    cbox.add((numeric_column_shape, SH.targetClass, dmop.Column))
    cbox.add((numeric_column_shape, SH.property, numeric_column_property))

    bnode = BNode()
    cbox.add((bnode, SH.path, dmop.hasColumn))
    cbox.add((bnode, SH.node, numeric_column_shape))

    numeric_tabular_dataset_shape = cb.NumericTabularDatasetShape
    cbox.add((numeric_tabular_dataset_shape, RDF.type, SH.NodeShape))
    cbox.add((numeric_tabular_dataset_shape, SH.targetClass, dmop.TabularDataset))
    cbox.add((numeric_tabular_dataset_shape, SH.property, bnode))

    # NormalizedTabularDatasetShape 
    cbox.add((cb.isNormalizedConstraint, RDF.type, SH.PropertyConstraintComponent))
    cbox.add((cb.isNormalizedConstraint, SH.path, dmop.isNormalized))
    cbox.add((cb.isNormalizedConstraint, SH.datatype, XSD.boolean))
    cbox.add((cb.isNormalizedConstraint, SH.hasValue, Literal(True)))

    cbox.add((cb.NormalizedTabularDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.NormalizedTabularDatasetShape, RDF.type, tb.DataTag))
    cbox.add((cb.NormalizedTabularDatasetShape, SH.property, cb.isNormalizedConstraint))
    cbox.add((cb.NormalizedTabularDatasetShape, SH.targetClass, dmop.TabularDataset))

    # TrainTabularDatasetShape
    cbox.add((cb.isTrainConstraint, RDF.type, SH.PropertyConstraintComponent))
    cbox.add((cb.isTrainConstraint, SH.path, dmop.isTrainDataset))
    cbox.add((cb.isTrainConstraint, SH.datatype, XSD.boolean))
    cbox.add((cb.isTrainConstraint, SH.hasValue, Literal(True)))

    cbox.add((cb.TrainTabularDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.TrainTabularDatasetShape, RDF.type, tb.DataTag))
    cbox.add((cb.TrainTabularDatasetShape, SH.property, cb.isTrainConstraint))
    cbox.add((cb.TrainTabularDatasetShape, SH.targetClass, dmop.TabularDataset))

    # TestTabularDatasetShape
    cbox.add((cb.isTestConstraint, RDF.type, SH.PropertyConstraintComponent))
    cbox.add((cb.isTestConstraint, SH.path, dmop.isTestDataset))
    cbox.add((cb.isTestConstraint, SH.datatype, XSD.boolean))
    cbox.add((cb.isTestConstraint, SH.hasValue, Literal(True)))

    cbox.add((cb.TestTabularDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.TestTabularDatasetShape, RDF.type, tb.DataTag))
    cbox.add((cb.TestTabularDatasetShape, SH.property, cb.isTestConstraint))
    cbox.add((cb.TestTabularDatasetShape, SH.targetClass, dmop.TabularDataset))


    ####################################################################################################################

    # NormalDistributionDatasetShape
    cbox.add((cb.isNormalDistributionConstraint, RDF.type, SH.PropertyConstraintComponent))
    cbox.add((cb.isNormalDistributionConstraint, SH.path, dmop.isNormallyDistributed))
    cbox.add((cb.isNormalDistributionConstraint, SH.datatype, XSD.boolean))  
    cbox.add((cb.isNormalDistributionConstraint, SH.hasValue, Literal(True)))  

    cbox.add((cb.NormalDistributionDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.NormalDistributionDatasetShape, RDF.type, tb.DataTag))
    cbox.add((cb.NormalDistributionDatasetShape, SH.property, cb.isNormalDistributionConstraint))
    cbox.add((cb.NormalDistributionDatasetShape, SH.targetClass, dmop.TabularDataset))


    # NotNormalDistributionDatasetShape
    cbox.add((cb.isNotNormalDistributionConstraint, RDF.type, SH.PropertyConstraintComponent))
    cbox.add((cb.isNotNormalDistributionConstraint, SH.path, dmop.isNormallyDistributed))
    cbox.add((cb.isNotNormalDistributionConstraint, SH.maxCount, Literal(0))) 

    cbox.add((cb.NotNormalDistributionDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.NotNormalDistributionDatasetShape, RDF.type, tb.DataTag))
    cbox.add((cb.NotNormalDistributionDatasetShape, SH.property, cb.isNotNormalDistributionConstraint))
    cbox.add((cb.NotNormalDistributionDatasetShape, SH.targetClass, dmop.TabularDataset))


    # OutlieredDatasetShape
    cbox.add((cb.hasOutliersConstraint, RDF.type, SH.PropertyConstraintComponent))
    cbox.add((cb.hasOutliersConstraint, SH.path, dmop.containsOutliers))
    cbox.add((cb.hasOutliersConstraint, SH.datatype, XSD.boolean))  
    cbox.add((cb.hasOutliersConstraint, SH.hasValue, Literal(True)))

    cbox.add((cb.OutlieredDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.OutlieredDatasetShape, RDF.type, tb.DataTag))
    cbox.add((cb.OutlieredDatasetShape, SH.property, cb.hasOutliersConstraint))
    cbox.add((cb.OutlieredDatasetShape, SH.targetClass, dmop.TabularDataset))

    
    # NotOutlieredDatasetShape
    cbox.add((cb.hasNoOutliersConstraint, RDF.type, SH.PropertyConstraintComponent))
    cbox.add((cb.hasNoOutliersConstraint, SH.path, dmop.containsOutliers))
    cbox.add((cb.hasNoOutliersConstraint, SH.datatype, XSD.boolean))  
    cbox.add((cb.hasNoOutliersConstraint, SH.hasValue, Literal(False)))

    cbox.add((cb.NotOutlieredDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.NotOutlieredDatasetShape, RDF.type, tb.DataTag))
    cbox.add((cb.NotOutlieredDatasetShape, SH.property, cb.hasNoOutliersConstraint))
    cbox.add((cb.NotOutlieredDatasetShape, SH.targetClass, dmop.TabularDataset))


    # IntegerTabularDatasetShape
    cbox.add((cb.integerTypeConstraint, RDF.type, SH.PropertyShape))
    cbox.add((cb.integerTypeConstraint, SH.path, dmop.hasDataPrimitiveTypeColumn))
    cbox.add((cb.integerTypeConstraint, SH.hasValue, dmop.Integer))

    cbox.add((cb.floatTypeConstraint, RDF.type, SH.PropertyShape))
    cbox.add((cb.floatTypeConstraint, SH.path, dmop.hasDataPrimitiveTypeColumn))
    cbox.add((cb.floatTypeConstraint, SH.hasValue, dmop.Float))

    cbox.add((cb.hasIntegerColumn, RDF.type, SH.PropertyShape))
    cbox.add((cb.hasIntegerColumn, SH.path, dmop.hasColumn))
    cbox.add((cb.hasIntegerColumn, SH.qualifiedValueShape, cb.integerTypeConstraint))
    cbox.add((cb.hasIntegerColumn, SH.qualifiedMinCount, Literal(1)))

    cbox.add((cb.hasFloatColumn, RDF.type, SH.PropertyShape))
    cbox.add((cb.hasFloatColumn, SH.path, dmop.hasColumn))
    cbox.add((cb.hasFloatColumn, SH.qualifiedValueShape, cb.floatTypeConstraint))
    cbox.add((cb.hasFloatColumn, SH.qualifiedMaxCount, Literal(0)))

    cbox.add((cb.IntegerTabularDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.IntegerTabularDatasetShape, SH.property, cb.hasIntegerColumn))
    cbox.add((cb.IntegerTabularDatasetShape, SH.property, cb.hasFloatColumn))
    cbox.add((cb.IntegerTabularDatasetShape, SH.targetClass, dmop.TabularDataset))

    # FloatTabularDatasetShape
    cbox.add((cb.integerTypeConstraint, RDF.type, SH.PropertyShape))
    cbox.add((cb.integerTypeConstraint, SH.path, dmop.hasDataPrimitiveTypeColumn))
    cbox.add((cb.integerTypeConstraint, SH.hasValue, dmop.Integer))

    cbox.add((cb.floatTypeConstraint, RDF.type, SH.PropertyShape))
    cbox.add((cb.floatTypeConstraint, SH.path, dmop.hasDataPrimitiveTypeColumn))
    cbox.add((cb.floatTypeConstraint, SH.hasValue, dmop.Float))

    cbox.add((cb.hasIntegerColumn, RDF.type, SH.PropertyShape))
    cbox.add((cb.hasIntegerColumn, SH.path, dmop.hasColumn))
    cbox.add((cb.hasIntegerColumn, SH.qualifiedValueShape, cb.integerTypeConstraint))
    cbox.add((cb.hasIntegerColumn, SH.qualifiedMaxCount, Literal(0)))

    cbox.add((cb.hasFloatColumn, RDF.type, SH.PropertyShape))
    cbox.add((cb.hasFloatColumn, SH.path, dmop.hasColumn))
    cbox.add((cb.hasFloatColumn, SH.qualifiedValueShape, cb.floatTypeConstraint))
    cbox.add((cb.hasFloatColumn, SH.qualifiedMinCount, Literal(1)))

    cbox.add((cb.FloatTabularDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.FloatTabularDatasetShape, SH.property, cb.hasIntegerColumn))
    cbox.add((cb.FloatTabularDatasetShape, SH.property, cb.hasFloatColumn))
    cbox.add((cb.FloatTabularDatasetShape, SH.targetClass, dmop.TabularDataset))

    # LowPercentageMVDatasetShape
    cbox.add((cb.missingValueConstraint, RDF.type, SH.PropertyShape))
    cbox.add((cb.missingValueConstraint, SH.path, dmop.missingvaluesPercentage))
    cbox.add((cb.missingValueConstraint, SH.maxInclusive, Literal(0.05)))
    cbox.add((cb.missingValueConstraint, SH.maxCount, Literal(1)))

    cbox.add((cb.LowMVTabularDatasetShape, RDF.type, SH.NodeShape))
    cbox.add((cb.LowMVTabularDatasetShape, SH.property, cb.missingValueConstraint))
    cbox.add((cb.LowMVTabularDatasetShape, SH.targetClass, dmop.TabularDataset))    




def main(dest='../ontologies/cbox.ttl'):
    cbox = init_cbox()
    add_problems(cbox)
    add_algorithms(cbox)
    add_implementations(cbox)
    add_models(cbox)
    add_visualizations(cbox)
    # add_datasets(cbox)
    add_subproperties(cbox)
    add_shapes(cbox)

    cbox.serialize(dest, format='turtle')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
