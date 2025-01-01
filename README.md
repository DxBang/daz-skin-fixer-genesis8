# DAZ3D Skin Fixer for Genesis 8 / 8.1 Female (G8F / G8.1F) (and Male (G8M / G8.1M) later)
_by Bang Systems_  

## Introduction
This script is designed to fix the skins of Genesis 8/8.1 Characters from DAZ3D. It can remove navel, genitals, eyebrows, and resize areola on female characters.  

## Installation
### Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python g8f.py "filename.png" --remove:navel --resize:areola --size:0.7
```
