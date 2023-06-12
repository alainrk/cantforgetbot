.PHONY: freeze-requirements dev run

freeze-requirements:
	pip freeze > requirements.txt

dev-bot:
	nodemon --exec "python3" app/main.py --bot-server

dev-reminders:
	nodemon --exec "python3" app/main.py --reminders-server

run-bot:
	python3 app/main.py --bot-server

run-reminders:
	python3 app/main.py --reminders-server
