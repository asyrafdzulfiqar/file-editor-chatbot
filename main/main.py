from openai import OpenAI
from tools import *
from openai.types.responses import ResponseTextDeltaEvent, ResponseFunctionToolCall, ResponseOutputMessage, ResponseCompletedEvent, ResponseReasoningItem
from openai import BadRequestError
import json
import readline
import pprint

client = OpenAI()

messages = [
    {
        "role": "system",
        "content": "You are an efficient agent that calls functions only once. ALWAYS consult the function documentation first for clearer context and instructions."
    }
]

def chat(prompt):
    global messages
    
    while True:
        stream = client.responses.create(
            model="gpt-6-luna",
            tools=tools_openai,
            input=prompt,
            stream=True
        )

        actions = 0

        for event in stream:
            if isinstance(event, ResponseTextDeltaEvent):
                print(event.delta, end="", flush=True)
                
            elif isinstance(event, ResponseCompletedEvent):
                output = event.response.output
                
                for item in output:
                    if isinstance(item, ResponseReasoningItem):
                        messages.append(item.to_dict())
                    
                    if isinstance(item, ResponseFunctionToolCall):
                        messages.append(item.to_dict())
                        
                        actions += 1
                        arguments = json.loads(item.arguments)
                        
                        if item.name == "create_file":
                            content = arguments["content"]
                            file_path = arguments["file_path"]
                            status = create_file(content=content, file_path=file_path)
                            
                        elif item.name == "read_file":
                            file_path = arguments["file_path"]
                            status = read_file(file_path=file_path)
                            
                        elif item.name == "update_file":
                            changes = arguments["changes"]
                            file_path = arguments["file_path"]
                            status = update_file(changes=changes, file_path=file_path)
                        
                        messages.append(
                            {
                                "type": "function_call_output",
                                "call_id": item.call_id,
                                "output": status
                            }
                        )
                        
                    elif isinstance(item, ResponseOutputMessage):
                        messages.append(
                            {
                                "role": "assistant",
                                "content": item.content[0].text
                            }
                        )
                        
        if not actions:
            break
                
    print(end="\n\n", flush=False)

try:
    while True:
        
        print(f"\nTokens used: {client.responses.input_tokens.count(model='gpt-6-luna', input=messages).input_tokens}")
        prompt = input("Enter prompt: ")
        
        if prompt == "":
            print("\n[WARNING] Enter prompt! No prompt to be empty\n")
        
        else:
            print()
            
            messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )
            
            chat(messages)
            
except KeyboardInterrupt:
    import subprocess
    subprocess.run(["clear"])
    
except BadRequestError as e:
    print(e)
    pprint.pprint(messages, sort_dicts=False)
    