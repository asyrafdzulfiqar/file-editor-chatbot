from pathlib import Path
import os
import json
import pprint

class ReadFiles:
    
    def __init__(self, file_path):
        self.p = Path(file_path)
        
        _cwd = str(self.p.cwd().parent)
        _path = str(self.p)
        
        if _cwd in _path:
            _path = _path.replace(_cwd, "")
            
        self.content = {"file": self.p.name}


    # TODO: refactor for readability and reduce code redundancy
    def read_ipynb(self, for_update: bool):
        """
        Reads IPYNB notebooks and returns the following JSON format:
        
        ```
        {
            "file": "file_path",
            "content": {
                cell_num: {
                    "cell_type": "[ markdown | code ]",
                    "source": {
                        line_num: "code",
                        line_num: "code"
                    },
                    "outputs": {
                        "output_type": "[ execute_result | display_data | error ]",
                        "[ text/plain | text/html | error ]": "displays output content according to type"
                    }
                }
            }
        }
        ```
        
        Refer to this [documentation](https://ipython.readthedocs.io/en/3.x/notebook/nbformat.html) for further on original IPYNB format.
        """
        
        with self.p.open() as file:
            content = json.loads("".join(file.readlines()))
        
        if for_update:
            return content
        
        # designing ipynb format
        ipynb_content = {}

        cells = content["cells"]
        
        for cell_num in range(len(cells)):
            ipynb_content[cell_num] = {
                "cell_type": cells[cell_num]["cell_type"],
                "source": {}
            }
            
            source_code = cells[cell_num]["source"]
            for line_num in range(len(source_code)):
                ipynb_content[cell_num]["source"][line_num] = source_code[line_num]

            if "outputs" in cells[cell_num] :
                if len(cells[cell_num]["outputs"]) != 0:
                    ipynb_content[cell_num]["outputs"] = {}
                    output_type = cells[cell_num]["outputs"][0]["output_type"]
                    ipynb_content[cell_num]["outputs"]["output_type"] = output_type
                
                    match output_type:
                        case "execute_result":
                            data_text_plain = cells[cell_num]["outputs"][0]["data"]["text/plain"]
                            data_text_html = cells[cell_num]["outputs"][0]["data"]["text/html"]
                            ipynb_content[cell_num]["outputs"]["text/plain"] = {}
                            ipynb_content[cell_num]["outputs"]["text/html"] = {}
                            
                            for line_output in range(len(data_text_plain)):
                                ipynb_content[cell_num]["outputs"]["text/plain"][line_output] = data_text_plain[line_output]
                                
                            for line_output in range(len(data_text_html)):
                                    ipynb_content[cell_num]["outputs"]["text/html"][line_output] = data_text_html[line_output]
                                
                        case "stream":
                            data = cells[cell_num]["outputs"][0]["text"]
                            ipynb_content[cell_num]["outputs"]["text"] = {}
                            
                            for line_output in range(len(data)):
                                ipynb_content[cell_num]["outputs"]["text"][line_output] = data[line_output]
                                
                        case "error":
                            data = cells[cell_num]["outputs"][0]
                            ipynb_content[cell_num]["outputs"]["error"] = {}
                            
                            ipynb_content[cell_num]["outputs"]["error"]["error_name"] = data["ename"]
                            ipynb_content[cell_num]["outputs"]["error"]["error_value"] = data["evalue"]
        
        self.content["content"] = ipynb_content
        
        return json.dumps(self.content, indent=4)
    

    def read_script(self, for_update: bool):
        """
        Reads programming scripts and returns the following JSON format:
        
        ```
        {
            "file": "file_path",
            "content": []
        }
        ```
        """
        
        with self.p.open() as script_file:
            content = script_file.readlines()
        
        if for_update:
            return content
        
        return json.dumps(content)

    def read_documents(self):
        pass
    
    def read_image(self):
        pass
    

