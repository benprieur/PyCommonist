'''
    get_files
'''
import os

def get_files(path):
    """ get_files """ 
    if os.path.exists(path):
        os.chdir(path)
        files = (os.listdir(path))
        items = {}
        def get_file_details(file):
            return {f:os.path.getmtime(file)}
        results = [get_file_details(file) for file in files]
        for result in results:
            for key, value in result.items():
                items[key] = value
    return items
    