"""Generic ComfyUI request adapter, rewritten for the reduced Demo.

Contains no production graph, model settings, prompts or asset naming rules.
"""
import argparse
import copy
import json
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def bind_workflow(workflow, bindings, values):
    if not isinstance(workflow, dict) or not workflow:
        raise ValueError('workflow must be a nonempty node dictionary')
    if set(bindings) != set(values):
        raise ValueError('bindings and values must have the same parameter names')
    result = copy.deepcopy(workflow)
    for name, targets in bindings.items():
        if not isinstance(targets, list) or not targets:
            raise ValueError(f'no targets for {name}')
        for target in targets:
            node_id, input_name = target['node'], target['input']
            if node_id not in result or input_name not in result[node_id].get('inputs', {}):
                raise ValueError(f'missing node/input for {name}')
            result[node_id]['inputs'][input_name] = copy.deepcopy(values[name])
    return result


class ComfyClient:
    def __init__(self, base_url, request_timeout=10):
        parsed = urllib.parse.urlsplit(base_url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            raise ValueError('an HTTP(S) service URL is required')
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('credentials, queries and fragments do not belong in the service URL')
        self.base = base_url.rstrip('/')
        self.request_timeout = request_timeout
        # The local demo does not forward loopback requests to an environment proxy.
        self.opener = (urllib.request.build_opener(urllib.request.ProxyHandler({}))
                       if parsed.hostname in ('127.0.0.1', 'localhost', '::1')
                       else urllib.request.build_opener())

    def _request(self, path, body=None, timeout=None):
        data = None if body is None else json.dumps(body).encode('utf-8')
        request = urllib.request.Request(self.base + path, data=data,
                                         headers={'Content-Type': 'application/json'})
        with self.opener.open(request, timeout=timeout or self.request_timeout) as response:
            payload = json.load(response)
        if not isinstance(payload, dict):
            raise RuntimeError('invalid service response')
        return payload

    def submit(self, workflow):
        # No automatic POST retry: a lost response is not proof the job was rejected.
        result = self._request('/prompt', {'prompt': workflow, 'client_id': str(uuid.uuid4())})
        job_id = result.get('prompt_id')
        if not isinstance(job_id, str) or not job_id:
            raise RuntimeError('submission did not return a job ID')
        return job_id

    def wait(self, job_id, timeout=30, interval=0.1):
        if timeout <= 0 or interval <= 0:
            raise ValueError('timeout and interval must be positive')
        deadline = time.monotonic() + timeout
        path = '/history/' + urllib.parse.quote(job_id, safe='')
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f'job {job_id} timed out')
            response = self._request(path, timeout=min(self.request_timeout, remaining))
            entry = response.get(job_id)
            if entry:
                status = entry.get('status', {}).get('status_str')
                if status == 'error':
                    raise RuntimeError(f'job {job_id} failed')
                if status == 'success':
                    return {'job_id': job_id, 'outputs': entry.get('outputs', {})}
            time.sleep(min(interval, max(0, deadline - time.monotonic())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workflow', 'bindings', 'values'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--submit', action='store_true')
    parser.add_argument('--api-base')
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args()
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    workflow = bind_workflow(read(args.workflow), read(args.bindings), read(args.values))
    if not args.submit:
        print(json.dumps({'mode': 'plan-only', 'node_count': len(workflow),
                          'workflow': workflow}, ensure_ascii=False, indent=2))
        return
    if any(str(node.get('class_type', '')).startswith('Demo') for node in workflow.values()):
        parser.error('mock nodes cannot be submitted to a real service; supply your own graph')
    if not args.api_base:
        parser.error('--api-base is required for submission')
    client = ComfyClient(args.api_base)
    job_id = client.submit(workflow)
    print(json.dumps({'job_id': job_id, 'state': 'submitted'}), flush=True)
    print(json.dumps(client.wait(job_id, timeout=args.timeout), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