class UpdateFiles:

    # TODO: refactor for readability and reduce code redundancy
    def update_ipynb(self, original_content: dict, new_content: dict):
        """
        Updates IPYNB notebooks using the following format:
        
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
        
        cell_inserted = 0
        
        for cell_num in new_content:
            target_cell = int(cell_num) + cell_inserted
            operation = new_content[cell_num]["operation"]
            
            if "content" in new_content[cell_num]:
                cell_content = new_content[cell_num]["content"]
            
            if operation == "insert_cell":
                original_content["cells"].insert(target_cell, cell_content)
                cell_inserted += 1
    
            elif operation == "edit_cell":
                # change cell_type
                original_content["cells"][target_cell]["cell_type"] = cell_content["cell_type"]
                
                # change source code
                original_source = original_content["cells"][target_cell]["source"]
                
                max_lines = max([int(line_num) for line_num in cell_content["source"]]) + 1
                if len(original_source) < max_lines:
                        original_source.extend("" for _ in range(max_lines - len(original_source)))
                
                for line_num, line_code in cell_content["source"].items():
                    original_source[int(line_num)] = line_code
                
                original_content["cells"][target_cell]["source"] = [item for item in original_source if item != ""]
                
                # change metadata (if present)
                if "metadata" in cell_content:
                    original_content["cells"][target_cell]["metadata"] = cell_content["metadata"]

            elif operation == "delete_cell":
                original_content["cells"].pop(target_cell)
                cell_inserted -= 1
            
        updated_content = json.dumps(original_content)
        len_updated_content = len(updated_content)
        
        return updated_content, len_updated_content

    def update_script(self, original_content: list, operations: list):
        """
        Updates programming scripts with the following format:
        ```
        [
            {
                "operation": "edit_line",       # must reference existing line number at the time when the file was read originally, target line must be compensated by line offset after above operations
                "lines": {
                    0: "code content\\n",
                    4: "code content\\n",
                }
            },
            {
                "operation": "insert_line",      # must increment line offset by one line for every line inserted
                "lines": {
                    0: ["code content", "\\n" "code content", "\\n",  "code content"],      # list out sequential lines of code to be inserted from one place
                    1: "code content",
                    2: ["code content", "\\n", "code content"]
                }
            },
            {
                "operation": "delete_line",     # must decrease line offset by one line for every line deleted
                "lines": [0, 1, 2]
            }   
        ]
        ```
        """

        def check_operations_availability_and_positions(operations: list):
            """
            operation_positions = {
                "edit_line": {
                    "position": 0,
                    "success_state": 1
                    "message": "Correct position"
                },
                "insert_line": {
                    "position": 1,
                    "success_state": 1,
                    "messages": "Correct position"
                },
                "delete_line": {
                    "position": 0,
                    "success_state": 1,
                    "message": "Correct position"
                }
            }
            """
            
            insert_operation = delete_operation = edit_operation = False
            operation_positions = {}
            
            for position in range(len(operations)):
                if operations[position]["operation"] == "insert_line":
                    insert_operation = True
                    operation_positions["insert_line"] = {"position": position, "success_state": None, "message": None}
                    
                elif operations[position]["operation"] == "delete_line":
                    delete_operation = True
                    operation_positions["delete_line"] = {"position": position, "success_state": None, "message": None}
                    
                elif operations[position]["operation"] == "edit_line":
                    edit_operation = True
                    operation_positions["edit_line"] = {"position": position, "success_state": None, "message": None}
            
            # checking operation ordering
            if edit_operation:
                if operation_positions["edit_line"]["position"] != 0:
                    operation_positions["edit_line"]["message"] = "Edit operation not in first position!"
                    operation_positions["edit_line"]["success_state"] = 0
                
                else:
                    operation_positions["edit_line"]["message"] = "Edit position is in the correct position"
                    operation_positions["edit_line"]["success_state"] = 1
                
            if insert_operation:
                if (not edit_operation and delete_operation) and operation_positions["insert_line"]["position"] != 0:
                    operation_positions["insert_line"]["message"] = "Insert operation not in first position!"
                    operation_positions["insert_line"]["success_state"] = 0
                
                # edit exists, so insert must be second
                elif edit_operation and operation_positions["insert_line"]["position"] != 1:
                    operation_positions["insert_line"]["message"] = "Insert operation not in second position!"
                    operation_positions["insert_line"]["success_state"] = 0
                
                else:
                    operation_positions["insert_line"]["message"] = "Insert position is in the correct position"
                    operation_positions["insert_line"]["success_state"] = 1
                
            if delete_operation:
                # insert and delete only, so delete must be second position
                # edit and delete only
                if ((not edit_operation and insert_operation) or (edit_operation and not insert_operation)) and operation_positions["delete_line"]["position"] != 1:
                    operation_positions["delete_line"]["message"] = "Delete operation not in second position!"
                    operation_positions["delete_line"]["success_state"] = 0

                elif (edit_operation and insert_operation) and operation_positions["delete_line"]["position"] != 2:
                    operation_positions["delete_line"]["message"] = "Delete operation not in third position!"
                    operation_positions["delete_line"]["success_state"] = 0
                else:
                    operation_positions["delete_line"]["message"] = "Delete position is in the correct position"
                    operation_positions["delete_line"]["success_state"] = 1
            
            return operation_positions, insert_operation, delete_operation, edit_operation

        lines_inserted = 0
        len_original = len(original_content)
        
        if len(operations) > 3:
            return "Error: max three operations are allowed! If there are duplicate operations, combine them into one!"

        operations_availability_and_positions, _, delete_operation, _ = check_operations_availability_and_positions(operations)
        
        success_states = []
        ops_messages = []

        for _, metadata in operations_availability_and_positions.items():
            success_states.append(metadata["success_state"])
            ops_messages.append(metadata["message"])
            
        if not all(success_states):
            # exit function and return JSON for chat
            error = 1
            return error, json.dumps(ops_messages), 0
        
        else:
            del success_states
            del ops_messages
            error = 0
        
        # When operations positions are correct

        for operation in operations:
            
            if operation["operation"] == "edit_line":
                for line_num, line_code in operation["lines"].items():
                    original_content[int(line_num)] = line_code
            
            elif operation["operation"] == "insert_line":
                lines_inserted = 0
                
                for insert_line_num, line_code in operation["lines"].items():
                    target_line = int(insert_line_num) + lines_inserted
                    
                    if 0 <= target_line < len_original:
                        if isinstance(line_code, list):
                            # insert new lines
                            original_content[:target_line] += line_code
                            lines_inserted += len(line_code)
                            added_lines = len(line_code)
                            
                        else:
                            original_content.insert(target_line, line_code)
                            lines_inserted += 1
                            added_lines = 1
                            
                        # compensate for delete lines after insertion at different indexes
                        if delete_operation:
                            
                            # delete operation is always last
                            for position in range(len(operations[-1]["lines"])):
                                num = int(operations[-1]["lines"][position])
                                
                                if num > int(insert_line_num):
                                    # print(f"{num} is more than {int(insert_line_num)}")
                                    operations[-1]["lines"][position] = num + added_lines
                            
                    else:
                        if isinstance(line_code, list):
                            original_content += line_code
                        
                        else:
                            original_content.append(line_code)
                        
            elif operation["operation"] == "delete_line":
                # this assumes the delete operation is compensated with inserted lines
                lines_deleted = 0
                
                for line in operation["lines"]:
                    original_content.pop(int(line) - lines_deleted)
                    lines_deleted += 1
            
        updated_content = "".join(original_content)
        
        return error, updated_content, len(updated_content)
    