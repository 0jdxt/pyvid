import pytoml as toml

with open('pyproject.toml', 'r') as f:
    data = toml.load(f)['tool']['poetry']

reqs = []
for dep in data['dependencies']:
    reqs.append(dep + '==' + data['dependencies'][dep][1:])

with open('requirements.txt', 'w') as f:
    print('\n'.join(reqs), file=f)


dreqs = []
for ddep in data['dev-dependencies']:
    dreqs.append(ddep + '==' + data['dev-dependencies'][ddep][1:])

with open('requirements-dev.txt', 'w') as f:
    print('\n'.join(dreqs), file=f)
