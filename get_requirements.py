#!usr/bin/env python
# called by pre-commmit hook
import pytoml as toml

with open("pyproject.toml", "r") as f:
    data = toml.load(f)["tool"]["poetry"]

deps = {**data["dependencies"], **data["dev-dependencies"]}
with open("requirements.txt", "w") as f:
    for dep, ver in deps.items():
        print(f"{dep}=={ver[1:]}", file=f)
