import os
import data

def write_tree(directory='.'):
    with os.scandir(directory) as path:
        for entry in path:
            full = os.path.join(directory, entry.name)
            if is_ignored(full):
                continue

            if entry.is_file(follow_symlinks=False):
                # TODO : write the file to object store
                print(full)
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)

    # TODO: actually create the tree object

def is_ignored(path):
    ignored_dirs = ['.__git__']
    if os.path.basename(path) in ignored_dirs:
        return True
    return False
