import socket
import dns.message
import dns.query
import dns.rdatatype
import ipaddress
import json

# File containing NAT (Network Address Translation) rules
nat_table_file = 'dns_nat_table.json'

# Default DNS resolver IP address to use as a fallback
default_dns = '1.1.1.1'

def load_nat_table():
    """
    Loads the NAT table from a JSON file and returns a dictionary.
    Each entry in the dictionary represents a DNS zone with its mappings and optional resolver.
    """
    try:
        with open(nat_table_file, 'r') as file:
            data = json.load(file)
            return {
                zone: {
                    "mappings": {ipaddress.ip_network(src): ipaddress.ip_network(dst) for src, dst in zone_data["mappings"].items()},
                    "resolver": zone_data.get("resolver")
                } for zone, zone_data in data.items()
            }
    except (FileNotFoundError, json.JSONDecodeError):
        # Returns an empty dictionary if the file is not found or JSON is invalid
        return {}

def is_subdomain_of(subdomain, domain):
    """
    Checks if a given subdomain is part of a specified domain.
    """
    return subdomain == domain or subdomain.endswith('.' + domain)

def translate_ip(zone, ip, nat_table):
    """
    Translates an IP address based on the NAT table.
    If the IP address is within a defined source network for a zone, it's translated to the corresponding destination network.
    """
    for defined_zone, zone_data in nat_table.items():
        if is_subdomain_of(zone, defined_zone):
            for src_net, dst_net in zone_data["mappings"].items():
                if ip in src_net:
                    offset = int(ip) - int(src_net.network_address)
                    translated_ip = int(dst_net.network_address) + offset
                    return ipaddress.ip_address(translated_ip)
    return ip

def handle_request(data, addr, sock, nat_table):
    """
    Processes incoming DNS queries.
    Extracts the query, identifies the appropriate zone and resolver, performs the query, modifies the response based on NAT table, and sends the response back to the client.
    """
    try:
        query = dns.message.from_wire(data)
        zone = query.question[0].name.to_text(omit_final_dot=True)

        # Default resolver IP is used unless a specific resolver is defined for the zone in the NAT table
        resolver_ip = default_dns 
        for defined_zone, zone_data in nat_table.items():
            if is_subdomain_of(zone, defined_zone) and zone_data.get("resolver"):
                resolver_ip = zone_data["resolver"]
                break

        response = dns.query.udp(query, resolver_ip)

        # Modifying the response based on NAT rules
        for i, rrset in enumerate(response.answer):
            if rrset.rdtype == dns.rdatatype.A:
                new_rrset = dns.rrset.RRset(rrset.name, rrset.rdclass, rrset.rdtype, rrset.ttl)
                for rr in rrset:
                    original_ip = ipaddress.ip_address(rr.address)
                    translated_ip = translate_ip(zone, original_ip, nat_table)
                    if translated_ip != original_ip:
                        new_rr = dns.rdtypes.IN.A.A(rr.rdclass, rr.rdtype, str(translated_ip))
                        new_rrset.add(new_rr, rrset.ttl)
                    else:
                        new_rrset.add(rr, rrset.ttl)
                response.answer[i] = new_rrset

        # Sending the modified response to the client
        sock.sendto(response.to_wire(), addr)
    except Exception as e:
        print(f"Error processing request: {e}")

def main():
    """
    Main function. Sets up a DNS server, listens for requests, and processes them.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 53))

    try:
        while True:
            # Load NAT table for each request
            nat_table = load_nat_table()
            # Receive DNS requests
            data, addr = sock.recvfrom(512)
            # Process each request
            handle_request(data, addr, sock, nat_table)
    except KeyboardInterrupt:
        # Graceful shutdown on keyboard interrupt
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    main()
