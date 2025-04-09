from common import *
from ..core import *

nn_learner_implementation = Implementation(
    name='NN Learner',
    algorithm=cb.NN,
    parameters=[
        Parameter("Class column", XSD.string, "$$LABEL$$"),
        Parameter("NN type", XSD.string, None),
    ],
    input=[
        [cb.LabeledTabularDatasetShape, cb.TrainTabularDatasetShape, cb.NormalizedTabularDatasetShape, cb.NonNullTabularDatasetShape],
    ],
    output=[
        cb.NNModel,
    ],
    implementation_type=tb.LearnerImplementation,
)

feedforward_learner_component = Component(
    name='FeedForward NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
         ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'FeedForward'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'Class column'),None)
    ],
    transformations=[
    ],
)

recurrent_learner_component = Component(
    name='Recurrent NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'Recurrent'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'Class column'),None)
    ],
    transformations=[
    ],
)

convolutional_learner_component = Component(
    name='Convolutional NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'Convolutional'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'Class column'),None)
    ],
    transformations=[
    ],
)

lstm_learner_component = Component(
    name='LSTM NN Learner',
    implementation=nn_learner_implementation,
    overriden_parameters=[
        ParameterSpecification(next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'NN type'), None), 'LSTM'),
    ],
    exposed_parameters=[
        next((param for param in nn_learner_implementation.parameters.keys() if param.label == 'Class column'),None)
    ],
    transformations=[
    ],
)

nn_predictor_implementation = Implementation(
    name='NN Predictor',
    algorithm=cb.NN,
    parameters=[
        Parameter("Prediction column name", XSD.string, "Prediction ($$LABEL$$)", 'prediction column name'),
        Parameter("Change prediction", XSD.boolean, False, 'change prediction'),
        Parameter("Add probabilities", XSD.boolean, False, 'add probabilities'),
        Parameter("Class probability suffix", XSD.string, "", 'class probability suffix'),
    ],
    input=[
        cb.NNModel,
        [cb.TestTabularDatasetShape,cb.NormalizedTabularDatasetShape, cb.NonNullTabularDatasetShape]
    ],
    output=[
        cb.TabularDatasetShape,
    ],
    implementation_type=tb.ApplierImplementation,
    counterpart=nn_learner_implementation,
)

nn_predictor_component = Component(
    name='NN Predictor',
    implementation=nn_predictor_implementation,
    transformations=[

    ],
    counterpart=[
        feedforward_learner_component,
        recurrent_learner_component,
        convolutional_learner_component,
        lstm_learner_component
    ],
)
