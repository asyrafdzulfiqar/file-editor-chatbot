from pathlib import Path
import os
import json

class ReadFiles:
    
    def __init__(self, file_path):
        self.p = Path(file_path)
        
        _cwd = str(self.p.cwd().parent)
        _path = str(self.p)
        
        if _cwd in _path:
            _path = _path.replace(_cwd, "..")
            
        self.content = {"file": _path}


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
    

    def read_script(self):
        pass

    def read_pdf(self):
        pass

    def read_word(self):
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
            cell_content = new_content[cell_num]["content"]
            
            if operation == "insert_cell":
                if cell_inserted == 0:
                    original_content["cells"].insert(target_cell, cell_content)
                else:
                    original_content["cells"].insert(target_cell + cell_inserted, cell_content)
            
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
        
        updated_content = json.dumps(original_content)
        len_updated_content = len(updated_content)
        
        return updated_content, len_updated_content

    def update_script(self):
        pass

    def update_pdf(self):
        pass

    def update_word(self):
        pass
    
    
    # read "two_variable_histograms.ipynb"