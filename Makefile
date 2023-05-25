.PHONY: freeze-requirements dev run

freeze-requirements:
	pip freeze > requirements.txt

dev:
	nodemon --exec "python3" bot/main.py

run:
	python3 bot/main.py
