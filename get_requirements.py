import pytoml as toml

with open('pyproject.toml', 'r') as f:
    data = toml.load(f)['tool']['poetry']

reqs = []
for dep in data['dependencies']:
    reqs.append(f'{dep}=={data["dependencies"][dep][1:]}')

with open('requirements.txt', 'w') as f:
    print('\n'.join(reqs), file=f)
