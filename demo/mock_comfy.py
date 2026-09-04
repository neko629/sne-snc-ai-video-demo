"""Minimal loopback fixture for the ComfyUI API subset used by the Demo.

No model, GPU or real video generation is provided by this fixture.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading


class MockComfy:
    def __enter__(self):
        owner = self
        self.jobs = {}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self, data, status=200):
                encoded = json.dumps(data).encode('utf-8')
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def do_POST(self):
                if self.path != '/prompt':
                    return self.reply({'error': 'unknown endpoint'}, 404)
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                if not isinstance(body.get('prompt'), dict) or not body.get('client_id'):
                    return self.reply({'error': 'invalid payload'}, 400)
                job_id = f'demo-job-{len(owner.jobs) + 1}'
                owner.jobs[job_id] = {'body': body, 'polls': 0}
                return self.reply({'prompt_id': job_id})

            def do_GET(self):
                prefix = '/history/'
                if not self.path.startswith(prefix):
                    return self.reply({'error': 'unknown endpoint'}, 404)
                job_id = self.path[len(prefix):]
                job = owner.jobs.get(job_id)
                if not job:
                    return self.reply({})
                job['polls'] += 1
                behavior = job['body']['prompt']['4']['inputs']['filename_prefix']
                if behavior == 'mock-timeout' or job['polls'] == 1:
                    return self.reply({})
                if behavior == 'mock-fail':
                    return self.reply({job_id: {'status': {'status_str': 'error'}}})
                return self.reply({job_id: {
                    'status': {'status_str': 'success'},
                    'outputs': {'4': {'videos': [{'filename': 'mock-result.mp4',
                                                 'subfolder': 'mock', 'type': 'output'}]}}
                }})

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
