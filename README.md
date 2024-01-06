# dns-nat-proxy

## Overview

This tool is designed to manage NAT rules and DNS resolvers for a DNS proxy service. It provides an easy-to-use web interface for configuring, updating, and deleting NAT mappings and resolver IP addresses.

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

## Webinterface

![Alt text](webinterface.png?raw=true "Title")