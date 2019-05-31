import time
import socket
import threading

TCP_IP = "localhost"
TCP_PORT = 111
BUF_LEN = 1024

def bitslice(val, start, stop):
        return (val >> start) & ((1 << (stop - start)) - 1)

LOGIN_FRAME_LAYOUT = [
    ("name", 64),
]

user_info = {
    "john": {
        "wpm_thresh": 70,
    }
}

class CarpalTunnelConnection(object):

    #States
    AWAIT_LOGIN = 0
    LOGIN_RECEIVED = 1
    LOGIN_INFO_VERIFIED = 2
    LOGIN_RESP_SENT = 3
    CLOSED = 4

    #Frame types
    LOGIN_FRAME = 0
    LOGIN_RESP_FRAME = 1

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.state = self.AWAIT_LOGIN

    def resolve_frame(self, buffer, layout):
        frame_dict = {}
        main_view = memoryview(buffer)
        for elm, byte_len in layout:
            frame_dict[elm] = main_view[:byte_len].tobytes()
            main_view = main_view[byte_len:]
        return frame_dict

    def do_login(self, buffer):
        self.state = self.LOGIN_RECEIVED
        frame_dict = self.resolve_frame(buffer, LOGIN_FRAME_LAYOUT)
        info = user_info[frame_dict["name"].strip()]
        self.state = self.LOGIN_INFO_VERIFIED
        frame_meta = 1 << 3
        frame_meta |= self.LOGIN_RESP_FRAME
        frame_buf = bytearray(3)
        frame_buf[0] = frame_meta >> 8
        frame_buf[1] = frame_meta & 0xFF
        frame_buf[2] = info["wpm_thresh"]
        self.conn.sendall(frame_buf)
        self.state = self.LOGIN_RESP_SENT
        self.state = self.CLOSED

    def receive_loop(self):
        while self.state != self.CLOSED:
            frame_meta = bytes(self.conn.recv(2))
            if not frame_meta:
                break
            frame_meta = (ord(frame_meta[0]) << 8) | ord(frame_meta[1])
            frame_length = bitslice(frame_meta, 3, frame_meta.bit_length())
            frame_type = bitslice(frame_meta, 0, 3)
            body_buffer = bytearray(frame_length)
            view = memoryview(body_buffer)
            while frame_length > 0:
                nbytes = self.conn.recv_into(view, frame_length)
                view = view[nbytes:]
                frame_length -= nbytes
            if frame_type == self.LOGIN_FRAME: self.do_login(body_buffer)
        if self.state == self.CLOSED:
            self.conn.shutdown(socket.SHUT_RDWR)
        self.state == self.CLOSED
        self.conn.close()

class CarpalTunnelServer(object):
    def __init__(self):
        self.closing = False
        self.connections = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((TCP_IP, TCP_PORT))
        self.sock.listen(1)

        print "listening"

        self.conn_sleep_time = 0.5
        self.conn_thread = threading.Thread(target = self.conn_worker)
        self.conn_thread.start()

        while True:
            print ">",
            if raw_input() == "q":
                self.closing = True
                self.conn_thread.join()
                break

    def conn_worker(self):
        while not self.closing:
            try:
                conn, addr = self.sock.accept()
            except socket.error:
                time.sleep(self.conn_sleep_time)
                continue
            print "Connection from", addr
            self.connections.append(CarpalTunnelConnection(conn, addr))
            threading.Thread(target = self.connections[-1].receive_loop).start()
        for connection in self.connections:
            connection.state = CarpalTunnelConnection.CLOSED

CarpalTunnelServer()