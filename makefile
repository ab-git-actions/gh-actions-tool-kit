setup-env:
	@echo "🧪 Setting up env..."
	python -m pip install --upgrade pip
	pip install pipenv pytest coverage pytest-cov
	@echo "✅ Setup completed."

run-pytest:
	@echo "🧪 Running unit tests..."
	pipenv run pytest --cov-report xml:coverage.xml --cov=. --cov-report=term-missing tests --junitxml=report.xml
	@echo "✅ Unit tests completed."
