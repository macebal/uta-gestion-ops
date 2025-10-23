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

**Typical installation commands:**
```powershell
# Optionally create and/or activate your project's folder
cd your-project-folder

# Install all project dependencies (creates .venv if it does not exist)
uv sync

# Activate the virtual environment if needed:
.\.venv\Scripts\activate
```

## 3. Run Your Project
Just run `uv run main.py`
