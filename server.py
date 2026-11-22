import socket
import threading
HOST = "0.0.0.0"
PORT = 8000
CLIENT_TIMEOUT = 5

PAGES = {
    "/": "<h1>Home</h1><p>Welcome to my own server.</p><a href='/about'>About</a>",
    "/about": "<h1>About</h1><p>Built from raw sockets in Python.</p><a href='/'>Home</a>",
}

def build_response(status, body):
    body_bytes = body.encode("utf-8")
    headers = (
        f"HTTP/1.1 {status}\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return headers.encode("utf-8") + body_bytes

def read_request(client_socket):
    """Keep reading until the blank line that ends the headers."""
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = client_socket.recv(4096)
        if not chunk:
            break
        data += chunk
        if len(data)>65536:
            break
    return data.decode("utf-8", errors="replace")

def handle_client(client_socket, client_address):
    client_socket.settimeout(CLIENT_TIMEOUT)
    try:
        request = read_request(client_socket)
        if not request:
            return
        request_line = request.split("\r\n")[0]
        parts = request_line.split(" ")
        if len(parts) !=3:
            client_socket.sendall(build_response("400 Bad Request", "<h1>400 Bad Request</h1>"))
            return
        method, path, version = parts  
        print(f"{client_address[0]} {method} {path}")

        if method != "GET":
            response = build_response("405 Method Not Allowed", "<h1>405 Method Not Allowed </h1>")
        elif path in PAGES:
            response = build_response("200 OK", PAGES[path])
        else:
            response = build_response("404 Not Found", "<h1>404 Not Found</h1>")    

        client_socket.sendall(response)
    except socket.timeout:
        print(f"{client_address[0]} time out (sent nothing for {CLIENT_TIMEOUT}s)")
    except OSError as error:
        print(f"{client_address[0]} connection error: {error}")
    finally:
        client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(50)
print(f"Listening on {HOST}: {PORT} ...")

while True:
    client_socket, client_address = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address),  daemon=True)
    thread.start()
                                   

