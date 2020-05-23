# Eid

A python tool to send personalized eid congratulations

## Supported platforms

- [x] Facebook messenger
- [ ] Telegram
- [ ] Whatsapp

## Installation

```sh
git clone https://github.com/mie00/eid
cd eid
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
# edit templates.txt to add the templates for the messages to send
./eid.py <facebook username> prepare
# edit to_be_sent.csv file to make sure everything is ok
./eid.py <facebook username> send
```

## Licence

MIT
