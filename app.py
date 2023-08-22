# Copyright 2023 https://github.com/ShishirPatil/gorilla
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import gradio as gr
import openai
import re

# There is no need for an API key let the following be as is
openai.api_key = "EMPTY"

# Set up the API base
openai.api_base = "http://zanino.millennium.berkeley.edu:8000/v1"
# If there is any issue try using
# openai.api_base = "http://34.132.127.197:8000/v1"

# Define function to get Gorilla response
def get_gorilla_response(prompt, model="gorilla-7b-hf-v1"):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

# Define function to parse output
def parse_output(text, model):
    if model == "gorilla-7b-hf-v1":
        components = {}
        components['domain'] = text.split("<<<domain>>>:")[1].split("<<<api_call>>>")[0].strip()
        components['api_call'] = text.split("<<<api_call>>>:")[1].split("<<<api_provider>>>")[0].strip()
        components['api_provider'] = text.split("<<<api_provider>>>:")[1].split("<<<explanation>>>")[0].strip()
        components['explanation'] = text.split("<<<explanation>>>:")[1].split("<<<code>>>")[0].strip()
        components['code'] = text.split("<<<code>>>:")[1].strip()
        return components
    elif model == "gorilla-mpt-7b-hf-v0":
        keys_to_remove = ['api_call', 'api_provider', 'explanation', 'code']
        x = text.split(":")
        x.pop(0)
        for i in range(len(x)):
            for key in keys_to_remove:
                x[i] = x[i].replace(f'{key}','').replace(f", '{key}'", '').replace(f", '{key}':", '').replace(f"'{key}':", '').replace('''\\"''','''"''').replace('''"\\''','''"''').replace("""\'""","""'""").replace("""'\\""","""'""")
        components = {
            'domain': x[0].strip("' ").replace("\n<<<","").replace('"','').replace('<','').replace('>',''),
            'api_call': x[1].strip("' ").replace("\n<<<","").replace('<','').replace('>',''),
            'api_provider': x[2].strip("' ").replace("\n<<","").replace('<','').replace('>',''),
            'explanation': x[3].strip("' ").replace(r'\n', '\n').replace('<','').replace('>',''),
            'code': x[4].strip("' ").replace(r'\n', '\n').replace('<','').replace('>','')
        }
        return components
    elif model == "gorilla-7b-th-v0":
        x = text.split(":")
        keys_to_remove = ['api_call', 'api_provider', 'explanation', 'code']
        x.pop(0)
        for i in range(len(x)):
            for key in keys_to_remove:
                x[i] = x[i].replace(f", '{key}'", '').replace(f", '{key}':", '').replace(f"'{key}':", '').replace('''\\"''','''"''').replace('''"\\''','''"''').replace("""\'""","""'""").replace("""'\\""","""'""")
        components = {
            'domain': x[0].strip("' "),
            'api_call': x[1].strip("' "),
            'api_provider': x[2].strip("' "),
          'explanation': x[3].strip("' ").replace(r'\n', '\n'),
          'code': x[4].strip("' ").replace(r'\n', '\n')
        }
        return components

# Define the function for the interface
def parse_and_display(prompt, model):
    text = get_gorilla_response(prompt, model)
    components = parse_output(text, model)
    domain = components['domain']
    api_call = components['api_call']
    api_provider = components['api_provider']
    explanation = components['explanation']
    code = components['code']
    return domain, api_call, api_provider, explanation, code

# Define example prompts
examples = [
    ["I would like to translate 'I feel very good today.' from English to French.","gorilla-7b-hf-v1"],
    ["I want to build a robot that can detecting objects in an image ‘cat.jpeg’. Input: [‘cat.jpeg’]","gorilla-7b-hf-v1"],
    ["I would like to translate from English to Chinese.","gorilla-7b-th-v0"],
]

# Create the Gradio interface
iface = gr.Interface(
    fn=parse_and_display,
    inputs=["text", gr.components.Dropdown(["gorilla-7b-hf-v1", "gorilla-7b-th-v0",  "gorilla-7b-tf-v0", "gorilla-mpt-7b-hf-v0"], label="Model")],
    outputs=[
        gr.components.Textbox(label="Domain"),
        gr.components.Textbox(label="API Call"),
        gr.components.Textbox(label="API Provider"),
        gr.components.Textbox(label="Explanation"),
        gr.components.Code(label="Code")
    ],
    title="Gorilla Gradio Explorer",
    description="Gorilla is an LLM that can pick the right API for your tasks. Check out the examples below. Learn more at gorilla.cs.berkeley.edu",
    examples=examples,
)

# Launch the interface and get the public gradio link
iface.launch()