.PHONY: freeze-requirements dev run

freeze-requirements:
	pip freeze > requirements.txt

dev-bot:
	nodemon --ignore '!app/**' --ignore '__pycache__' --exec "python3" app/main.py --bot-server

dev-reminders:
	nodemon --ignore '!app/**' --ignore '__pycache__' --exec "python3" app/main.py --reminders-server

run-bot:
	python3 app/main.py --bot-server

run-reminders:
	python3 app/main.py --reminders-server

deploy-bot:
	gcloud app deploy --appyaml=app-bot.yaml

deploy-reminders:
	gcloud app deploy --appyaml=app-reminders.yaml

deploy: deploy-bot deploy-reminders
