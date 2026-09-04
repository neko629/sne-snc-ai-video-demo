"""Exercise the reduced Skill interfaces with synthetic, nonproduction inputs."""
from pathlib import Path
import copy
import importlib.util
import json
import sys

from mock_comfy import MockComfy

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
OUT = ROOT / 'demo' / 'output'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def expect_error(kind, action):
    try:
        action()
    except kind:
        return
    raise AssertionError(f'expected {kind.__name__}')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    client = load('job_client', SKILLS / 'comfyui-job-demo/scripts/client.py')
    timing = load('subtitle_timing', SKILLS / 'subtitle-timing-demo/scripts/timing.py')
    structure = load('trilingual_check', SKILLS / 'trilingual-structure-demo/scripts/check_structure.py')
    asset = SKILLS / 'comfyui-job-demo/assets'
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    graph = read(asset / 'workflow.mock.json')
    bindings = read(asset / 'bindings.demo.json')
    values = read(asset / 'values.demo.json')
    checks = []

    def check(name, action):
        try:
            action()
            result = {'name': name, 'passed': True}
        except Exception as error:
            result = {'name': name, 'passed': False, 'error': str(error)}
        checks.append(result)
        print(f"{'PASS' if result['passed'] else 'FAIL'} {name}")

    bound = client.bind_workflow(graph, bindings, values)

    def parameter_check():
        require(bound['1']['inputs']['image'] == values['image'], 'image binding missing')
        require(bound['3']['inputs']['noise_seed'] == values['seed'], 'seed binding missing')
        require(graph == read(asset / 'workflow.mock.json'), 'original template was changed')

    check('workflow_bindings_preserve_template', parameter_check)
    damaged_bindings = copy.deepcopy(bindings)
    damaged_bindings['image'][0]['node'] = 'missing'
    check('missing_node_is_rejected', lambda: expect_error(ValueError, lambda:
          client.bind_workflow(graph, damaged_bindings, values)))

    lifecycle = []
    with MockComfy() as server:
        api = client.ComfyClient(server.url)

        def lifecycle_check():
            job_id = api.submit(bound)
            result = api.wait(job_id, timeout=2, interval=0.02)
            require(server.jobs[job_id]['body']['prompt'] == bound, 'submitted payload differs')
            require(server.jobs[job_id]['polls'] >= 2, 'pending state was not exercised')
            require(result['outputs']['4']['videos'][0]['filename'] == 'mock-result.mp4',
                    'output metadata missing')
            lifecycle.append({'state': 'success', 'metadata_only': True, **result})

        check('mock_submit_pending_success', lifecycle_check)

        def failure_check():
            bad = client.bind_workflow(graph, bindings, dict(values, output='mock-fail'))
            job_id = api.submit(bad)
            expect_error(RuntimeError, lambda: api.wait(job_id, timeout=2, interval=0.02))
            lifecycle.append({'job_id': job_id, 'state': 'failure_detected'})

        check('mock_failure_is_reported', failure_check)

        def timeout_check():
            stalled = client.bind_workflow(graph, bindings, dict(values, output='mock-timeout'))
            job_id = api.submit(stalled)
            expect_error(TimeoutError, lambda: api.wait(job_id, timeout=0.15, interval=0.02))
            lifecycle.append({'job_id': job_id, 'state': 'timeout_detected'})

        check('mock_timeout_is_bounded', timeout_check)

    srt = (SKILLS / 'subtitle-timing-demo/assets/example.srt').read_text(encoding='utf-8')
    shifted = timing.shift_srt(srt, 0.75)
    before, after = timing.parse_srt(srt), timing.parse_srt(shifted)
    check('subtitle_offset_applied', lambda: require(
        all(b['start'] - a['start'] == 750 and b['end'] - a['end'] == 750
            for a, b in zip(before, after)), 'timestamp shift is incorrect'))
    check('subtitle_text_preserved', lambda: require(
        [c['text'] for c in before] == [c['text'] for c in after], 'cue text changed'))
    check('reversed_timestamp_rejected', lambda: expect_error(ValueError, lambda:
        timing.parse_srt('1\n00:00:03,000 --> 00:00:02,000\nExample.\n')))

    trilingual = (SKILLS / 'trilingual-structure-demo/assets/example.txt').read_text(encoding='utf-8')
    check('three_line_sample_valid', lambda: require(structure.check(trilingual)['valid'],
                                                   'valid sample rejected'))
    missing_token = trilingual.replace('jīn tiān xià yǔ', 'jīn tiān xià')
    check('missing_pinyin_detected', lambda: require(not structure.check(missing_token)['valid'],
                                                   'missing token not detected'))
    missing_line = trilingual.replace('It is raining today.\n', '')
    check('missing_translation_detected', lambda: require(not structure.check(missing_line)['valid'],
                                                        'missing field not detected'))

    (OUT / 'shifted.srt').write_text(shifted, encoding='utf-8')
    (OUT / 'job_lifecycle.json').write_text(json.dumps(lifecycle, indent=2), encoding='utf-8')
    report = {'scope': 'Reduced demo with synthetic fixtures and a loopback mock service',
              'external_service_calls': False, 'model_inference': False,
              'video_generated': False, 'checks': checks,
              'passed': all(item['passed'] for item in checks)}
    (OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n{sum(c['passed'] for c in checks)}/{len(checks)} checks passed. See demo/output/report.json")
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
