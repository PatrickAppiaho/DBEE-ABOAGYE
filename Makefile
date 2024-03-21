.PHONY: install-actions
install-actions:
	pip install -r requirements.txt

.PHONY: run
run:
	python main.py