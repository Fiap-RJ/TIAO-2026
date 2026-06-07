.PHONY: install run clean copy

install:
	poetry install

run:
	poetry run python main.py

clean:
	rm -f output/context_data.json

copy:
	cp output/context_data.json ../backend/context_data.json
	@echo "✅ context_data.json copiado para o backend"
