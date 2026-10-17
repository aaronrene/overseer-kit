"""Owner-authorized single pinned PyPI artifact acquisition; no installation."""
import hashlib
import json
from pathlib import Path
import ssl
import sys
import urllib.parse
import urllib.request

DEST = Path(__file__).resolve().parent
URL = 'https://pypi.org/pypi/cffi/2.1.0/json'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError('redirect refused')

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect(),
    urllib.request.HTTPSHandler(context=ssl.create_default_context()))

def read(url, host, maximum):
    p = urllib.parse.urlsplit(url)
    assert p.scheme == 'https' and p.hostname == host and p.port in (None, 443)
    assert p.username is None and p.password is None and not p.fragment
    with opener.open(urllib.request.Request(url, headers={'User-Agent': 'Overseer-local-acceptance/1'}), timeout=45) as r:
        data = r.read(maximum + 1)
        assert len(data) <= maximum
        return data, {'status': r.status, 'url': r.url, 'headers': dict(r.headers)}

report = {'kind': 'Pinned prerequisite acquisition only', 'metadata_url': URL}
try:
    data, response = read(URL, 'pypi.org', 4 * 1024 * 1024)
    metadata = json.loads(data)
    assert metadata['info']['name'].lower() == 'cffi' and metadata['info']['version'] == '2.1.0'
    (DEST / 'cffi-2.1.0-pypi.json').write_bytes(data)
    report['metadata_response'] = response
    candidates = [r for r in metadata['urls'] if r['packagetype'] == 'bdist_wheel'
                  and r['filename'].startswith('cffi-2.1.0-cp311-cp311-macosx_')
                  and r['filename'].endswith('_arm64.whl') and not r.get('yanked')]
    report['compatible_candidates'] = candidates
    assert len(candidates) == 1, 'expected one macOS arm64 cp311 wheel'
    selected = candidates[0]
    report['selected'] = selected
    wheel, response = read(selected['url'], 'files.pythonhosted.org', 8 * 1024 * 1024)
    actual = hashlib.sha256(wheel).hexdigest()
    assert actual == selected['digests']['sha256'] and len(wheel) == selected['size']
    with (DEST / selected['filename']).open('xb') as f:
        f.write(wheel)
    report.update(ok=True, artifact_response=response, verified_sha256=actual,
                  artifact=str(DEST / selected['filename']))
except Exception as exc:
    report.update(ok=False, error=repr(exc))
finally:
    output = DEST / ('acquisition-' + str(len(list(DEST.glob('acquisition-*.json'))) + 1) + '.json')
    output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report.get(k) for k in ('ok', 'artifact', 'verified_sha256', 'error')}, indent=2))
sys.exit(0 if report['ok'] else 1)
