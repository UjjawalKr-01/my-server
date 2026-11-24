import asyncio

HOST = "0.0.0.0"
PORT = 8001  # different from server.py (8000) so both can run side by side
CLIENT_TIMEOUT = 5  # seconds a client may take to send its headers

PAGES = {
    "/": "<h1>Home</h1><p>Welcome to my own server (asyncio).</p><a href='/about'>About</a>",
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


async def handle_client(reader, writer):
    peer = writer.get_extra_info("peername")
    ip = peer[0] if peer else "unknown"
    try:
        try:
            raw = await asyncio.wait_for(
                reader.readuntil(b"\r\n\r\n"), timeout=CLIENT_TIMEOUT
            )
        except asyncio.IncompleteReadError:
            return  # client connected and closed without a full request
        except asyncio.LimitOverrunError:
            writer.write(build_response("431 Request Header Fields Too Large",
                                        "<h1>431 Headers Too Large</h1>"))
            await writer.drain()
            return

        request = raw.decode("utf-8", errors="replace")
        request_line = request.split("\r\n")[0]
        parts = request_line.split(" ")
        if len(parts) != 3:
            writer.write(build_response("400 Bad Request", "<h1>400 Bad Request</h1>"))
            await writer.drain()
            return

        method, path, version = parts
        print(f"{ip} {method} {path}")

        if method != "GET":
            response = build_response("405 Method Not Allowed", "<h1>405 Method Not Allowed</h1>")
        elif path in PAGES:
            response = build_response("200 OK", PAGES[path])
        else:
            response = build_response("404 Not Found", "<h1>404 Not Found</h1>")

        writer.write(response)
        await writer.drain()
    except asyncio.TimeoutError:
        print(f"{ip} timed out (sent no complete request in {CLIENT_TIMEOUT}s)")
    except OSError as error:
        print(f"{ip} connection error: {error}")
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            pass


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT, backlog=100)
    print(f"Listening on {HOST}:{PORT} (asyncio) ...")
    async with server:
        await server.serve_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nStopped.")