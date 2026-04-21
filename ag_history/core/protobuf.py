import base64

# ==============================================================================
# PRECISION LOGIC (PROTOBUF ENCODER)
# ==============================================================================

class ProtobufEncoder:
    @staticmethod
    def write_varint(v: int) -> bytes:
        if v < 0: raise ValueError(f"Negative varint: {v}")
        if v == 0: return b"\x00"
        result = bytearray()
        while v > 0x7F:
            result.append((v & 0x7F) | 0x80)
            v >>= 7
        result.append(v & 0x7F)
        return bytes(result)

    @classmethod
    def write_string_field(cls, field_num: int, value: str | bytes) -> bytes:
        b = value.encode("utf-8") if isinstance(value, str) else value
        return cls.write_varint((field_num << 3) | 2) + cls.write_varint(len(b)) + b

    @classmethod
    def write_bytes_field(cls, field_num: int, value: bytes) -> bytes:
        return cls.write_varint((field_num << 3) | 2) + cls.write_varint(len(value)) + value

    @classmethod
    def write_varint_field(cls, field_num: int, value: int) -> bytes:
        return cls.write_varint((field_num << 3) | 0) + cls.write_varint(value)

    @classmethod
    def write_timestamp(cls, field_num: int, epoch: int) -> bytes:
        inner = cls.write_varint_field(1, epoch) + cls.write_varint_field(2, 0)
        return cls.write_bytes_field(field_num, inner)

    @classmethod
    def build_workspace_field9(cls, ws: dict[str, str]) -> bytes:
        sub3 = cls.write_string_field(1, ws["corpus"]) + cls.write_string_field(2, ws["git_remote"])
        inner = cls.write_string_field(1, ws["uri_encoded"]) + cls.write_string_field(2, ws["uri_encoded"]) + cls.write_bytes_field(3, sub3) + cls.write_string_field(4, ws["branch"])
        return cls.write_bytes_field(9, inner)

    @classmethod
    def build_workspace_field17(cls, ws: dict[str, str], uid: str, epoch: int) -> bytes:
        sub1 = cls.write_string_field(1, ws["uri_plain"]) + cls.write_string_field(2, ws["uri_plain"])
        sub2 = cls.write_varint_field(1, epoch) + cls.write_varint_field(2, 0)
        inner = cls.write_bytes_field(1, sub1) + cls.write_bytes_field(2, sub2) + cls.write_string_field(3, uid) + cls.write_string_field(7, ws["uri_encoded"])
        return cls.write_bytes_field(17, inner)

    @staticmethod
    def decode_varint(data: bytes, pos: int) -> tuple[int, int]:
        result, shift = 0, 0
        while pos < len(data):
            b = data[pos]
            result |= (b & 0x7F) << shift
            if (b & 0x80) == 0: return result, pos + 1
            shift += 7
            pos += 1
        return result, pos

    @classmethod
    def skip_protobuf_field(cls, data: bytes, pos: int, wire_type: int) -> int:
        if wire_type == 0: _, pos = cls.decode_varint(data, pos)
        elif wire_type == 2:
            length, pos = cls.decode_varint(data, pos)
            pos += length
        elif wire_type == 1: pos += 8
        elif wire_type == 5: pos += 4
        return pos

    @classmethod
    def strip_field(cls, data: bytes, target_field_number: int) -> bytes:
        remaining = b""
        pos = 0
        while pos < len(data):
            start_pos = pos
            try:
                tag, pos = cls.decode_varint(data, pos)
            except Exception:
                remaining += data[start_pos:]
                break
            wire_type = tag & 7
            field_num = tag >> 3
            new_pos = cls.skip_protobuf_field(data, pos, wire_type)
            if new_pos == pos and wire_type not in (0, 1, 2, 5):
                remaining += data[start_pos:]
                break
            pos = new_pos
            if field_num != target_field_number:
                remaining += data[start_pos:pos]
        return remaining

    @classmethod
    def has_timestamp_fields(cls, inner_blob: bytes) -> bool:
        if not inner_blob: return False
        try:
            pos = 0
            while pos < len(inner_blob):
                tag, pos = cls.decode_varint(inner_blob, pos)
                fn = tag >> 3
                wt = tag & 7
                if fn in (3, 7, 10): return True
                pos = cls.skip_protobuf_field(inner_blob, pos, wt)
        except Exception: pass
        return False

    @classmethod
    def build_trajectory_entry(cls, uid: str, title: str, ws: dict[str, str]|None, ctime: int, mtime: int, existing_inner: bytes|None = None, step_count: int = 1) -> bytes:
        if existing_inner:
            preserved = cls.strip_field(existing_inner, 1)
            inner_pb = cls.write_string_field(1, title) + preserved

            if ws:
                inner_pb = cls.strip_field(inner_pb, 9)
                inner_pb = cls.strip_field(inner_pb, 17)
                inner_pb += cls.build_workspace_field9(ws)
                inner_pb += cls.build_workspace_field17(ws, uid, mtime)

            if not cls.has_timestamp_fields(existing_inner):
                inner_pb += cls.write_timestamp(3, ctime)
                inner_pb += cls.write_timestamp(7, mtime)
                inner_pb += cls.write_timestamp(10, mtime)
        else:
            inner_pb = (
                cls.write_string_field(1, title)
                + cls.write_varint_field(2, step_count)
                + cls.write_timestamp(3, ctime)
                + cls.write_string_field(4, uid)
                + cls.write_varint_field(5, 1)
                + cls.write_timestamp(7, mtime)
                + (cls.build_workspace_field9(ws) if ws else b"")
                + cls.write_timestamp(10, mtime)
                + (cls.build_workspace_field17(ws, uid, mtime) if ws else b"")
            )
        
        inner_b64 = base64.b64encode(inner_pb).decode("utf-8")
        wrapper = cls.write_string_field(1, inner_b64)
        entry = cls.write_string_field(1, uid) + cls.write_bytes_field(2, wrapper)
        return cls.write_bytes_field(1, entry)
