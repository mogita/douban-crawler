from os import getcwd


def get_real_path(filepath):
    cwd = getcwd()
    if not filepath.startswith("/"):
        filepath = cwd + "/" + filepath
    return filepath
