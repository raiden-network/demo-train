# https://stackoverflow.com/questions/24564587/communicate-between-a-processing-sketch-and-a-python-program

# Echo server program
import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5204              	# Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)
conn, addr = s.accept()
print('Connected by', addr)
while True:
    conn.send("a")
    conn.send("a")
    conn.send("a")
    conn.send("a")
    conn.send("a")
    conn.send("a")
    conn.send("a")
    conn.send("a")
    conn.send("c")
    data = conn.recv(1024)
    if not data: break
    print(data) # Paging Python!
    # # do whatever you need to do with the data
conn.close()
# optionally put a loop here so that you start 
# listening again after the connection closes