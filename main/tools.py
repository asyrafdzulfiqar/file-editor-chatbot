import json
from typing import Optional
import os
from pathlib import Path
from read_files import ReadFiles

def create_file(content: str, file_path: str | None) -> str:
    """
    Injects code into a script and saves into a custom file path, current working directory is defaulted with the extension ".txt". 
    Call this tool when a user asks to create a new script.

    Args:
        content: strings of code to store in a script file
        file_path: custom file path to store script file to, MUST have an extension at the end

    Returns:
        status: status of file creation and storing
    """

    len_content = len(content)
    
    try:
        if not file_path:
            file_path = "test.txt"
            
        elif file_path and not os.path.splitext(file_path)[-1]:
            file_path = file_path + ".txt"
        
        parent = Path().cwd().parent
        p = Path(file_path)
        
        match p.suffix:
            case ".txt" | ".py" | ".json" | ".R":
                folder = "scripts"
                
            case ".ipynb":
                folder = "notebooks"
        
        target_path = parent / folder / p.name
        
        with target_path.open("w") as file:
            len_content_file_write = file.write(content)
            
        if len_content_file_write == len_content:
            target_path = str(target_path)
            parent = str(parent)
            target_path = target_path.replace(parent, "..")
                
            return f"File created and saved successfully into `{target_path}`!"

    except Exception as e:
        return f"Error occurred: {e}"


def read_file(file_path: str) -> str:
    """
    Reads content of file in a specified file path, returns a dictionary of line numbers with their codes, MUST provide file path. 
    Call this function when user asks to read file contents at specified file path.\n
    NEVER guess where the file might be located, return to user with `FileNotFoundError` message and ask for its correct path\n

    Args:
        file_path: file path to read file contents from
    """
    parent = Path().cwd().parent
    p = Path(file_path)
    extension = p.suffix
    
    if not extension:
        return f'Error: file "{file_path}" has no extension.'
    
    match extension:
        case ".txt" | ".py" | ".json" | ".R":
            folder = "scripts"
        
        case ".ipynb":
            folder = "notebooks"
    
    path = parent / folder / p
    
    if path.exists():
        match folder:
            case "notebooks":
                return ReadFiles(file_path=path).read_ipynb()
            
    else:
        return f'Error: file in path "{file_path}" not found.'


def update_file(changes: str, read_file_path: str, save_file_path: Optional[str]) -> str:
    """
    Edits file contents based on line numbers\n
    Example format: {1: "code here", 3: "code there", 18: "code everywhere}\n
    Call this function when user asks to edit a file

    Args:
        changes: a key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in dictionary format
        read_file_path: file path to read file contents from
        save_file_path: optional file path to save changes to, defaulted to overwriting changes on the same file path as read_file_path
    """
    
    # To-do for this funciton:
    # 1. save changes to a log file. must include contents from before changes
    
    with open(read_file_path, "r") as file:
        content = file.readlines()

    content_changes = json.loads(changes)

    for line, code in content_changes:
        content.pop(line)
        content.insert(line, code)

    edited_content = "".join(content)

    if save_file_path:
        with open(save_file_path, "w") as file:
            file.write(edited_content)

    else:
        with open(read_file_path, "w") as file:
            file.write(edited_content)

    return "Changes made and saved!"


# OpenAI format for tools

tools_openai =  [
    {
        "type": "function",
        "name": "create_file",
        "description": "Injects code into a script and saves into a custom file path, current working directory is defaulted with the extension '.txt'. Call this tool when a user asks to create a new script.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "strings of code to store in a script file"
                },
                "file_path": {
                    "type": "string",
                    "description": "custom file path to store script file to, MUST have an extension at the end"
                }
            },
            "required": ["content"],
            "strict": True
        }
    },
    {
        "type": "function",
        "name": "read_file",
        "description": "Reads contents of file in a specified file path, returns a dictionary of line numbers in integer with their codes in string, MUST provide file path. Call this function when user asks to read file contents or you need to understand file contents for context.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "file path to read file contents from"
                },
            },
            "required": ["file_path"],
        }
    },
    {
        "type": "function",
        "name": "update_file",
        "description": "Edits file contents based on line numbers. Call this function when user asks to edit a file.",
        "parameters": {
            "changes": {
                "type": "string",
                "description": "a key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in dictionary format"
            },
            "read_file_path": {
                "type": "string",
                "description": "file path to read file contents from"
            },
            "save_file_path": {
                "type": "string",
                "description": "optional file path to save changes to, defaulted to overwriting changes on the same file path as read_file_path"
            },
            "required": ["changes", "read_file_path"],
        }
    }
]