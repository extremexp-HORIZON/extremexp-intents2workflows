import requests
import ollama
from openai import OpenAI
from llamaapi import LlamaAPI
from dotenv import load_dotenv
import os



def extract_label(predicted_label, labels):
    """
    Extracts the first matching label based on the predicted label.
    """
    try:
        for label in labels:
            if label in predicted_label:
                return label
        return 'unknown'
    except Exception as e:
        raise Exception(f"Error extracting label: {str(e)}")

def get_prediction_ollama(content, labels, model='phi4'):
    try:
        client = ollama.Client(host='http://<host-ip>:11434') #TODO change host-IP
        response = client.generate(model=model, prompt=content)
        prediction = response['response'].lower()
        return extract_label(prediction, labels)
    except Exception as e:
        raise Exception (f"Error requesting ollama prediction: {str(e)}")



def get_prediction(text_data, selected_model):
    """
    Classifies the provided text using the specified model and returns the predicted label.
    """
    try:
        url = f"{os.getenv('INTENTS2WORKFLOWS_URL')}/problems"  # get the labels from the ontology
        response = requests.get(url)
        labels = list(response.json().keys())

        # labels = [
        #     'data profiling', 'classification', 'correlation',
        #     'anomaly detection', 'clustering', 'causal inference',
        #     'association rules', 'regression', 'forecasting'
        # ]

        content = f"Classes: {labels}\nText: {text_data}\n\nClassify the text into one of the above classes."
        #prediction = get_prediction_ollama(content, labels, model=selected_model) #TODO enable it

        ## To integrate, we will not generate the intent prediction, we just return "Classification"
        prediction = "Classification"

        return prediction
    except Exception as e:
        print(f"Error getting prediction: {str(e)}")
        prediction = "Classification"
        return prediction
