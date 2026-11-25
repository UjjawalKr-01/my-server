import socket
import sys
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
TOTAL = int(sys.argv[2]) if len(sys.argv) > 2 else 500
WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 50
IDLE = int(sys.argv[4]) if len(sys.argv) > 4 else 0

def one_request():
    start = time.pref_counter()
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=10) as S:
            s.sendall(b"GET /about HTTP/1.1\r\nHost: localhost\r\n\r\n")
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
        ok = data.startswith(b"HTTP/1.1 200")
    except OSError:
        ok = False
    return time.perf_counter() - start, ok

idle_sockets = []
for _ in range(IDLE):
    try:
        idle_sockets.append(socket.create_connection(("127.0.0.1", PORT), timeout=10))
    except OSError:
        break

print(f"Port {PORT}: {TOTAL} requests, {WORKERS} at a time, {len(idle_sockets)} idle connection open")

begin = time.perf_counter()
with ThreadPoolExecutor(max_Workers=WORKERS) as pool:
    results = list(pool.map(lambda _: one_request(), range(TOTAL)))
elapsed = time.perf_counter() - begin

for s in idle_sockets:
    s.close()

times = sorted(t for t, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)

print(f"Total time:      {elapsed:.2f} s")
print(f"Requests/second: {TOTAL / elapsed:.0f}")
print(f"Failed:          {failed}")
if times:
    print(f"Latency average: {statistics.mean(times) * 1000:.1f} ms")
    print(f"Latency 95th %:  {times[int(len(times) * 0.95) - 1] * 1000:.1f} ms")
    print(f"Latency max:     {times[-1] * 1000:.1f} ms")