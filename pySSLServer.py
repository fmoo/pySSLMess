if __name__ == '__main__':

    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('port', type=int, default=0, nargs='?')
    ap.add_argument('host', type=str, default='127.0.0.1', nargs='?')
    ap.add_argument('--key', default='server.key', type=str)
    ap.add_argument('--crt', default='server.crt', type=str)
    ap.add_argument('--cacrt', default='CA/cacert.pem')
    ns = ap.parse_args()

    import socket
    s = socket.socket()
    s.bind((ns.host, ns.port))
    print s.getsockname()

    RUNNING = True

    import ssl
    def handler(sock):
        sock = ssl.wrap_socket(sock, keyfile=ns.key, certfile=ns.crt,
                               server_side=True, cert_reqs=ssl.CERT_REQUIRED,
                               ssl_version=ssl.PROTOCOL_TLSv1, ca_certs=ns.cacrt)
        print sock.getpeercert()
        sock.send("Hello world\n")
        sock.close()

    def acceptor(sock):
        sock.listen(128)
        while RUNNING:
            conn, peeraddr = sock.accept()
            print peeraddr, "connected"
            t = threading.Thread(target=handler, args=(conn, ))
            t.setDaemon(True)
            t.start()

    import threading
    t = threading.Thread(target=acceptor, args=(s, ))
    t.setDaemon(True)
    t.start()

    try:
        while True:
            t.join()
    finally:
        RUNNING = False
