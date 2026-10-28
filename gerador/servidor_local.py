"""Local server for the site: serves the repository and passes the character lookups of "Meu personagem" on to the
official Aion 2 site, which only answers its own pages. The published site does the same through aion2_worker.js.

Run from the repository: py -I gerador/servidor_local.py [port]   (default 5176)
Then open http://127.0.0.1:5176/ . A copy of the page opened as a file also uses this server while it runs."""
import functools
import http.server
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5176
# the only addresses passed on: /aion2/<key>?<query> -> ROUTES[key]?<query>
ROUTES = {
    'search': 'https://api-search.plaync.com/aion2global/search/v2/character',
    'servers': 'https://aion2.plaync.com/en-us/api/gameinfo/servers',
    'info': 'https://aion2.plaync.com/api/character/info',
    'equipment': 'https://aion2.plaync.com/api/character/equipment',
    'item': 'https://aion2.plaync.com/api/character/equipment/item',
    'daevanion': 'https://aion2.plaync.com/api/character/daevanion/detail',
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        if not url.path.startswith('/aion2/'):
            return super().do_GET()
        target = ROUTES.get(url.path[len('/aion2/'):])
        if not target:
            return self.answer(404, b'{"error":"unknown route"}')
        req = urllib.request.Request(target + ('?' + url.query if url.query else ''),
                                     headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                self.answer(r.status, r.read())
        except urllib.error.HTTPError as e:
            self.answer(e.code, e.read())
        except OSError as e:
            self.answer(502, ('{"error":"%s"}' % type(e).__name__).encode())

    def answer(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    print('Atreia Hub em http://127.0.0.1:%d/  (Ctrl+C para parar)' % PORT)
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Handler, directory=ROOT)).serve_forever()
