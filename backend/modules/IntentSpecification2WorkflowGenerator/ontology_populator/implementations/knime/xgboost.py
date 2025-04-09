from common import *
from .knime_implementation import KnimeImplementation, KnimeXGBoostBundle, KnimeParameter, KnimeXGBoostFeature
from ..core import *

xgboost_linear_learner_implementation = KnimeImplementation(
    name='XGBoost Linear Learner',
    algorithm=cb.XGBoost,
    parameters=[
        KnimeParameter("Target column", XSD.string, "$$LABEL_CATEGORICAL$$", 'targetColumn',path='model/options'),
        KnimeParameter("Overlapping Penalty", XSD.string, None, 'weightColumn',path='model/options'),
        KnimeParameter("Boosting rounds", XSD.int, 100, 'boostingRounds',path='model/options'),
        KnimeParameter("Number of threads", XSD.int, 4, 'numThreads',path='model/options'),
        KnimeParameter("Manual number of threads", XSD.boolean, False, 'manualNumThreads',path='model/options'),
        KnimeParameter("Use static seed", XSD.boolean, False, 'useStaticSeed',path='model/options'),
        KnimeParameter("Static seed", XSD.int, 0, 'staticSeed', path='model/options'),
        KnimeParameter("BaseScore", XSD.double, 0.5, 'baseScore', path='model/options'),
        KnimeParameter("Objective", XSD.string, "multi:softprob", "identifier", path='model/options/objective' ),
        KnimeParameter("Filter type", XSD.string, "STANDARD", "filter-type", path='model/options/featureFilter'),
        KnimeParameter("Enforce option", XSD.string, "EnforceInclusion", "enforce_option", path='model/options/featureFilter'),
        KnimeParameter('Numeric columns', RDF.List, '$$NUMERIC_COLUMNS$$', 'included_names', path='model/options/featureFilter'),
        KnimeParameter('Other columns', XSD.string, None, '$$SKIP$$', path='model/options/featureFilter/excluded_names'),
        KnimeParameter("Lambda", XSD.double, 0.3, "lambda", path='model/booster'),
        KnimeParameter("Alpha", XSD.double, 0.3, "alpha", path='model/booster'),
        KnimeParameter("Updater", XSD.string, "CoordDescent", "updater", path='model/booster'),
        KnimeParameter("Feature selector", XSD.string, "Greedy", "featureSelector", path='model/booster'),
        KnimeParameter("Top K", XSD.int, 0, "topK", path='model/booster')
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape, (cb.NonNullTabularDatasetShape,2)],
    ],
    output=[
        cb.XGBoostModel,
    ],
    implementation_type=tb.LearnerImplementation,
    knime_node_factory='org.knime.xgboost.base.nodes.learner.classification.XGBLinearClassificationLearnerNodeFactory2',
    knime_bundle=KnimeXGBoostBundle,
    knime_feature=KnimeXGBoostFeature
)

xgboost_linear_learner_component = Component(
    name='XGBoost Linear Learner',
    implementation=xgboost_linear_learner_implementation,
    overriden_parameters=[
    ],
    exposed_parameters=[
        next((param for param in xgboost_linear_learner_implementation.parameters.keys() if param.knime_key == 'targetColumn'), None),
    ],
    transformations=[
        Transformation(
            query='''
INSERT {
    $output1 cb:setsClassColumnName "Prediction (?label)" .
}
WHERE {
    $input1 dmop:hasColumn ?column .
    ?column dmop:isLabel true ;
            dmop:hasColumnName ?label .
}
            ''',
        ),
    ],
)


