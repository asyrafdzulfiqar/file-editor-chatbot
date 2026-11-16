import json

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
            with open("test.txt", "w") as test_file:
                len_content_file_write = test_file.write(content)

        else:
            with open(file_path, "w") as test_file:
                len_content_file_write = test_file.write(content)
        
        if len_content_file_write == len_content:
            return f"File '{file_path}' created and saved successfully!"

    except Exception as e:
        return f"Error occurred: {e}"


def read_file(file_path: str) -> str:
    """
    Reads content of file in a specified file path, returns a dictionary of line numbers with their codes, MUST provide file path. 
    Call this function when user asks to read file contents at specified file path.

    Args:
        file_path: file path to read file contents from
    """

    try:
        file_io_wrapper = open(file_path, "r")
        count = 0
        status = None
        content = {}

        while True:
            item = file_io_wrapper.readline()
            if item == "":
                file_io_wrapper.close()

                return json.dumps(content)

            if status is None:
                print("Reading file...")
                status = "Reading"
            
            content[count] = item
            count += 1

    except FileNotFoundError:
        return f"Error: file in file path {file_path} not found"


def update_file(changes: str, read_file_path: str, save_file_path: str | None) -> str:
    """
    Edits file contents based on line numbers
    Example format: {1: "code here", 3: "code there", 18: "code everywhere}
    Call this function when user asks to edit a file

    Args:
        changes: a key-value pair containing the keys as line numbers in integers and values as their line of contents in string, MUST be in dictionary format
        read_file_path: file path to read file contents from
        save_file_path: optional file path to save changes to, defaulted to overwriting changes on the same file path as read_file_path
    """

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