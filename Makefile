test-backend:
	python -m unittest discover -s backend/tests -p "*.py"

test-frontend:
	cd frontend && npm test && npx tsc --noEmit && npm run lint

test-all: test-backend test-frontend
