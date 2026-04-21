import base64
import sqlite3
import os
import shutil
import time
from .protobuf import ProtobufEncoder
from .utils import normalize_uri

def extract_workspace_uri(raw_inner: bytes) -> str:
    if b"file:///" not in raw_inner: return ""
    try:
        pos, latest_uri = 0, ""
        while pos < len(raw_inner):
            tag, pos = ProtobufEncoder.decode_varint(raw_inner, pos)
            fn, wt = tag >> 3, tag & 7
            if wt == 2:
                length, pos = ProtobufEncoder.decode_varint(raw_inner, pos)
                content = raw_inner[pos:pos+length]
                pos += length
                if fn == 17 or fn == 9:
                    sub_pos = 0
                    while sub_pos < len(content):
                        try:
                            s_tag, sub_pos = ProtobufEncoder.decode_varint(content, sub_pos)
                            s_fn, s_wt = s_tag >> 3, s_tag & 7
                            if s_wt == 2:
                                s_len, sub_pos = ProtobufEncoder.decode_varint(content, sub_pos)
                                s_content = content[sub_pos:sub_pos+s_len]
                                sub_pos += s_len
                                if fn == 17 and s_fn == 7: latest_uri = s_content.decode('utf-8', errors='ignore')
                                elif fn == 9 and s_fn == 1 and not latest_uri: latest_uri = s_content.decode('utf-8', errors='ignore')
                            else: sub_pos = ProtobufEncoder.skip_protobuf_field(content, sub_pos, s_wt)
                        except: break
            else: pos = ProtobufEncoder.skip_protobuf_field(raw_inner, pos, wt)
        return normalize_uri(latest_uri)
    except: return ""

def extract_metadata(decoded: bytes):
    titles, blobs = {}, {}
    pos = 0
    while pos < len(decoded):
        try:
            tag, pos = ProtobufEncoder.decode_varint(decoded, pos)
        except Exception: break
        if (tag & 7) != 2: break
        length, pos = ProtobufEncoder.decode_varint(decoded, pos)
        outer_entry = decoded[pos:pos+length]
        pos += length

        ep = 0
        try:
            t, ep = ProtobufEncoder.decode_varint(outer_entry, ep)
            if (t >> 3) == 1 and (t & 7) == 2:
                l, ep = ProtobufEncoder.decode_varint(outer_entry, ep)
                if ep + l == len(outer_entry): entry = outer_entry[ep:ep + l]
                else: entry = outer_entry
            else: entry = outer_entry
        except Exception: entry = outer_entry

        ep, uid, info_b64 = 0, None, None
        while ep < len(entry):
            try:
                t, ep = ProtobufEncoder.decode_varint(entry, ep)
            except Exception: break
            fn, wt = t >> 3, t & 7
            if wt == 2:
                l, ep = ProtobufEncoder.decode_varint(entry, ep)
                c = entry[ep:ep+l]
                ep += l
                if fn == 1:
                    try: uid = c.decode('utf-8', errors='strict')
                    except UnicodeDecodeError: break
                elif fn == 2:
                    sp = 0
                    try:
                        _, sp = ProtobufEncoder.decode_varint(c, sp)
                        sl, sp = ProtobufEncoder.decode_varint(c, sp)
                        info_b64 = c[sp:sp+sl].decode('utf-8', errors='strict')
                    except Exception: pass
            elif wt == 0: _, ep = ProtobufEncoder.decode_varint(entry, ep)
            elif wt == 1: ep += 8
            elif wt == 5: ep += 4
            else: break

        if uid and info_b64:
            try:
                raw_inner = base64.b64decode(info_b64)
                blobs[uid] = raw_inner
                ip = 0
                _, ip = ProtobufEncoder.decode_varint(raw_inner, ip)
                il, ip = ProtobufEncoder.decode_varint(raw_inner, ip)
                try: found_title = raw_inner[ip:ip+il].decode('utf-8', errors='strict')
                except UnicodeDecodeError: found_title = f"Conversation {uid[:8]}"
                if not found_title.startswith("Conversation (") and not found_title.startswith("Conversation "):
                    titles[uid] = found_title
            except Exception: pass
    return titles, blobs

def create_backup(db_path: str, backup_prefix: str) -> str:
    backup_path = f"{db_path}.{backup_prefix}_{int(time.time())}_before_restore"
    shutil.copy2(db_path, backup_path)
    return backup_path

def safe_rollback(backup_path: str, target_path: str):
    try: shutil.copy2(backup_path, target_path)
    except: pass
