import sys
import http.server
import socketserver
import threading
import config
import db


''' Test HTTPD '''


HTTPD_OPTIONS = ('127.0.0.1', 8080)

class Handler(http.server.BaseHTTPRequestHandler):
    """ HTTP Requests """
    def do_GET(self):
        """ GET Method """
        query_params = self.path.split('=')[1]
        ts = query_params
        payload = [payload for _, payload in db.query_json_path(ts, f'$.NOTIFICATION.{config.INVERTER_ID}', None)]
        data = payload[0].encode()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(data)


class TCPServerThread(threading.Thread):
    """ Thread for http server """
    def run(self):
        """ Start server """
        with socketserver.TCPServer((HTTPD_OPTIONS), Handler, False) as httpd:
            httpd.allow_reuse_address = True
            httpd.server_bind()
            httpd.server_activate()
            httpd.serve_forever()


print('Starting http server thread', HTTPD_OPTIONS)
t = TCPServerThread()
t.daemon = True
try:
    t.start()
    t.join()
except (KeyboardInterrupt, SystemExit):
    print('HTTPD exiting...')
    raise
finally:
    sys.exit(0)
