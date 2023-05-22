.PHONY: freeze-requirements

freeze-requirements:
	pip freeze > requirements.txt

dev:
	nodemon --exec "python3" bot/main.py
