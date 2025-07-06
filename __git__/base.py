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
     return '.__git__' in path.split('/')

def iter_tree_entries(oid):
    # tree = data.get_object(oid, expected="tree").decode()
    # tokenized_content = []

    # tree = tree[:-1].split('\n')
    # tokenized_tree = [line.split() for line in tree]
    # return tokenized_tree
    if not oid:
        return
    tree = data.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(' ', 2)
        yield type_, oid, name

def get_tree(tree_oid, base_path=""):
    result = {}
    for name, oid, type_ in iter_tree_entries(tree_oid):
        path = base_path + name
        if type_ == "blob":
            result[path] = oid
        elif type_ == "tree":
            result.update(get_tree(oid, f"{path}/"))
        else:
            assert False, f"Unknown tree entry {type_}"
    return result

def empty_current_directory():
    for root, dirnames, filenames in os.walk(".", topdown=False):
        for filename in filenames:
            path = os.path.relpath(f"{root}/{filename}")
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
        for dirname in dirnames:
            path = os.path.relpath(f"{root}/{dirname}")
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError):
                # Deletion might file if the directory contains ignored files.
                # In this case we can simply ignore the directory.
                pass

def read_tree(tree_oid):
    empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path="./").items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as file:
            file.write(data.get_object(oid))

def commit(message):
    commit = f"tree {write_tree()}\n"
    commit += "\n"
    commit += f"{message}\n"
    return data.hash_object(commit.encode(), "commit")

