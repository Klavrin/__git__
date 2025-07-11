import hashlib
import os

GIT_DIR = ".__git__"

def init():
    os.makedirs(GIT_DIR)
    os.makedirs(f"{GIT_DIR}/objects")

def hash_object(data, type_="blob"):
    obj = type_.encode() + b"\x00" + data
    oid = hashlib.sha1(obj).hexdigest()  
    with open(f"{GIT_DIR}/objects/{oid}", "wb") as out:
        out.write(obj)
    return oid

def get_object(oid, expected: str | None = "blob"):
    with open(f"{GIT_DIR}/objects/{oid}", "rb") as file:
        obj = file.read()

        type_, _, content = obj.partition(b"\x00")
        type_ = type_.decode()

        if expected is not None:
            assert type_ == expected, f"Expected {expected}, got {type_}"
        return content

# def set_HEAD(oid):
#     with open(f"{GIT_DIR}/HEAD", "w") as file:
#         file.write(oid)
#
# def get_HEAD():
#     try:
#         with open(f"{GIT_DIR}/HEAD") as file:
#             return file.read().strip()
#     except FileNotFoundError:
#         pass

def update_ref(ref, oid):
    ref_path = f"{GIT_DIR}/{ref}"

    # extract the directory part of `ref_path` and create a full directory path inside `.__git__`
    os.makedirs(os.path.dirname(ref_path), exist_ok=True) 

    with open(ref_path, "w") as file:
        file.write(oid)

def get_ref(ref):
    try:
        rel_path = f"{GIT_DIR}/{ref}"
        value = None
        with open(rel_path) as file:
            value = file.read().strip()

        if value and value.startswith("ref:"):
            return get_ref(value.split(":", 1)[1].strip())

        return value
    except FileNotFoundError:
        pass

def iter_refs():
    refs = ["HEAD"]
    for root, _, filenames in os.walk(f"{GIT_DIR}/refs/"):
        root = os.path.relpath(root, GIT_DIR)
        refs.extend(f"{root}/{name}" for name in filenames)
        
    for refname in refs:
        yield refname, get_ref(refname)

