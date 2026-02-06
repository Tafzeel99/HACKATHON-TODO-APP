# Phase 1 - Troubleshooting Guide

## Common Errors and Solutions

### Error 1: "No module named 'src'"

**Error message:**
```
ModuleNotFoundError: No module named 'src'
```

**Cause:** You're not in the correct directory

**Solution:**
```bash
# Navigate to phase1 directory first
cd phase1

# Then run
python -m src.main
```

---

### Error 2: "attempted relative import with no known parent package"

**Error message:**
```
ImportError: attempted relative import with no known parent package
```

**Cause:** Trying to run the file directly instead of as a module

**Wrong:**
```bash
python src/main.py  # ❌ This won't work
cd src && python main.py  # ❌ This won't work either
```

**Correct:**
```bash
cd phase1
python -m src.main  # ✅ This works
```

---

### Error 3: "ModuleNotFoundError: No module named 'colors'"

**Error message:**
```
ModuleNotFoundError: No module named 'colors'
```

**Cause:** Running from wrong directory or running file directly

**Solution:**
```bash
# Make sure you're in phase1 directory
cd /mnt/d/IT\ CLASSES\ pc/HACKATHON-TODO-APP/phase1

# Run as a module
python -m src.main
```

---

### Error 4: Python version too old

**Error message:**
```
SyntaxError: invalid syntax
```

**Cause:** Python version is too old (< 3.8)

**Solution:**
```bash
# Check your Python version
python --version

# Should be Python 3.8 or higher
# If not, install Python 3.13 or use python3
python3 -m src.main
```

---

### Error 5: Permission denied

**Error message:**
```
Permission denied
```

**Cause:** Files don't have execute permissions

**Solution:**
```bash
cd phase1
chmod +x src/*.py
python -m src.main
```

---

## Quick Commands Reference

### From Phase 1 Directory

```bash
# Run the app
python -m src.main

# Run tests
python src/tests/test_app.py
```

### From Project Root

```bash
# Run the app
python -m phase1.src.main

# Run tests
python -m phase1.src.tests.test_app
```

---

## Verification Commands

### Check if you're in the right directory:
```bash
pwd
# Should show: /mnt/d/IT CLASSES pc/HACKATHON-TODO-APP/phase1
```

### Check if src directory exists:
```bash
ls -la src/
# Should show: main.py, cli.py, models.py, task_manager.py, colors.py
```

### Check Python version:
```bash
python --version
# Should be: Python 3.8+ (recommended: Python 3.13)
```

### Check if __init__.py exists:
```bash
ls -la src/__init__.py
# Should exist
```

---

## Still Having Issues?

1. **Make sure you're in the phase1 directory:**
   ```bash
   cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP/phase1"
   ```

2. **Verify all files are present:**
   ```bash
   ls -la src/
   ```

3. **Try running with python3 instead of python:**
   ```bash
   python3 -m src.main
   ```

4. **Check for hidden errors:**
   ```bash
   python -m src.main 2>&1
   ```

---

## Correct Project Structure

Your phase1 directory should look like this:

```
phase1/
├── README.md
├── TROUBLESHOOTING.md
└── src/
    ├── __init__.py          # ← This file is required!
    ├── main.py
    ├── cli.py
    ├── models.py
    ├── task_manager.py
    ├── colors.py
    ├── README.md
    └── tests/
        └── test_app.py
```

If `__init__.py` is missing, create it:
```bash
touch src/__init__.py
```

---

**Need more help? Check the main README.md or CLAUDE.md for additional guidance.**
