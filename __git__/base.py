import os
import data
import itertools
import operator
from collections import deque, namedtuple
import string

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
    commit = f"tree {write_tree()}"
    HEAD = data.get_ref("HEAD")
    if HEAD:
        commit += f"\nparent {HEAD}"
    commit += "\n\n"
    commit += f"{message}\n"

    oid = data.hash_object(commit.encode(), "commit")
    data.update_ref("HEAD", oid)
    return oid

Commit = namedtuple("Commit", ["tree", "parent", "message"])
def get_commit(oid):
    tree = None
    parent = None

    commit = data.get_object(oid, "commit").decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(" ", 1)
        if key == "tree":
            tree = value
        elif key == "parent":
            parent = value
        else:
            assert False, f"Unknown field {key}"

    message = "\n\n".join(lines)
    return Commit(tree=tree, parent=parent, message=message)

def checkout(oid):
    commit = get_commit(oid)
    read_tree(commit.tree)
    data.update_ref("HEAD", oid)

def create_tag(name, oid):
    data.update_ref(f"refs/tags/{name}", oid)

def get_oid(name):
    if name == "@":
        name = "HEAD"

    # name is ref
    refs_to_try = [
        f"{name}",
        f"refs/{name}",
        f"refs/tags/{name}",
        f"refs/heads/{name}"
    ]
    for ref in refs_to_try:
        get_ref = data.get_ref(ref) 
        print("get_ref", get_ref)
        if get_ref:
            return get_ref

    # name is SHA-1
    is_hex = all(char in string.hexdigits for char in name)
    if len(name) == 40 and is_hex:
        return name

    assert False, f'Unknown name {name}'

def iter_commits_and_parents(oids):
    oids = deque(oids)
    visited = set()

    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        visited.add(oid)
        yield oid

        commit = get_commit(oid)
        oids.appendleft(commit.parent)

def create_branch(name, oid):
    data.update_ref(f"refs/heads/{name}", oid)

