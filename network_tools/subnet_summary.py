"""Summarise an IPv4 network without third-party dependencies."""

import ipaddress


def summarise(cidr: str) -> dict:
    network = ipaddress.ip_network(cidr, strict=False)
    hosts = list(network.hosts())
    return {
        "network": str(network.network_address),
        "broadcast": str(network.broadcast_address),
        "prefix": network.prefixlen,
        "total_addresses": network.num_addresses,
        "usable_hosts": len(hosts),
        "first_host": str(hosts[0]) if hosts else None,
        "last_host": str(hosts[-1]) if hosts else None,
    }


if __name__ == "__main__":
    for key, value in summarise("192.168.10.0/28").items():
        print(f"{key}: {value}")
