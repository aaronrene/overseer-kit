"""Validate the bounded-v1 informational site and its static content."""
from __future__ import annotations
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import yaml
from tools.landing.schema import load_manifest

RELEASE = 'https://github.com/aaronrene/overseer-kit/releases/tag/v1.0.0-rc.1'
COMMANDS = {'status', 'init', 'sync', 'adopt', 'mirror', 'next', 'next-write'}
SECTIONS = ('hero', 'context', 'how-it-works', 'modes', 'boundaries', 'start')
RETIRED = re.compile(r'\b(?:check-ok|governance-sync|handover-compact|honesty-status|hosted-dashboard|land-closeout|pr-land|upgrade-regime|verify-step)\b|\bok\s+(?:app|ledger|review|route|workspace|hook)\b|status\s+--check-footprint', re.I)
SECRET_PATTERNS = (
    re.compile(r'AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{20,}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'(?i)(?:api[_-]?key|secret|password)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]'),
)
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


@dataclass
class ValidationResult:
    ok: bool = True
    errors: list[str] = field(default_factory=list)

    def add(self, code: str, detail: str) -> None:
        self.ok = False
        self.errors.append(f'{code}: {detail}')


class Page(HTMLParser):
    def __init__(self, path: Path, result: ValidationResult):
        super().__init__(convert_charrefs=True)
        self.path, self.result = path, result
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.stack: list[str] = []
        self.counts: dict[str, int] = {}
        self.lang = self.viewport = False
        self.codes: list[str] = []
        self.code: list[str] | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if tag not in VOID:
            self.stack.append(tag)
        if tag == 'html':
            self.lang = a.get('lang') == 'en'
        if tag == 'meta' and a.get('name') == 'viewport':
            self.viewport = 'width=device-width' in a.get('content', '')
        if 'id' in a:
            if a['id'] in self.ids:
                self.result.add('duplicate_id', f'{self.path.name}: {a["id"]}')
            self.ids.add(a['id'])
        if tag == 'img' and 'alt' not in a:
            self.result.add('image_alt', self.path.name)
        if tag == 'th' and a.get('scope') not in {'row', 'col'}:
            self.result.add('table_scope', self.path.name)
        for key in ('href', 'src'):
            if key in a:
                self.links.append(a[key])
        if tag == 'script' and urlsplit(a.get('src', '')).netloc:
            self.result.add('external_script', self.path.name)
        if tag == 'code':
            self.code = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.result.add('html_structure', f'{self.path.name}: unexpected </{tag}>')
        else:
            self.stack.pop()
        if tag == 'code' and self.code is not None:
            self.codes.append(''.join(self.code))
            self.code = None

    def handle_data(self, data):
        if self.code is not None:
            self.code.append(data)
        if not any(tag in self.stack for tag in ('script', 'style')):
            self.text.append(data)


def validate_landing(kit_root: Path) -> ValidationResult:
    result = ValidationResult()
    landing = (kit_root / 'docs/landing').resolve()
    try:
        manifest = load_manifest(landing / 'manifest.yaml')
    except (OSError, ValueError, yaml.YAMLError) as exc:
        result.add('manifest_parse', str(exc))
        return result
    if manifest.section_ids != SECTIONS:
        result.add('section_contract', str(manifest.section_ids))
    if manifest.primary_download_href != RELEASE:
        result.add('release_target', str(manifest.primary_download_href))
    if manifest.status_badges != {'example'}:
        result.add('scenario_status', 'Scenarios must be labelled examples')
    if manifest.funnel_steps != ('install', 'init', 'status', 'next', 'next-write'):
        result.add('flow', 'Expected the bounded-v1 installation and handoff flow')
    pages = {}
    for rel in ('index.html', 'docs.html', 'scenarios/index.html'):
        path = landing / rel
        if not path.is_file():
            result.add('missing_file', rel)
            continue
        html = path.read_text(encoding='utf-8')
        page = Page(path, result)
        page.feed(html)
        page.close()
        pages[path] = page
        if page.stack or not html.lower().startswith('<!doctype html>'):
            result.add('html_structure', rel)
        if not page.lang or not page.viewport:
            result.add('document_metadata', rel)
        for tag in ('h1', 'main', 'title'):
            if page.counts.get(tag) != 1:
                result.add('landmark', f'{rel}: expected one {tag}')
        if '#main' not in page.links:
            result.add('skip_link', rel)
        text = ' '.join(page.text)
        if 'prerelease' not in text.lower() or 'does not run Overseer' not in text:
            result.add('product_disclosure', rel)
        if RETIRED.search(html) or re.search(r'\.dmg|127\.0\.0\.1|localhost|session_credential', html):
            result.add('retired_surface', rel)
        if re.search(r'\beval\s*\(', html):
            result.add('script_eval', rel)
    for path, page in pages.items():
        for link in page.links:
            u = urlsplit(link)
            if u.scheme or u.netloc:
                if u.scheme != 'https' or not u.netloc or u.username or u.password:
                    result.add('unsafe_link', link)
                continue
            target = (path.parent / unquote(u.path)).resolve() if u.path else path
            if target.is_dir():
                target /= 'index.html'
            if not target.is_relative_to(landing) or not target.is_file():
                result.add('broken_link', f'{path.name}: {link}')
            elif u.fragment and (target not in pages or unquote(u.fragment) not in pages[target].ids):
                result.add('broken_anchor', f'{path.name}: {link}')
    home = pages.get(landing / 'index.html')
    docs = pages.get(landing / 'docs.html')
    scenarios = pages.get(landing / 'scenarios/index.html')
    if home and (not set(SECTIONS).issubset(home.ids) or 'cta-release' not in home.ids or RELEASE not in home.links):
        result.add('home_contract', 'Missing sections or explicit rc.1 release action')
    if docs and not COMMANDS.issubset(set(docs.codes)):
        result.add('commands', 'Docs must list all seven public commands')
    if scenarios and not {f'persona-{p}' for p in manifest.persona_ids}.issubset(scenarios.ids):
        result.add('scenarios', 'Missing example scenario')
    for path in landing.rglob('*'):
        if path.is_file() and path.suffix in {'.html', '.css', '.js', '.svg', '.md', '.yaml'}:
            text = path.read_text(encoding='utf-8')
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                result.add('secret_leak', path.relative_to(landing).as_posix())
            if re.search(r'/Users/|/home/|RECOVERY-RUNS/|overseer-kit-v1-recovery', text):
                result.add('private_path', path.relative_to(landing).as_posix())
    for rel in ('assets/style.css', 'assets/theme.js'):
        if not (landing / rel).is_file():
            result.add('missing_file', rel)
    if not (kit_root / 'LICENSE').is_file() or manifest.license != 'MIT':
        result.add('license', 'Expected repository MIT license')
    if not (kit_root / 'SECURITY.md').is_file():
        result.add('security', 'Missing security policy')
    return result


def main() -> int:
    import sys
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    result = validate_landing(root)
    if not result.ok:
        for error in result.errors:
            print(error, file=sys.stderr)
        return 1
    print('landing: ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
