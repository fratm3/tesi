import requests
from time import perf_counter
import string
import random

file_path = "prompts.txt"

def id_generator():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))




if __name__ == "__main__" :

    prompts = None

    with open(file_path, 'r') as prompt_file:
        prompts = prompt_file.readlines()

    for prompt in prompts :

        request = {
            'request'   : '"'+prompt.strip()+'"',
            'user'      : id_generator()
        }

        #response = (requests.post("http://127.0.0.1:5000/request", json=request)).json()
        #output = response['response']

       t0 = perf_counter()

        response = (requests.post("http://127.0.0.1:5000/request", json=request)).json()
        output = response['response']

        dt = perf_counter()

        latency = dt - t0

        print(output)

        print("latency: " + str(latency))
