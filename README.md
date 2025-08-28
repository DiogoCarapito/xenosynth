# xenosynth

[![Github Actions Workflow](https://github.com/DiogoCarapito/xenosynth/actions/workflows/main.yaml/badge.svg)](https://github.com/DiogoCarapito/xenosynth/actions/workflows/main.yaml)

raspberry pi based digital synth to explore xentonal tones and scales

Python version: 3.12

## cheat sheet

### setup

copy all files (folders, hidden and non-hidden files) to the higher directory
usefull if you clone the repo into your desired directory
ignore if clone and after change the name of the directory

```bash
mv python_project_template/{*,.*} . && rm -r python_project_template/
```

### venv

create venv

```bash
python3.12 -m venv .venv
```

activate venv

```bash
source .venv/bin/activate
```
