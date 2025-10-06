#!/bin/bash

# Stryde Development Helper Script

case "$1" in
  "install")
    echo "Installing all dependencies..."
    make install-backend
    make install-frontend
    ;;
  "start")
    echo "Starting both servers..."
    make start-all
    ;;
  "backend")
    echo "Starting backend only..."
    make start-backend
    ;;
  "frontend")
    echo "Starting frontend only..."
    make start-frontend
    ;;
  "test")
    echo "Running unit tests..."
    make test-all
    ;;
  "test-integration")
    echo "Testing running endpoints..."
    make test-integration
    ;;
  "clean")
    echo "Cleaning up..."
    make clean
    ;;
  *)
    echo "Usage: ./dev.sh [install|start|backend|frontend|test|test-integration|clean]"
    echo ""
    echo "Commands:"
    echo "  install         - Install all dependencies"
    echo "  start           - Start both servers"
    echo "  backend         - Start backend only"
    echo "  frontend        - Start frontend only"
    echo "  test            - Run unit tests"
    echo "  test-integration - Test running endpoints"
    echo "  clean           - Stop all servers"
    ;;
esac
