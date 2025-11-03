# Running the Project on Windows

To run this project and enable PDF generation (WeasyPrint), the main native dependency is Pango, provided by MSYS2. All Python dependencies are handled by `uv`.

## 1. Install MSYS2 and Pango Dependencies
1. **Download and install MSYS2** from [msys2.org](https://www.msys2.org/).
   - **It is strongly recommended to install MSYS2 in the default location**:
     `C:\msys64`
2. Open the **MSYS2 MINGW64 Shell** and run:
   ```bash
   pacman -S mingw-w64-x86_64-pango
   ```
   This installs Pango and its required libraries for WeasyPrint.

## 2. Python Environment and Project Dependencies
- This project uses [`uv`](https://github.com/astral-sh/uv) to install and manage Python dependencies from `pyproject.toml` and `uv.lock`.
- `uv sync` will create a virtual environment automatically if one does not already exist (in `.venv` by default).

**Installation:**
```bash
uv sync
```

## 3. Run Your Project

```bash
make run
```

## 4. Load Test Data

```bash
make create-test-data
```

Loads sample data from `tests/data/*.csv` into the database.

## Development and Contributing

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features

### Contributing Workflow

1. Branch from `develop`:
   ```bash
   git checkout -b feature/your-feature-name develop
   ```

2. Create PR targeting `develop` branch

## Release Process

1. Merge `develop` → `main`:

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
