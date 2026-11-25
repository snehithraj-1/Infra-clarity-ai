.PHONY: dev backend frontend test test-backend test-frontend clean

dev:
	@echo "Starting InfraClarity AI Backend & Frontend..."
	@powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd backend; ..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000'; cd frontend; npm run dev"

backend:
	cd backend && ..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test: test-backend test-frontend

test-backend:
	cd backend && ..\.venv\Scripts\python -m pytest tests/ -v

test-frontend:
	cd frontend && npm run test

clean:
	@powershell -Command "Remove-Item -Recurse -Force backend/data/jobs/* -ErrorAction SilentlyContinue"
