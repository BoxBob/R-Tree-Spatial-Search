#!/bin/bash

echo "🚀 Setting up R-tree Spatial Search Engine development environment..."

# Create necessary directories
mkdir -p api frontend database/init database/backups scripts logs

# Start PostgreSQL and Redis
echo "📦 Starting database services..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Generate sample data
echo "📊 Generating sample spatial data..."
python scripts/generate_sample_data.py

echo "✅ Development environment setup complete!"
echo "🔗 Access points:"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo "   - pgAdmin: http://localhost:8080"
