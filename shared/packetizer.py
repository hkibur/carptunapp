import random

def bitslice(val, start, stop):
        return (val >> start) & ((1 << (stop - start)) - 1)

class PacketLayoutContext(object):
    def __init__(self):
        self.meta_byte_len = None
        self.meta_layout = [("frame_type", 8)]

        self.layout_byte_lens = {}
        self.layouts = {}

        self.frame_type_lookup = []

        self.resolve_lengths_with_pad()

    def resolve_lengths_with_pad(self):
        meta_bit_len = 0
        for name, elm_bit_len in self.meta_layout: 
            if name == "_PAD":
                self.meta_layout.remove((name, elm_bit_len))
                continue
            meta_bit_len += elm_bit_len
        self.meta_layout.append(("_PAD", (8 - meta_bit_len) % 8))
        self.meta_byte_len = (meta_bit_len + 7) // 8

        for layout_name, layout in self.layouts.iteritems():
            bit_len = 0
            for name, elm_bit_len in layout: 
                if name == "_PAD":
                    layout.remove((name, elm_bit_len))
                    continue
                bit_len += elm_bit_len
            layout.append(("_PAD", (8 - bit_len) % 8))
            self.layout_byte_lens[layout_name] = (bit_len + 7) // 8

    def get_layout_from_frame_type(self, frame_type):
        name = self.frame_type_lookup[frame_type]
        return (self.layouts[name], self.layout_byte_lens[name])

def get_raw(sock, byte_len):
    buf = bytearray(byte_len)
    window = memoryview(buf)
    while byte_len > 0:
        bytes_read = sock.recv_into(window, byte_len)
        window = window[bytes_read:]
        byte_len -= bytes_read
    return buf

def packet_to_dict(raw, layout):
    packet_dict = {}
    bit_offset = 0
    byte_ind = 0
    for elm, bit_len in layout:
        val = bitslice(raw[byte_ind], max(8 - (bit_len + bit_offset), 0), 8 - bit_offset)
        bit_len -= 8 - bit_offset
        if bit_len <= 0:
            packet_dict[elm] = val
            bit_offset = 8 + bit_len
            continue
        while bit_len > 8:
            byte_ind += 1
            val <<= 8
            val |= raw[byte_ind]
            bit_len -= 8
        byte_ind += 1
        val <<= max(bit_len, 0)
        val |= bitslice(raw[byte_ind], 8 - bit_len, 8)
        packet_dict[elm] = val
        bit_offset = bit_len
    return packet_dict

def pop_packet(sock, layout_context):
    meta_dict = packet_to_dict(get_raw(sock, layout_context.meta_byte_len), layout_context.meta_layout)
    packet_layout, packet_layout_byte_len = layout_context.get_layout_from_frame_type(meta_dict["frame_type"])
    return packet_to_dict(get_raw(sock, packet_layout_byte_len), packet_layout)

def serialize_packet_dict(view, packet_dict, layout):
    bit_offset = 0
    for field, bit_len in layout:
        if bit_len == 0: continue
        field_view = view[:(bit_offset + bit_len + 7) // 8]
        temp_arr = bytearray(field_view)
        val = packet_dict[field] if field != "_PAD" else 0
        bit_len -= 8 - bit_offset
        ind = None
        if bit_len < 0: 
            temp_arr[0] |= val << (~bit_len + 1)
            bit_offset = 8 + bit_len
            ind = 0
        else: 
            temp_arr[0] |= val >> bit_len
            ind = 1
            while bit_len >= 8:
                bit_len -= 8
                temp_arr[ind] = (val >> bit_len) & 0xFF
                ind += 1
            if bit_len > 0: temp_arr[ind] = (val << (8 - bit_len)) & 0xFF
            bit_offset = bit_len
        field_view[:] = temp_arr
        view = view[ind:]

def push_packet(sock, content, layout_context, layout_name):
    packet_bytes = bytearray(layout_context.meta_byte_len + layout_context.layout_byte_lens[layout_name])
    main_view = memoryview(packet_bytes)
    meta = {
        "frame_type": layout_context.frame_type_lookup.index(layout_name)
    }
    serialize_packet_dict(main_view[:layout_context.meta_byte_len], meta, layout_context.meta_layout) #Slice the main view just to be safe
    serialize_packet_dict(main_view[layout_context.meta_byte_len:], content, layout_context.layouts[layout_name])
    for b in packet_bytes:
        print bin(b)[2:].zfill(8), 
    return packet_bytes

if __name__ == "__main__":
    lcon = PacketLayoutContext()
    lcon.layouts["sample"] = []
    for i in xrange(5):
        lcon.layouts["sample"].append((str(i), random.randint(1, 20)))
    lcon.resolve_lengths_with_pad()
    lcon.frame_type_lookup.append("sample")
    sample_values = {}
    for name, width in lcon.layouts["sample"]:
        sample_values[name] = random.randint(0, (2 ** width) - 1)
    print sample_values
    print lcon.layouts["sample"]
    ser = push_packet(None, sample_values, lcon, "sample")
    print
    print packet_to_dict(ser[1:], lcon.layouts["sample"])