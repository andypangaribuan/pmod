sudo apt update
sudo apt install libpq-dev python3-dev build-essential -y

python -m venv .venv
source .venv/bin/activate
pip install psycopg2-binary
pip install psycopg2
pip install -q -r requirements.txt

"cmd + shift + p" ▶ >Python: Select Interpreter


then select the ./.venv/bin/python
