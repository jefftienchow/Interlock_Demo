import socketserver
import pickle

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)


class MyHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = []
        while True:
            packet = self.rfile.readline()
            if not packet: break
            data.append(packet)
        if data:
            data_arr = pickle.loads(b"".join(data))
            print (data_arr)
            # time.sleep(3)

server = socketserver.TCPServer(('', PORT), MyHandler)
server.serve_forever()

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by', addr)
#         while True:
#             data = []
#             while True:
#                 packet = conn.recv(4096)
#                 if not packet: break
#                 data.append(packet)
#             if data:
#                 data_arr = pickle.loads(b"".join(data))
#                 print (data_arr)
