import ipaddress

def describe(address: str) -> dict:
    ip = ipaddress.ip_address(address)
    return {"address": str(ip), "version": ip.version, "private": ip.is_private,
            "loopback": ip.is_loopback, "multicast": ip.is_multicast}

def network_summary(network: str) -> dict:
    net = ipaddress.ip_network(network, strict=False)
    return {"network": str(net.network_address), "broadcast": str(net.broadcast_address),
            "prefix": net.prefixlen, "num_addresses": net.num_addresses}

if __name__ == "__main__":
    print(describe("192.168.1.10"))
    print(network_summary("192.168.1.0/24"))
