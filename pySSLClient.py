if __name__ == '__main__':
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('port', type=int, nargs='?')
    ap.add_argument('host', type=str, default='127.0.0.1', nargs='?')
    ap.add_argument('--key', default='server.key', type=str)
    ap.add_argument('--crt', default='server.crt', type=str)
    ns = ap.parse_args()

    import socket
    s = socket.socket()
    s.connect((ns.host, ns.port))

    import ssl
    s = ssl.wrap_socket(s, keyfile=ns.key, certfile=ns.crt,
                        ssl_version=ssl.PROTOCOL_TLSv1)
    s.write("GET / HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % ns.host)

    import sys
    num_bytes = 0
    try:
        while True:
            d = s.recv(2048)
            num_bytes += len(d)
            sys.stdout.write(d)
    finally:
        print "TOTAL BYTES =", num_bytes
