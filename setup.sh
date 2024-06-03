#!/bin/bash
rm -Rf .venv/
python -m venv .venv
source .venv/bin/activate
pip install pygame pillow pytz requests python-dotenv
python main.py