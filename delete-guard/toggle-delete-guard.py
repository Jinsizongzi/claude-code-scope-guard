"""Toggle the delete-confirmation rules in ~/.claude/settings.json.

Usage: python toggle-delete-guard.py on|off|status
The rule list lives in ~/.claude/delete-guard.json. Other ask rules are kept.
"""
import json
import pathlib
import shutil
import sys

HOME = pathlib.Path.home() / '.claude'
SETTINGS = HOME / 'settings.json'
RULES = HOME / 'delete-guard.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'status'
    rules = load(RULES)
    settings = load(SETTINGS)
    perms = settings.setdefault('permissions', {})
    ask = perms.get('ask', [])
    extras = [r for r in ask if r not in rules]
    active = sum(r in ask for r in rules)

    if mode == 'status':
        state = 'ON' if active == len(rules) else ('OFF' if active == 0 else 'PARTIAL')
        print(f'delete guard: {state} ({active}/{len(rules)} rules active)')
        return
    if mode not in ('on', 'off'):
        sys.exit('usage: toggle-delete-guard.py on|off|status')

    perms['ask'] = (rules + extras) if mode == 'on' else extras
    shutil.copyfile(SETTINGS, SETTINGS.with_suffix('.json.bak'))
    tmp = SETTINGS.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    tmp.replace(SETTINGS)
    print(f'delete guard: {mode.upper()} ({len(rules) if mode == "on" else 0}/{len(rules)} rules active)')


if __name__ == '__main__':
    main()
