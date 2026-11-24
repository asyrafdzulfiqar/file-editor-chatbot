from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig, TextIteratorStreamer
import torch
from tools import *
import os
import xmltodict
from xml.parsers.expat import ExpatError
import pprint
from threading import Thread
from pathlib import Path

device = "cuda" if torch.cuda.is_available() else "cpu"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

processor = AutoProcessor.from_pretrained("Qwen/Qwen3.5-9B")
model = AutoModelForMultimodalLM.from_pretrained(
    "Qwen/Qwen3.5-9B", 
    device_map=device, 
    quantization_config=quantization_config,
)

tools = [
    create_file,
    read_file,
    update_file
]

# system_message = """You are a helpful agent utilizing tools according to user request.
# When asked to code, do not generate codes in your reasoning content, only provide it in response or tool calls.
# When you require to call multiple tools where one 
# """

messages = [
    {
        "role": "system",
        "content": "You are a helpful agent utilizing tools according to user request. When asked to code, do not generate codes in your reasoning content, only provide it in response or tool calls. When breaking down tasks for multiple tool calls, do not assume user prompts. Chain your tool calls where necessary."
    },
    {
        "role": "user",
        "content": "How are you?",
    },
    {
        "role": "assistant",
        "content": "I'm good! How do you do? What can I help you with today?"
    },
    {
        "role": "user",
        "content": "What did I just ask you?"
    },
    {
        "role": "assistant",
        "content": "You just asked me how I was doing."
    },
]

def chat(messages: list[dict], max_new_tokens: int = 32768, custom_chat_template_path: str | None = None, init: bool = False) -> None:
    global tools
    global model
    global processor

    if custom_chat_template_path:
        path = Path(custom_chat_template_path)

        if path.exists():
            with path.open() as mctf:
                custom_chat_template = ''.join(mctf.readlines())

            print("Custom chat template is being used.\n")

        else:
            raise FileNotFoundError(f"File path to custom chat template not found: '{custom_chat_template_path}'")

    else:
        custom_chat_template = None
        print("Custom chat template is NOT being used.\n")

    inputs = processor.apply_chat_template(
        messages,
        chat_template=custom_chat_template,
        tools=tools,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        enable_thinking=True
    )["input_ids"] \
        .to(model.device)

    
    if not init:
        output = processor.decode(model.generate(inputs, max_new_tokens=max_new_tokens)[0][inputs.shape[-1]:], skip_special_tokens=True)
        print(output)

        messages.append(
            {
                "role": "assistant",
                "content": output
            }
        )

    else:
        model.generate(inputs)

    # if not init:
    #     try:
    #         output = xmltodict.parse(f"<root>\n{output}\n</root>")["root"]
    #         print("[DEBUG] Output parsed to XML successfully!\n")

    #         if "think" in output:
    #             print("[Reasoning content]\n")
    #             reasoning_content = output["think"]
    #             print(reasoning_content)
    #             print()
    #         else:
    #             reasoning_content = ""

    #         if "tool_call" in output:
    #             print("[Tool calling]\n")
    #             tool = json.loads(output["tool_call"]["#text"])

    #             if tool["name"] == "create_file":
    #                 status = create_file(tool["arguments"]["content"], tool["arguments"]["file_path"])
    #                 print(status)

    #         if "#text" in output:
    #             print("[Answer]\n")
    #             print(output["#text"])

    #     except ExpatError as e:
    #         with open("error_xml.xml", "w") as error_xml:
    #             error_xml.write(f"<root>\n{processor.decode(output[0][inputs.shape[-1]-2:], skip_special_tokens=True)}\n</root>")

    #         print(f"Something went wrong: '{e}'. Saved error into 'error_xml.xml', check it out.\n")
    #         print("Here is the raw output:\n")
    #         print(processor.decode(output[0][inputs.shape[-1]-2:], skip_special_tokens=True))

    # else:
    #     model.generate(inputs, max_new_tokens=32)

print("\nInitializing, stand by...\n")
test_messages = [
    {
        "role": "user",
        "content": "Test prompt. Do not interact."
    }
]

chat(test_messages, custom_chat_template_path="modified_chat_template.txt", init=True)

print("\nInitialization complete! Test out the prompt.\n")


try:
    while True:
        print("Message history:\n")
        pprint.pprint(
            processor.apply_chat_template(
                messages,
                return_dict=True,
                tokenize=False,
                tools=tools
            ), 
            sort_dicts=False
        )
        print()
        print("-" * 150)

        prompt = input("\nPrompt: ")
        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )
        
        print()
        chat(messages, custom_chat_template_path="modified_chat_template.txt")
        print()

except KeyboardInterrupt:
    os.system("cls")