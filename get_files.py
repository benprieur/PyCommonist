'''
    get_files
'''
def get_files(path):
    import os
    if os.path.exists(path):
        os.chdir(path)
        files = (os.listdir(path))
        items = {}
        def get_file_details(f):
            return {f:os.path.getmtime(f)}
        results = [get_file_details(f) for f in files]
        for result in results:
            for key, value in result.items():
                items[key] = value
    return items