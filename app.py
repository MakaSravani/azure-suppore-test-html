


# from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS
# import openai
# import os
# import requests
# import re

# app = Flask(__name__)
# CORS(app)
# # app.static_folder = 'static'
# from collections.abc import Sequence
# # from flask import Flask
# def is_it_a_sequence(obj):
#     return isinstance(obj, Sequence)
# print(is_it_a_sequence([1, 2, 3])) # True
# print(is_it_a_sequence('abc')) # True

# openai.api_type = "azure"
# openai.api_version = "2023-08-01-preview"
# openai.api_base = "https://cog-cdzj2obpa54em.openai.azure.com/"
# openai.api_key = "825a0d3880054857a94fd70649196ad3"
# deployment_id = "chat"

# search_endpoint = "https://gptkb-cdzj2obpa54em.search.windows.net"
# search_key = "VmM0fMtVNqbwZKbomZrZgRKnadwl12Qc3KXxMsXIzIAzSeBAgDyI"
# search_index_name = "escogidxtest"


# def setup_byod(deployment_id: str) -> None:
#     class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):

#         def send(self, request, **kwargs):
#             request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
#             return super().send(request, **kwargs)

#     session = requests.Session()
#     session.mount(
#         prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
#         adapter=BringYourOwnDataAdapter()
#     )
#     openai.requestssession = session


# def generate_message_text(conversation_history, user_question):
#     messages = [{"role": "user", "content": user_question}]

#     for entry in conversation_history:
#         messages.append({"role": "assistant", "content": entry["assistant_response"]})

#     return messages

# def clean_up_response(assistant_response):
#     # Replace [docX] with an empty string
#     cleaned_response = re.sub(r'\[doc\d+\]', '', assistant_response)
#     return cleaned_response
# @app.route("/", methods=["POST"])
# def index():
#     conversation_history = []
#     user_question = request.json.get("user_question")

#     if conversation_history:
#         last_assistant_response = conversation_history[-1]["assistant_response"]
#         message_text = generate_message_text(conversation_history, user_question)
#         message_text.append({"role": "assistant", "content": last_assistant_response})
#     else:
#         message_text = generate_message_text(conversation_history, user_question)

#     completion = openai.ChatCompletion.create(
   
#     deployment_id=deployment_id,  # Specify the model name here
#     messages=message_text,
#     dataSources=[  # Use completions_extensions instead of dataSources
#         {
#             "type": "AzureCognitiveSearch",
#             "parameters": {
#                 "endpoint": search_endpoint,
#                 "key": search_key,
#                 "indexName": search_index_name,
#             }
#         }
#     ],
#     max_tokens=13590,
#     temperature=0.3
# )

#     assistant_response = completion['choices'][0]['message']['content']
#     cleaned_response = clean_up_response(assistant_response)
#     conversation_history.append({"user_question": user_question, "assistant_response": cleaned_response})

#     return jsonify({"user_question": user_question, "assistant_response": cleaned_response})


# if __name__ == "__main__":
#     setup_byod(deployment_id)
#     app.run(debug=True,port=8000)

from flask import  Flask, render_template, request, redirect, url_for
import openai
import os
import requests
from dotenv import load_dotenv

app = Flask(__name__)
app.static_folder = 'static'

openai.api_type = "azure"
openai.api_version = "2023-08-01-preview"
openai.api_base = "https://cog-cdzj2obpa54em.openai.azure.com/"
openai.api_key = "825a0d3880054857a94fd70649196ad3"
deployment_id = "chat"

search_endpoint = "https://gptkb-cdzj2obpa54em.search.windows.net"
search_key = "VmM0fMtVNqbwZKbomZrZgRKnadwl12Qc3KXxMsXIzIAzSeBAgDyI"
search_index_name = "escogidxtest"

def setup_byod(deployment_id: str) -> None:
    class BringYourOwnDataAdapter(requests.adapters.HTTPAdapter):

        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()
    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=BringYourOwnDataAdapter()
    )
    openai.requestssession = session



# Update the generate_message_text function
def generate_message_text(user_question: str, assistant_response: str):
    messages = []

    if assistant_response:
        messages.append({"role": "user", "content": user_question})
        messages.append({"role": "assistant", "content": assistant_response})
    else:
        messages.append({"role": "user", "content": user_question})

    return messages



conversation_history = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_question = request.form["user_question"]

        if conversation_history:
            # Use the last assistant response as context for the next user question
            last_assistant_response = conversation_history[-1]["assistant_response"]
            message_text = generate_message_text(user_question, last_assistant_response)
        else:
            message_text = generate_message_text(user_question, "")

        completion = openai.ChatCompletion.create(
           model="gpt-35-turbo-16k"
            messages=message_text,
            deployment_id=deployment_id,
            dataSources=[
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": search_endpoint,
                        "key": search_key,
                        "indexName": search_index_name,
                    }
                }
            ]
        )

        assistant_response = completion['choices'][0]['message']['content']
        conversation_history.append({"user_question": user_question, "assistant_response": assistant_response})

    return render_template("index.html", conversation_history=conversation_history)
@app.route("/clear_history", methods=["GET"])
def clear_history():
    # Clear the conversation history
    global conversation_history
    conversation_history = []
    
    # Redirect back to the main chat page
    return redirect(url_for("index"))


if __name__ == "__main__":
    setup_byod(deployment_id)
    app.run(debug=True)
