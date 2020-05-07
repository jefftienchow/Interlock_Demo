import pickle
import socketserver
import socket

PORT = 12345

class ActuatorHandler(socketserver.StreamRequestHandler):
    def handle(self):
        data = []
        while True:
            packet = self.rfile.readline()
            if not packet:
                break
            data.append(packet)
        if data:
            result = pickle.loads(b"".join(data))
            if not (result):
                print("Stop! Intervention from monitor!")

def main():
    print('actuator: ', socket.gethostbyname(socket.gethostname()))
    server = socketserver.TCPServer(('', PORT), ActuatorHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
