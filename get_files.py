'''
    get_files
'''
import os


'''
    get_files
'''
def get_files(path):    
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