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
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
# edit templates.txt to add the templates for the messages to send
./eid <facebook username> prepare
# edit to_be_sent.csv file to make sure everything is ok
./eid <facebook username> send
```

## Licence

MIT
