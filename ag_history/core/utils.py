import os
import re
import sys
import hashlib
import urllib.parse

def calculate_file_hash(path):
    if not os.path.isfile(path): return None
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def normalize_uri(uri: str) -> str:
    if not uri: return ""
    decoded = urllib.parse.unquote(uri).replace("\\", "/").rstrip("/")
    # Force lowercase drive letter for Windows strictness
    return re.sub(r'^(file:///?)(\w)(:|%3a)', lambda m: f"file:///{m.group(2).lower()}:", decoded, flags=re.IGNORECASE)

def build_workspace_dict(path: str) -> dict[str, str]:
    path_normalized = path.replace("\\", "/").rstrip("/")
    if sys.platform.startswith("win") and len(path_normalized) >= 2 and path_normalized[1] == ":":
        path_normalized = path_normalized[0].lower() + path_normalized[1:]
    
    folder_name = os.path.basename(path_normalized) or "RecoveredProject"
    uri_path_encoded = urllib.parse.quote(path_normalized, safe="/")
    
    return {
        "uri_encoded": f"file:///{uri_path_encoded}",
        "uri_plain": f"file:///{path_normalized}",
        "corpus": f"local/{folder_name}",
        "git_remote": f"https://github.com/local/{folder_name}.git",
        "branch": "main",
    }

def uri_to_path(uri: str) -> str:
    if not uri: return ""
    path = urllib.parse.unquote(uri).replace("file:///", "")
    if sys.platform == "win32" and path[1:2] == ":": return path.replace("/", "\\")
    return path
