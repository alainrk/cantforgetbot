# Can't Forget Bot

Spaced repetitions Telegram Bot

## Dev

### Setup

```sh
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Freeze dependencies
pip3 freeze > requirements.txt
```

### Run

```sh
# Run bot
make run

# Live reload server (requires nodemon)
make dev
```
