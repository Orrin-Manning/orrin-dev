# Machine Learning Learning project

## Goals
- Understand fundamental ML concepts
- Practice with real datasets
- Implement algorithms from scratch and with libraries

## Topics to Cover
- [ ] Linear regression
- [ ] Classification (logistic regression, decision trees)
- [ ] Neural networks basics
- [ ] Model evaluation and validation

## Setup

### Local Development
```bash
# Install dependencies
uv sync

# Run development server
uv run fastapi dev app/main.py
```

### Docker Development
```bash
# Development mode (hot reload on port 8000)
docker compose --profile dev up

# Production mode (nginx on port 80)
docker compose --profile prod up --build
```

See [CLAUDE.md](CLAUDE.md) for detailed documentation.
