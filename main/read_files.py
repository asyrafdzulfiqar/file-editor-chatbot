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
    def read_ipynb(self):
        with self.p.open() as file:
            content = json.loads("".join(file.readlines()))
        
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

            if "outputs" in cells[cell_num]:
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
                        data = cells[cell_num]["outputs"][0]["data"]["text"]
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
    
    
    # read "two_variable_histograms.ipynb"