xgboost_tree_learner_implementation = KnimeImplementation(
    name='XGBoost Tree Learner',
    algorithm=cb.XGBoost,
    parameters=[
        KnimeParameter("Target column", XSD.string, "$$LABEL_CATEGORICAL$$", 'targetColumn',path='model/options'),
        KnimeParameter("Overlapping Penalty", XSD.string, None, 'weightColumn',path='model/options'),
        KnimeParameter("Boosting rounds", XSD.int, 100, 'boostingRounds',path='model/options'),
        KnimeParameter("Number of threads", XSD.int, 4, 'numThreads',path='model/options'),
        KnimeParameter("Manual number of threads", XSD.boolean, False, 'manualNumThreads',path='model/options'),
        KnimeParameter("Use static seed", XSD.boolean, False, 'useStaticSeed',path='model/options'),
        KnimeParameter("Static seed", XSD.int, 0, 'staticSeed', path='model/options'),
        KnimeParameter("BaseScore", XSD.double, 0.5, 'baseScore', path='model/options'),
        KnimeParameter("Objective", XSD.string, "multi:softprob", "identifier", path='model/options/objective' ),
        KnimeParameter("Filter type", XSD.string, "STANDARD", "filter-type", path='model/options/featureFilter'),
        KnimeParameter("Enforce option", XSD.string, "EnforceInclusion", "enforce_option", path='model/options/featureFilter'),
        KnimeParameter('Numeric columns', RDF.List, '$$NUMERIC_COLUMNS$$', 'included_names', path='model/options/featureFilter'),
        KnimeParameter('Other columns', XSD.string, None, '$$SKIP$$', path='model/options/featureFilter/excluded_names'),
        KnimeParameter('Booster', XSD.string, "Tree", 'booster', path='model/booster'),
        KnimeParameter("Eta", XSD.double, 0.3, "eta", path='model/booster'),
        KnimeParameter("Gamma", XSD.double, 0.0, "gamma", path='model/booster'),
        KnimeParameter("Max Depth", XSD.int, 6, "maxDepth", path='model/booster'),
        KnimeParameter("Min child weight", XSD.double, 1.0, "minChildWeight", path='model/booster'),
        KnimeParameter("Max delta step", XSD.double, 0.0, "maxDeltaStep", path='model/booster'),
        KnimeParameter("Subsample", XSD.double, 1.0, "subsample", path='model/booster'),
        KnimeParameter("Col sample by tree", XSD.double, 1.0, "colSampleByTree", path='model/booster'),
        KnimeParameter("Col sample by level", XSD.double, 1.0, "colSampleByLevel", path='model/booster'),
        KnimeParameter("Col sample by node", XSD.double, 1.0, "colSampleByNode", path='model/booster'),
        KnimeParameter("Lambda", XSD.double, 0.3, "lambda", path='model/booster'),
        KnimeParameter("Alpha", XSD.double, 0.3, "alpha", path='model/booster'),
        KnimeParameter("Tree method", XSD.string, "Auto", "treeMethod", path='model/booster'),
        KnimeParameter("Sketch Eps", XSD.double, 0.03, "sketchEps", path='model/booster'),
        KnimeParameter("Scale Pos Weight", XSD.double, 1.0, "scalePosWeight", path='model/booster'),
        KnimeParameter("Grow policy", XSD.string, "DepthWise", "growPolicy", path='model/booster'),
        KnimeParameter("Max Leaves", XSD.int, 0, "maxLeaves", path='model/booster'),
        KnimeParameter("Max Bin", XSD.int, 256, "maxBin", path='model/booster'),
        KnimeParameter('Sample type', XSD.string, "Uniform", 'sampleType', path='model/booster'),
        KnimeParameter('Normalize type', XSD.string, "Tree", 'normalizeType', path='model/booster'),
        KnimeParameter("Rate drop", XSD.double, 0.0, "rateDrop", path='model/booster'),
        KnimeParameter("One drop", XSD.boolean, False, "oneDrop", path='model/booster'),
        KnimeParameter("Skip drop", XSD.double, 0.0, "skipDrop", path='model/booster'),
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape, (cb.NonNullTabularDatasetShape,2)],
    ],
    output=[
        cb.XGBoostModel,
    ],
    implementation_type=tb.LearnerImplementation,
    knime_node_factory='org.knime.xgboost.base.nodes.learner.classification.XGBTreeClassificationLearnerNodeFactory2',
    knime_bundle=KnimeXGBoostBundle,
    knime_feature=KnimeXGBoostFeature
)

xgboost_tree_learner_component = Component(
    name='XGBoost Tree Learner',
    implementation=xgboost_tree_learner_implementation,
    overriden_parameters=[
    ],
    exposed_parameters=[
        next((param for param in xgboost_tree_learner_implementation.parameters.keys() if param.knime_key == 'targetColumn'), None),
    ],
    transformations=[
        Transformation(
            query='''
INSERT {
    $output1 cb:setsClassColumnName "Prediction (?label)" .
}
WHERE {
    $input1 dmop:hasColumn ?column .
    ?column dmop:isLabel true ;
            dmop:hasColumnName ?label .
}
            ''',
        ),
    ],
)


xgboost_predictor_implementation = KnimeImplementation(
    name='XGBoost Predictor',
    algorithm=cb.XGBoost,
    parameters=[
        KnimeParameter("SVM Prediction column name", XSD.string, "Prediction ($$LABEL$$)", 'predictionColumnName'),
        KnimeParameter("Change prediction", XSD.boolean, False, 'changePredictionColumnName'),
        KnimeParameter("Add probabilities", XSD.boolean, False, 'appendProbabilities'),
        KnimeParameter("Class probability suffix", XSD.string, "", 'probabilitySuffix'),
        KnimeParameter("Unknown categorical as missing", XSD.boolean, False, 'unknownAsMissing'),
        KnimeParameter('Batch size', XSD.int, 10000, "batchSize")
    ],
    input=[
        cb.XGBoostModel,
        [cb.TestTabularDatasetShape, (cb.NonNullTabularDatasetShape,2)]
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart= [
        xgboost_linear_learner_implementation,
        xgboost_tree_learner_implementation,
    ],
    knime_node_factory='org.knime.xgboost.base.nodes.predictor.XGBClassificationPredictorNodeFactory',
    knime_bundle=KnimeXGBoostBundle,
    knime_feature=KnimeXGBoostFeature,
)

xgboost_predictor_component = Component(
    name='XGBoost Predictor',
    implementation=xgboost_predictor_implementation,
    transformations=[
        CopyTransformation(2, 1),
        Transformation(
            query='''
INSERT {
    $output1 dmop:hasColumn _:labelColumn .
    _:labelColumn a dmop:Column ;
        dmop:isLabel true;
      dmop:hasName $parameter1.
}
WHERE {
    $input1 cb:setsClassColumnName ?classColumnName .
}
            ''',
        ),
    ],
    counterpart=[
        xgboost_linear_learner_component,
        xgboost_tree_learner_component,
    ],
)

