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
    Reads contents of file in a specified file path, returns a dictionary of line numbers in integer with their codes in string, MUST provide file path.\n 
    Call this function when user asks to read file contents or you need to understand file contents for context.

    Args:
        file_path: file path to read file contents from
        
    ---
    
    **IMPORTANT FILE PATH NOTICE:**\n
    NEVER guess where the file might be located, return to user with `FileNotFoundError` message and ask for its correct path\n
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
        changes: a series of key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in JSON format (refer to **IMPORTANT FORMATTING NOTICE** documentation below)
        file_path: file path to read file contents from
    
    ---
    
    ### IMPORTANT FORMATTING NOTICE:\n
        
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
    
    **IMPORTANT CELL NUMBER AND LINE NUMBER NOTICE:**\n
    
    Provide the cell number and line number you wish to add and edit at the time when the file is read. An internal counter is being implemented to track cell count and positioning differences.\n
    
    For example, suppose the JSON structure for an IPYNB notebook is as such:
    
    ```
    {'cells': [{'cell_type': 'code',
                'execution_count': None,
                'id': '8ea3d3f2',
                'metadata': {},
                'outputs': [],
                'source': ['print("hello there")']},
            {'cell_type': 'code',
                'execution_count': None,
                'id': '09c81d49',
                'metadata': {},
                'outputs': [],
                'source': ['"hello"']},
            {'cell_type': 'code',
                'execution_count': None,
                'id': '30b151d0',
                'metadata': {},
                'outputs': [],
                'source': ['import pandas as pd\n',
                        'df = pd.DataFrame({"Column 1": range(1, 11), "Column '
                        '2": range(11, 21)})\n',
                        'display(df)']}],
    'metadata': {'kernelspec': {'display_name': 'llm',
                                'language': 'python',
                                'name': 'python3'},
                'language_info': {'name': 'python', 'version': '3.13.18'}},
    'nbformat': 4,
    'nbformat_minor': 5}
    ```
    
    and the prompt is as such:
    
    ```
    update "*.ipynb" in the following edits: 1. create a cell at the top of the file to display a markdown title "this is a test". 2. insert another code cell at cell 1 to print "hello there". 3. edit the current second cell to display a dataframe with 2 columns and 10 records. 4. delete the last cell.
    ```
    
    the `changes` parameter should look like this:\n
    
    ```
    {
        0: {
            "operation": "insert_cell",
            "content": {
                "cell_type": "markdown",
                "source": ["# This is a test"]
            }
        },
        1: {
            "operation": "insert_cell",
            "content": {
                "cell_type": "code",
                "source": ["print(\"hello there\")"],
            }
        },
        1: {    # at the time of reading the file, this current cell BEFORE INSERTIONS above is the second cell, therefore refer to this cell number, NOT the cell number after insertion operations above
            "operation": "edit_cell",
            "content": {
                "cell_type": "code",
                "source": {
                    0: "import pandas as pd", ...
                }
            }
        },
        2: {    # at the time of reading the file, this current cell BEFORE INSERTIONS above is the last cell, therefore refer to this cell number, NOT the cell number after insertion operations above
            "operation": "delete_cell"
        }
    }
    ```\n
    
    For every insertion, an internal counter is already keeping track of the cell number by adding how many cells were inserted. Therefore, keep the cell number in the `changes` parameter referencing the cell number at the time of reading the file. DO NOT ASSUME what cell numbers would be after adding a cell.\n
    Note that **you are referencing 0-based indexing** while manipulating contents, while **user prompts are using 1-based indexing** for easy reference. Note this difference.
    
    **IMPORTANT REMOVING LINES NOTICE:**\n
    
    Include lines where they need to be removed from the lines of code with:
        - `.ipynb` notebook: ```"source": {line_num: "editing this line", line_num: "", line_num: ""}      # two lines removed from code, IMPORTANT to include to remove unwanted lines of code in a cell```
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
            updated_content, len_updated_content = updateFile.update_ipynb(original_content, changes)
            
    path = parent / folder / p
    
    with path.open("w") as file:
        len_file_write = file.write(updated_content)
    
    if len_updated_content == len_file_write:
        return f"File overwrite successful at `{file_path}`!"
    
    
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
            "changes": {
                "type": "string",
                "description": "a key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in dictionary format"
            },
            "file_path": {
                "type": "string",
                "description": "file path to read file contents from"
            },
            "required": ["changes", "file_path"],
        }
    }
]

# edit two_variable_histograms.ipynb file's last cell to change its contents to printing hello world