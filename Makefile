test-backend:
	python -m unittest discover -s backend/tests -p "*.py"

test-frontend:
	cd frontend/src && npx tsc --noEmit && npm run lint # TODO: Add actual test runner and string it together

test-all: test-backend test-frontend
