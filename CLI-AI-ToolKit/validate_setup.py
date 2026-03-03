#!/usr/bin/env python3
"""Setup validation script to check API keys and dependencies."""

import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = Path(__file__).parent / ".env"
    
    print("[*] Checking .env file...")
    if not env_path.exists():
        print("[X] .env file not found")
        print(f"   Location: {env_path}")
        print("   Copy from .env.example first!")
        return False
    
    print(f"[OK] .env file found: {env_path}")
    
    with open(env_path) as f:
        content = f.read()
    
    # Check for required keys
    valid = True
    
    if "OPENAI_API_KEY" not in content:
        print("[!] OPENAI_API_KEY not found in .env")
        valid = False
    else:
        lines = [l for l in content.split('\n') if l.startswith('OPENAI_API_KEY')]
        if lines:
            key_line = lines[0]
            if "your_openai_api_key" in key_line.lower() or "=" not in key_line:
                print("[!] OPENAI_API_KEY appears to be a placeholder")
                valid = False
            else:
                print("[OK] OPENAI_API_KEY is configured")
    
    return valid

def check_imports():
    """Check if required packages are installed."""
    print("\n[*] Checking required packages...")
    
    required = [
        "openai",
        "playwright",
        "ddgs",
        "requests",
        "dotenv"
    ]
    
    all_ok = True
    for pkg in required:
        try:
            if pkg == "dotenv":
                from dotenv import load_dotenv
                print(f"[OK] {pkg}")
            else:
                __import__(pkg)
                print(f"[OK] {pkg}")
        except ImportError as e:
            print(f"[X] {pkg} - {e}")
            all_ok = False
    
    return all_ok

def check_api_key_format():
    """Validate API key format."""
    print("\n[*] Validating API key formats...")
    
    from pathlib import Path
    from dotenv import load_dotenv
    import os
    
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return False
    
    load_dotenv(env_path)
    
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    valid = True
    
    if not openai_key or openai_key.startswith("your_"):
        print("[X] OPENAI_API_KEY is invalid or placeholder")
        print("   Get a key from: https://platform.openai.com/api-keys")
        valid = False
    elif openai_key.startswith("sk-"):
        print(f"[OK] OPENAI_API_KEY format looks valid (starts with 'sk-')")
    else:
        print("[!] OPENAI_API_KEY has unexpected format (should start with 'sk-')")
    
    return valid

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("CLI-AI-ToolKit Setup Validator")
    print("=" * 60)
    
    checks = [
        ("Environment File", check_env_file),
        ("Package Imports", check_imports),
        ("API Key Format", check_api_key_format),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"[!] Error during {name} check: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "[OK] PASS" if passed else "[X] FAIL"
        print(f"{status} - {name}")
    
    if all(results.values()):
        print("\n[SUCCESS] All checks passed! Your toolkit is ready to use.")
        print("\nTry running:")
        print("  python main.py search 'what is AI?'")
        print("  python main.py generate-image 'a futuristic city'")
        print("  python main.py analyze-website 'http://localhost:8000/'")
        return 0
    else:
        print("\n[!] Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Copy .env.example to .env")
        print("2. Add valid API key from:")
        print("   - OpenAI: https://platform.openai.com/api-keys")
        print("3. Run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
