import socket

HOST = "0.0.0.0"
PORT = 8000

# 1. Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 2. Bind it to an address and port
server_socket.bind((HOST, PORT))

# 3. Start listening for connections
server_socket.listen(5)
print(f"Listening on {HOST}:{PORT} ...")

while True:
    # 4. Wait here until a client connects
    client_socket, client_address = server_socket.accept()
    print(f"\n--- Connection from {client_address} ---")

    # 5. Read the raw request the client sent
    request = client_socket.recv(4096).decode("utf-8", errors="replace")
    print(request)

    # 6. Build the response by hand
    body = "<h1>Hello from my own server!</h1>"
    body_bytes = body.encode("utf-8")
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    # 7. Send it and close the connection
    client_socket.sendall(headers.encode("utf-8") + body_bytes)
    client_socket.close()
