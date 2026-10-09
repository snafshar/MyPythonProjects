#!/usr/bin/env python3
"""Small networking health checker using the standard library."""
import socket
import time

def check_host(host="example.com", port=443, timeout=3):
    started=time.perf_counter()
    try:
        with socket.create_connection((host,port),timeout=timeout):
            return {"host":host,"port":port,"reachable":True,"latency_ms":round((time.perf_counter()-started)*1000,2)}
    except OSError as exc:
        return {"host":host,"port":port,"reachable":False,"error":str(exc)}

if __name__=="__main__":
    print(check_host())
