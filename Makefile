# Stryde Development Commands

.PHONY: help install-backend install-frontend start-backend start-frontend start-all test-backend test-frontend clean

help:
	@echo "Available commands:"
	@echo "  install-backend  - Install Python dependencies"
	@echo "  install-frontend - Install Node.js dependencies"
	@echo "  start-backend    - Start backend server (port 8000)"
	@echo "  start-frontend   - Start frontend server (port 5173)"
	@echo "  start-all        - Start both backend and frontend"
	@echo "  test-backend     - Run backend unit tests"
	@echo "  test-frontend    - Run frontend unit tests"
	@echo "  test-all         - Run all unit tests"
	@echo "  test-integration - Test running endpoints"
	@echo "  clean            - Clean up processes"

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && python3 -m venv venv
	cd backend && source venv/bin/activate && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

start-backend:
	@echo "Starting backend server..."
	cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

start-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

start-all:
	@echo "Starting both servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:5173"
	@echo "Press Ctrl+C to stop both"
	@trap 'kill %1 %2' INT; \
	cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000 & \
	cd frontend && npm run dev & \
	wait

test-backend:
	@echo "Running backend tests..."
	@cd backend && source venv/bin/activate && python -m pytest tests/ -v

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm run test:run

test-all: test-backend test-frontend
	@echo "✅ All tests completed!"

test-integration:
	@echo "Testing backend endpoints..."
	@curl -s http://localhost:8000/ping | grep -q "pong" && echo "✅ Backend ping: OK" || echo "❌ Backend ping: FAILED"
	@curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend docs: OK" || echo "❌ Backend docs: FAILED"
	@echo "Testing frontend..."
	@curl -s http://localhost:5173 > /dev/null && echo "✅ Frontend: OK" || echo "❌ Frontend: FAILED"

clean:
	@echo "Cleaning up processes..."
	@pkill -f "uvicorn main:app" || true
	@pkill -f "vite" || true
	@echo "✅ Cleanup complete"
