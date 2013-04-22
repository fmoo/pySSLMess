if __name__ == '__main__':

    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('port', type=int, default=0, nargs='?')
    ap.add_argument('host', type=str, default='127.0.0.1', nargs='?')
    ap.add_argument('--key', default='server.key', type=str)
    ap.add_argument('--crt', default='server.crt', type=str)
    ns = ap.parse_args()

    import socket
    s = socket.socket()
    s.bind((ns.host, ns.port))
    print s.getsockname()

    RUNNING = True

    from OpenSSL import crypto, SSL
    def verify(conn, cert, errnum, errdepth, ok):
        print "== verify =="
        print "conn =", conn
        print "cert =", cert
        print "errnum = %s (%d)" % \
            (crypto.X509_verify_cert_error_string(errnum), errnum)
        print "errdepth =", errdepth
        print "ok =", ok
        return 1


    def handler(sock):
        ctx = SSL.Context(SSL.TLSv1_METHOD)
        ctx.use_privatekey_file(ns.key)
        ctx.use_certificate_file(ns.crt)
        ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT |
                       SSL.VERIFY_CLIENT_ONCE, verify)
        #cacert = crypto.load_certificate(crypto.FILETYPE_PEM, open("CA/cacert.pem").read())
        #ctx.add_client_ca(cacert)
        ctx.load_verify_locations("CA/cacert.pem")
        conn = SSL.Connection(ctx, sock)
        print conn.get_cipher_list()
        conn.set_accept_state()
        conn.do_handshake()
        conn.send("Hello world\n")
        conn.close()

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
