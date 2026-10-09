import ipaddress
import sys

def report(cidr: str) -> None:
    net = ipaddress.ip_network(cidr, strict=False)
    print("Network:", net.network_address)
    print("Broadcast:", net.broadcast_address)
    print("Prefix:", net.prefixlen)
    print("Addresses:", net.num_addresses)

if __name__ == "__main__":
    report(sys.argv[1] if len(sys.argv) > 1 else "10.0.0.0/24")
