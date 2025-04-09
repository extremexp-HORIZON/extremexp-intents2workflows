from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.query_graphdb import  get_all_metrics, get_all_algorithms, \
    get_all_preprocessing_algorithms
from utils.recommendations import *

app = Flask(__name__)
CORS(app)

# Dictionary route information
routes_info = {
    "/add_workflow": {
    "parameters": ["data"],
    "description": "Adds a new workflow to the GraphDB repository using the provided data.",
    "response": {
        "workflow_name": "string"
    },
    "example_usage": "curl -X POST http://localhost:8002/add_workflow -H \"Content-Type: application/json\" -d '{\"data\": {\"user\": \"example_user\", \"dataset\": \"dataset_name\", \"intent\": \"intent_class\", \"algorithm_constraint\": \"ExampleAlgorithm\", \"hyperparam_constraints\": {\"param1\": \"value1\", \"param2\": \"value2\"}, \"time\":  \"time_value\", \"preprocessor_constraint\": \"ExamplePreprocessor\", \"max_time\": \"max_time_value\", \"pipeline\": {\"preprocs\": [\"ExamplePreprocessor()\"], \"learner\": \"ExampleLearner()\"}, \"metricName\": \"example_metric\", \"metric_value\": \"example metric_value\"}}'"
}

}

@app.route('/', methods=['GET'])
def base_route():
    return jsonify(routes_info), 200

@app.route('/get_recommendations', methods=['GET'])
def get_recommendations_route():
    user = request.args.get('user')
    dataset = request.args.get('dataset')
    intent = request.args.get('intent')
    if not user or not dataset or not intent:
        return jsonify({"error": "Missing user, dataset, or intent parameter"}), 400

    try:
        print('Start')
        experiment = annotate_tsv(user,intent,dataset)
        print('Middle')
        results = recommendations(experiment,user,intent,dataset)
        print('End')
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500   


@app.route('/get_all_info', methods=['GET'])
def get_all_info_route():
    metrics = get_all_metrics()
    algorithms = get_all_algorithms()
    preprocessing_algorithms = get_all_preprocessing_algorithms()
    return jsonify({
        "metrics": metrics,
        "algorithms": algorithms,
        "preprocessing_algorithms": preprocessing_algorithms,
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=8002)
