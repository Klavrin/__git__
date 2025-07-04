import os
import data

def write_tree(directory='.'):
    entries = []
    with os.scandir(directory) as path:
        for entry in path:
            full = os.path.join(directory, entry.name)
            if is_ignored(full):
                continue

            oid, type_ = None, None
            if entry.is_file(follow_symlinks=False):
                type_ = "blob"
                with open(full, "rb") as file:
                    oid = data.hash_object(file.read())
            elif entry.is_dir(follow_symlinks=False):
                type_ = "tree"
                oid = write_tree(full)
            entries.append((entry.name, oid, type_))

    tree = ""
    for name, oid, type_ in sorted(entries):
        tree += f"{name} {oid} {type_}\n"

    return data.hash_object(tree.encode(), "tree")

def is_ignored(path):
    ignored_dirs = ['.__git__']
    if os.path.basename(path) in ignored_dirs:
        return True
    return False
