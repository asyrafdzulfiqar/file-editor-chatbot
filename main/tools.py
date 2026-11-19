import json
from typing import Optional
import os
from pathlib import Path
from file_operations import ReadFiles, UpdateFiles


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
            return f"File created and saved successfully into `{file_path}`!"

    except Exception as e:
        return f"Error occurred: {e}"


def read_file(file_path: str, for_update: bool = False) -> str:
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
    readFiles = ReadFiles(file_path=path)
    
    if path.exists():
        match folder:
            case "notebooks":
                return readFiles.read_ipynb(for_update=for_update)
            
    else:
        return f'Error: file in path "{file_path}" not found.'


def update_file(changes: str, file_path: str) -> str:
    """
    Edits file contents\n
    Call this function when user asks to edit a file\n
    
    Args:
        changes: a key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in JSON format (refer to documentation below)
        file_path: file path to read file contents from
    
    ---
    
    If the file path is an `.ipynb` notebook, `changes` parameter should be in following JSON format:
    ```
    {
        cell_number: {
            "operation": "insert_cell",
            "content": {
                "cell_type": "[ markdown | code ]",
                "source": []    # line-by-line code, following IPYNB format
                "metadata": {}  # provide this attribute where necessary
            }
        },
        cell_number: {
            "operation": "edit_cell",
            "content": {
                "cell_type": "[ markdown | code ]",
                "source": {
                    line_num: "code = \"here\"",
                    line_num: "\\n",
                    line_num: "var = 123",
                    line_num: "print(var)"
                },
                "metadata": {}  # provide this attribute where necessary
            }
        },
        cell_number: {
            "operation": "delete_cell",
        }
    }
    ```
    """
    
    # To-do for this funciton:
    # 1. save changes to a log file. must include contents from before changes
    
    original_content = read_file(file_path=file_path, for_update=True)
    updateFile = UpdateFiles()
    
    # To save
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
            updated_content, len_updated_content = updateFile.update_ipynb(original_content, json.loads(changes))
            
    path = parent / folder / p
    
    with path.open("w") as file:
        len_file_write = file.write(updated_content)
    
    if len_updated_content == len_file_write:
        return f"Check file at {file_path}!"
    
    
def delete_file(file_path: str):
    pass


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
            "file_path": {
                "type": "string",
                "description": "file path to read file contents from"
            },
            "required": ["changes", "read_file_path"],
        }
    }
]