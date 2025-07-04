import os
import data

def write_tree(directory='.'):
    with os.scandir(directory) as path:
        for entry in path:
            full = os.path.join(directory, entry.name)
            if entry.is_file(follow_symlinks=False):
                # TODO : write the file to object store
                print(full)
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)

    # TODO: actually create the tree object

