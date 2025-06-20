# pmod

Python Extended Module

Focus on simplicity, speed and safety.

## Use

```sh
pip install git+https://github.com/andypangaribuan/pmod@v0.0.22
```

or using requirements.txt

```text
pmod @ git+https://github.com/andypangaribuan/pmod@v0.0.22
```

## When error occurs

```sh
pip install psycopg2-binary
```

## Debug

```sh
On VSCode > Python: Select Interpreter

python -m venv .venv
source .venv/bin/activate
pip install -r ./requirements.txt

printf "%s %s\n" "ipykernel :" "$(pip show ipykernel | grep Version | sed 's/Version: //g')"
pip install 'ipykernel==6.29.5' --force-reinstall
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/andypangaribuan/pmod/tags).

## Contributions

Feel free to contribute to this project.

If you find a bug or want a feature, but don't know how to fix/implement it, please fill an [`issue`](https://github.com/andypangaribuan/pmod/issues).  
If you fixed a bug or implemented a feature, please send a [`pull request`](https://github.com/andypangaribuan/pmod/pulls).

## MIT License

Copyright (c) 2025 Andy Pangaribuan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
