from flask import Flask, request
from langchain_google_genai import GoogleGenerativeAI
from lunary import LunaryCallbackHandler, agent
import requests
import os
import csv
import whylogs as why
from langkit import llm_metrics
import pandas as pd

"""
Required APIs: lakera, lunary, gemini, langkit

"""


request_log = '/home/ubuntu/Desktop/app/request_log.csv'
response_log = '/home/ubuntu/Desktop/app/response_log.csv'


def check_for_policy_violation(message, user, log_file) :

    session = requests.Session()  

    result = (session.post(
    "https://api.lakera.ai/v2/guard",
    json={"messages": [{"content": message, "role": "user"}]},
    headers={"Authorization": "Bearer "+ os.environ['LAKERA_API_KEY']},
    )).json()
    
    violation = result["flagged"]

    if violation :

        results = session.post(
        "https://api.lakera.ai/v2/guard/results",
        json={"messages": [{"content": message, "role": "user"}]},
        headers={"Authorization": "Bearer "+ os.environ['LAKERA_API_KEY']}).json()

        with open(log_file, 'a') as log:

            writer = csv.writer(log)
            writer.writerow((user, results))
        
        
    return violation


@agent()
def execute_and_track_prompt(prompt):

    handler = LunaryCallbackHandler()       #by default using lunary_public_key in environment variables
    
    model = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.environ["GOOGLE_API_KEY"], callbacks=[handler])

    response = model.invoke(prompt)

    return response



def evaluate_with_langkit(prompt, response) :

    item = pd.DataFrame({"prompt":[prompt], "response":[response]})
    results = why.log(item, schema=llm_metrics.init())
    
    results.writer("whylabs").write()
            

          

app = Flask(__name__)

@app.post('/request')
def execute_prompt() :

    user = request.get_json()['user']
    prompt = request.get_json()['request']
    

    if check_for_policy_violation(prompt, user, request_log) :

        return {'response' : 'The request will not be carried out as it violated policy regulations'}

    else :

        response = execute_and_track_prompt(prompt)

        if check_for_policy_violation(prompt, user, response_log) :

            return {'response' : 'The request will not be carried out as it violated policy regulations'}

        upload_into_langkit(prompt, response)

        return {'response' : response}



if __name__ == '__main__' :
    app.run(debug=True)
