import json
from typing import Optional
import os
from pathlib import Path
from file_operations import ReadFiles, UpdateFiles


def folder_assignment(file_path: str):
    parent = Path().cwd().parent
    p = Path(file_path)
    
    match p.suffix:
        case ".ipynb":
            folder = "notebooks"
            
        case _:
            folder = "scripts"
    
    return parent / folder / p.name


def create_file(content: str, file_path: str | None) -> str:
    """
    Injects code into a script and saves into a custom file path, current working directory is defaulted with the extension ".txt". 
    Call this tool when a user asks to create a new script.

    Args:
        content: strings of code to store in a script file
        file_path: custom file path to store script file to, MUST have an extension at the end
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
            case ".ipynb":
                folder = "notebooks"
                
            case _:
                folder = "scripts"
        
        target_path = parent / folder / p.name
        
        with target_path.open("w") as file:
            len_content_file_write = file.write(content)
            
        if len_content_file_write == len_content:
            return f"File created and saved successfully into `{file_path}`!"

    except Exception as e:
        return f"Error occurred: {e}"


def read_file(file_path: str, for_update: bool = False) -> str:
    """
    Reads contents of file in a specified file path, returns a dictionary of line numbers in integer with their codes in string, MUST provide file path.\n 
    Call this function when user asks to read file contents or you need to understand file contents for context.

    Args:
        file_path: file path to read file contents from
        
    ---
    
    **IMPORTANT FILE PATH NOTICE:**\n
    Assume that the file path given is in the current working directory.\n
    NEVER guess where the file might be located when you are returned `FileNotFoundError` message. Ask the user for its correct path.\n
    """
    
    parent = Path().cwd().parent
    p = Path(file_path)
    extension = p.suffix
    
    if not extension:
        return f'Error: file "{file_path}" has no extension.'
    
    match extension:
        case ".ipynb":
            folder = "notebooks"
            
        case _:
            folder = "scripts"
    
    path = parent / folder / p
    
    readFiles = ReadFiles(file_path=path)
    
    if path.exists():
        match folder:
            case "notebooks":
                # `for_update`: False for gpt format (default), True for raw list
                return readFiles.read_ipynb(for_update=for_update)
            
            case "scripts":
                return readFiles.read_script(for_update=for_update)
            
    else:
        return f'Error: file in path "{file_path}" not found.'


def update_file(file_path: str, changes: list,) -> str:
    """
    Edits file contents\n
    Call this function when user asks to udpate or edit a file\n
    Imperative that you read the target file content first before suggesting an edit!\n
    NEVER run this function until the user verifies your formatting\n
    Show the user your appropriate JSON formatting based on tpye of file you are editing first\n
    
    Args:
        changes: a series of key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in JSON format (refer to **IMPORTANT FORMATTING NOTICE** documentation below)
        file_path: file path to read file contents from
    
    ---
    
    ### Important Formatting Notice:\n
        
    `changes` parameter should be in following JSON format if the file is a/an:
    
    - `.ipynb` notebook:
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
    
    - `.py`, `.txt`, `.json` or similar scripting extensions:
    ```
    # all lines must reference their respective positions at the time of reading file contents
    # order of operations must strictly be in this order: `edit_line`, `insert_line`, `delete_line`
    # NEVER use `edit_line` to edit one line to insert multiple lines of code!!! Use `insert_line` instead
    # always insert the newline character at the end of line you are editing
    
    [
        {
            "operation": "edit_line",    # must reference line position at the time of file read, NOT after above operations
            "lines": {
                0: "code content",
                4: "code content",
            }
        },
        {
            "operation": "insert_line", 
            "lines": {
                0: ["code content", "\\n" "code content", "\\n",  "code content"],    # list out sequential lines of code to be inserted from one place
                1: "code content",    # prepare only one line of code for lines requiring only one line of code to be inserted
                2: ["code content", "\\n", "code content"]
            }
        },
        {
            "operation": "delete_line",  
            "lines": [0, 1, 2]    # prepare line(s) of code to remove in list
        },
    ]
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
        case ".ipynb":
            folder = "notebooks"
            updated_content, len_updated_content = updateFile.update_ipynb(original_content, changes)
        
        case _:
            folder = "scripts"
            error, updated_content, len_updated_content = updateFile.update_script(original_content, changes)
            
            if error:
                return updated_content
                
    path = parent / folder / p
    
    with path.open("w") as file:
        len_file_write = file.write(updated_content)
    
    if len_updated_content == len_file_write:
        return f"File overwrite successful at `{file_path}`! [IMPORTANT] Read the file again to ensure all edits are correct."
    
    
def delete_file(file_path: str):
    pass


# OpenAI format for tools

tools_openai =  [
    {
        "type": "function",
        "name": "create_file",
        "description": create_file.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string"
                },
                "file_path": {
                    "type": "string"
                }
            },
            "required": ["content", "file_path"],
            "strict": True
        }
    },
    {
        "type": "function",
        "name": "read_file",
        "description": read_file.__doc__,
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
        "description": update_file.__doc__,
        "parameters": {
            "file_path": {
                "type": "string",
                "description": "file path to read file contents from"
            },
            "changes": {
                "type": "string",
                "description": "a key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in dictionary format"
            },
            "required": ["changes", "file_path"],
        }
    }
]

# edit two_variable_histograms.ipynb file's last cell to change its contents to printing hello world

# update hello.py to include object detection capabilities with rf-detr model