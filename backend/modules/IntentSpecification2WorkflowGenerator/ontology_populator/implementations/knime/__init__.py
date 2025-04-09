from .partitioning import *
from .decision_tree import *
from .normalization import *
from .decision_tree import *
from .svm import *
from .missing_values import *
from .csv_io import *
from .pie_chart import *
from .bar_chart import *
from .histogram import *
from .scatter_plot import *
from .line_plot import *
from .heatmap import *
from .xgboost import *

implementations = [
    partitioning_implementation,
    decision_tree_learner_implementation,
    decision_tree_predictor_implementation,
    normalizer_implementation,
    normalizer_applier_implementation,
    svm_learner_implementation,
    svm_predictor_implementation,
    missing_value_implementation,
    missing_value_applier_implementation,
    csv_reader_implementation,
    csv_writer_implementation,
    piechart_visualizer_implementation,
    barchart_visualizer_implementation,
    histogram_visualizer_implementation,
    scatterplot_visualizer_implementation,
    lineplot_visualizer_implementation,
    heatmap_visualizer_implementation,
    xgboost_linear_learner_implementation,
    xgboost_tree_learner_implementation,
    xgboost_predictor_implementation,
]

components = [
    random_relative_train_test_split_component,
    random_absolute_train_test_split_component,
    top_relative_train_test_split_component,
    top_absolute_train_test_split_component,
    decision_tree_learner_component,
    decision_tree_predictor_component,
    min_max_scaling_component,
    z_score_scaling_component,
    decimal_scaling_component,
    normalizer_applier_component,
    polynomial_svm_learner_component,
    hypertangent_svm_learner_component,
    rbf_svm_learner_component,
    svm_predictor_component,
    drop_rows_component,
    mean_imputation_component,
    missing_value_applier_component,
    csv_reader_local_component,
    csv_writer_local_component,
    piechart_sum_visualizer_component,
    piechart_count_visualizer_component,
    piechart_avg_visualizer_component,
    barchart_sum_visualizer_component,
    barchart_count_visualizer_component,
    barchart_avg_visualizer_component,
    histogram_sum_visualizer_component,
    histogram_count_visualizer_component,
    histogram_avg_visualizer_component,
    scatterplot_visualizer_component,
    lineplot_visualizer_component,
    heatmap_visualizer_component,
    xgboost_linear_learner_component,
    xgboost_tree_learner_component,
    xgboost_predictor_component,
]
