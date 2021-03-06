#!/usr/bin/env python3
import sys
import os
import re
import json


FILES_TO_UPDATE = (
    'src/karmen_frontend/package.json',
    'src/karmen_frontend/package-lock.json',
    'src/karmen_backend/server/__init__.py',
    'src/fakeprinter/fakeprinter/__init__.py',
    'docs/source/conf.py',
)

def update_json(version, pathname):
    with open(pathname, 'r+') as fp:
        data = json.load(fp)
        data['version'] = version
        fp.seek(0)
        fp.truncate()
        json.dump(data, fp, indent=2)

def update_py(version, pathname):
    with open(pathname, 'r+') as fp:
        data = fp.read()
        data = re.sub(r'^(__version__\s*=\s*)(\'|").+(\2)', r'\1"%s"' % version, data, 0, re.MULTILINE)
        fp.seek(0)
        fp.truncate()
        fp.write(data)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python make-version.py 1.2.3')
        sys.exit(1)
    version = sys.argv[1]
    print("Updating to version '%s'." % version)
    for filepath in FILES_TO_UPDATE:
        print('... %s' % filepath)
        if filepath.endswith('.py'):
            update_py(version, filepath)
        elif filepath.endswith('.json'):
            update_json(version, filepath)
        else:
            raise ValueError("Invalid file extension '%s'." % filepath)
    print('''Done.

    Don't forget to:

    git commit %(files)s -m 'version raised to %(version)s'
    git tag %(version)s
    ''' % {
        'version':version,
        'files': '\\\n        '.join(FILES_TO_UPDATE),
        })
