"""Local standard-library host. UE bridge owns all review operations."""
import json
import secrets
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / 'runtime'
ORIGIN = 'http://127.0.0.1:8746'
TOKEN = secrets.token_urlsafe(32)


def read_status():
    try:
        data = json.loads((RUNTIME / 'status.json').read_text(encoding='utf-8'))
        data['connected'] = time.time() - data['heartbeat'] < 5 and not data.get('error')
        return data
    except (OSError, ValueError, KeyError):
        return {'connected': False, 'error': 'Attach the review panel in Unreal Editor first.'}


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data), encoding='utf-8')
    temp.replace(path)


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data, mime='application/json'):
        body = data.encode('utf-8') if isinstance(data, str) else json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get('Host') != '127.0.0.1:8746':
            return self.reply(403, {'error': 'Use the loopback panel address'})
        if self.path == '/':
            return self.reply(200, (ROOT / 'panel.html').read_text(encoding='utf-8').replace('__TOKEN__', TOKEN), 'text/html')
        if self.path == '/api/status':
            return self.reply(200, read_status())
        if self.path.startswith('/api/result/'):
            key = self.path.rsplit('/', 1)[-1]
            if len(key) != 32 or any(c not in '0123456789abcdef' for c in key):
                return self.reply(400, {'error': 'Invalid command identifier'})
            path = RUNTIME / 'results' / (key + '.json')
            if path.exists():
                return self.reply(200, json.loads(path.read_text(encoding='utf-8')))
            return self.reply(202, {'pending': True})
        self.reply(404, {'error': 'Not found'})

    def do_POST(self):
        if (self.path != '/api/command' or self.headers.get('Origin') != ORIGIN
                or self.headers.get('Host') != '127.0.0.1:8746'
                or self.headers.get('X-Panel-Token') != TOKEN):
            return self.reply(403, {'error': 'Reload the local panel before sending a command'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                raise ValueError('Invalid command size')
            data = json.loads(self.rfile.read(length))
            if data['action'] not in ('open', 'start', 'save', 'finish', 'refresh', 'select', 'view', 'step', 'record', 'accept', 'unresolved', 'track', 'identify'):
                raise ValueError('Unknown action')
            if not read_status().get('connected'):
                raise ValueError('Editor disconnected; attach the panel and refresh')
            key = uuid.uuid4().hex
            command = {k: data[k] for k in ('action', 'args', 'bridge_id', 'character', 'session_id', 'revision')}
            command.update(expires=time.time() + 12)
            atomic(RUNTIME / 'commands' / (key + '.json'), command)
            self.reply(202, {'id': key})
        except (ValueError, KeyError, TypeError) as exc:
            self.reply(400, {'error': str(exc)})

    def log_message(self, fmt, *args):
        # Local usability host, no human evidence or requests copied into logs.
        pass


if __name__ == '__main__':
    RUNTIME.mkdir(exist_ok=True)
    print(ORIGIN, flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8746), Handler).serve_forever()
