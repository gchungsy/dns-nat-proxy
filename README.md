# dns-nat-proxy

## Overview

A client sends a DNS request to the DNS-NAT-Proxy. The DNS server checks if it recognizes the requested DNS zone. If not, it forwards the request to a default DNS server and returns the response to the client. If the DNS server is familiar with the DNS zone, it forwards the request to the associated DNS resolver. If the DNS response includes a subnet found in the Network Address Translation (NAT) table, it undergoes modification before being sent back to the client.

## Features

- **Add NAT Rule**: Define new NAT mappings for DNS zones.
- **Update Resolver**: Assign or update resolver IPs for DNS zones.
- **Delete NAT Rule**: Remove specific NAT mappings from the DNS zone.
- **Delete DNS Zone**: Completely remove a DNS zone and its associated configurations.

## Configuration

The `dns_nat_table.json` file serves as the  configuration input for the tool, defining the DNS zones, resolver IPs, and NAT mappings.

## Getting Started

1. Clone the repository.
2. Install dependencies: `pip3 install -r requirements.txt`.
3. Run the Flask app: `python app.py`.
4. Open the web interface in a browser.

## Docker Deployment

The tool is also available as a Docker container for ease of deployment and is accessible at `docker pull ghcr.io/thenetautomationquy/dns-nat-proxy:latest`.

## Webinterface (http://localhost:8080)

![Alt text](webinterface.png?raw=true "Title")
