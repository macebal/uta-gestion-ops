# Contributing

Thank you for your interest in contributing to this project!

## Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features

## Contributing Workflow

1. Branch from `develop`:
   ```bash
   git checkout -b feature/your-feature-name develop
   ```

2. Create PR targeting `develop` branch

## Release Process

1. Merge `develop` → `main`

2. Tag and push (use semantic versioning):
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. Build artifact:
   ```bash
   make package
   ```

4. Upload `dist/uta-gestion-ops-<version>.zip` to GitHub Releases

## Development Setup

For instructions on setting up your local development environment, please see [DEVELOPMENT.md](DEVELOPMENT.md).

