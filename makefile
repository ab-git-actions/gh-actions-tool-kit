setup-env:
	@echo "🧪 Setting up development environment..."
	python -m pip install --upgrade pip
	pip install -e .[dev]
	@echo "✅ Environment ready."

run-pytest:
	@echo "🧪 Running unit tests..."
	pytest --cov-report xml:coverage.xml --cov=. --cov-report=term-missing tests --junitxml=report.xml
	@echo "✅ Unit tests completed."
