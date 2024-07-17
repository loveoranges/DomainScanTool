#!/usr/bin/env python

import binascii
import socket
import random
import os
import argparse
import concurrent.futures

DEFAULT_PORT = 53
VERSION = '2.0'
MAX_CONCURRENT_REQUESTS = 400  # Set the maximum number of concurrent requests
TIMEOUT = 5  # Set the timeout duration (seconds)


def send(message, server, port):
    """
    Sends UDP packet to server and waits for response.

    Args:
        message: Encoded data, which will be sent.
        server: DNS server address. Both IPv4 and IPv6 are supported.
        port: DNS server port.

    Returns:
        A string containing raw response.
    """
    message = message.strip()
    addr = (server, port)

    if '.' in server:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    s.settimeout(TIMEOUT)

    try:
        s.sendto(binascii.unhexlify(message), addr)
        data, address = s.recvfrom(4096)
    except socket.timeout:
        return None  # Return None to indicate timeout
    finally:
        s.close()

    return binascii.hexlify(data).decode()


def build_message(domain):
    """
    Creates a DNS request according to RFC2929. Attributes other than domain name are hard-coded.

    Args:
        domain: The domain name to be checked.

    Returns:
        A string containing raw DNS request.
    """
    message = '{:04x}'.format(random.randint(0, 65535))  # Generate a random request ID
    message += '01000001000000000000'

    addr = domain.split('.')
    for i in addr:
        length = '{:02x}'.format(len(i))
        addr = binascii.hexlify(i.encode())
        message += length
        message += addr.decode()

    message += '0000060001'

    return message


def validate_server(ip, port):
    """
    Checks if the given IP-port combination is valid.

    Args:
        ip: IPv4 or IPv6 address.
        port: Port number.

    Returns:
        A bool value. True for valid and False for invalid.
    """
    if port <= 0 or port > 65535:
        return False

    try:
        if '.' in ip:
            socket.inet_pton(socket.AF_INET, ip)
        else:
            socket.inet_pton(socket.AF_INET6, ip)
    except:
        return False

    return True


def check(domain, server, port):
    """
    Sends the request, reads the raw response, and checks the ANCOUNT attribute according to RFC2929.

    Args:
        domain: Domain name to be checked.
        server: DNS server to check against.
        port: DNS server port.

    Returns:
        A bool value representing if the domain exists.
    """
    message = build_message(domain)
    response = send(message, server, port)
    if response is None:
        return None  # Return None to indicate timeout or error
    rcode = '{:b}'.format(int(response[4:8], 16)).zfill(16)[12:16]
    return False if rcode == '0011' else True


def scan_domain(domain, servers, ports, verbose):
    """
    Scans a single domain against a list of DNS servers and ports.

    Args:
        domain: Domain name to be checked.
        servers: List of DNS servers to check against.
        ports: List of DNS server ports.
        verbose: Boolean flag to indicate if unavailable domains should be shown.

    Returns:
        A tuple containing the domain and its availability.
    """
    for server, port in zip(servers, ports):
        result = check(domain, server, port)
        if result is None:
            continue  # Skip in case of timeout or error
        if not result:
            return domain, True
    if verbose:
        return domain, False
    return domain, None


def main():
    parser = argparse.ArgumentParser(
        description='Domain Scan Tool',
        usage='%(prog)s <dns_servers> <suffixes> <dict_file> <result_file> <verbose>\n'
              'Example: %(prog)s "8.8.8.8:53,1.1.1.1:53" "com,net" dictionary.txt results.txt y \n'
              'Example: %(prog)s 8.8.8.8 com dictionary.txt results.txt n'
    )
    parser.add_argument('dns_servers', help='Comma-separated list of DNS servers (IPv4 or IPv6)')
    parser.add_argument('suffixes', help='Comma-separated list of suffixes to be scanned')
    parser.add_argument('dict_file', help='Path for dictionary file')
    parser.add_argument('result_file', help='Path to save the results')
    parser.add_argument('verbose', choices=['y', 'n'], help='Show unavailable domains [y/N]')

    args = parser.parse_args()

    print('Domain scanning tool version %s' % VERSION)

    servers = []
    ports = []
    dns = args.dns_servers.split(',')
    for item in dns:
        item = item.strip()
        if '[' in item:
            s = item.split(']')[0][1:]
            p = item.split(']')[1][1:] or DEFAULT_PORT
        else:
            s = item.split(':')[0]
            p = item.split(':')[1] if ':' in item else DEFAULT_PORT
        p = int(p)
        if not validate_server(s, p):
            print('Invalid DNS server.')
            return
        servers.append(s)
        ports.append(p)

    tld = args.suffixes.split(',')
    for i, item in enumerate(tld):
        tld[i] = item.strip()

    dict_file = args.dict_file
    if not os.access(dict_file, os.R_OK):
        print('Unable to read dictionary file.')
        return

    result_file = args.result_file
    result = open(result_file, 'a')

    verbose = args.verbose.lower() == 'y'

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
        futures = []
        for line in open(dict_file):
            for suffix in tld:
                domain = line.strip() + '.' + suffix
                futures.append(executor.submit(scan_domain, domain, servers, ports, verbose))

        for future in concurrent.futures.as_completed(futures):
            result_tuple = future.result()
            if result_tuple:
                domain, available = result_tuple
                if available is not None:
                    if available:
                        print(domain + ' is available.')
                        if result:
                            result.write(domain + ' is available.\n')
                    else:
                        print(domain + ' is not available.')
                        if result:
                            result.write(domain + ' is not available.\n')

    print('Scanning finished.')
    result.close()
    print('Results have been saved to ' + result_file + '.')


if __name__ == '__main__':
    main()
