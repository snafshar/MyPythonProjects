import socket

def service_name(port: int, protocol: str = "tcp") -> str:
    try:
        return socket.getservbyport(port, protocol)
    except OSError:
        return "unknown"

if __name__ == "__main__":
    for port in (22, 53, 80, 443):
        print(port, service_name(port))
