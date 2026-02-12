"""Setup script to install dependencies and configure Playwright."""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        return False


def main():
    """Setup the toolkit."""
    print("🚀 Setting up AI Toolkit...")
    
    # Install Python requirements
    success = run_command(
        f'"{sys.executable}" -m pip install -r requirements.txt',
        "Installing Python packages"
    )
    
    if not success:
        print("\n❌ Failed to install Python packages")
        return False
    
    # Install Playwright browsers
    success = run_command(
        f'"{sys.executable}" -m playwright install chromium',
        "Installing Playwright browsers"
    )
    
    if not success:
        print("\n❌ Failed to install Playwright browsers")
        return False
    
    print("\n" + "="*60)
    print("✅ Setup completed successfully!")
    print("="*60)
    print("\n📖 Quick Start:")
    print("  Web Search:        python main.py search \"your query\"")
    print("  Generate Image:    python main.py generate-image \"image description\"")
    print("  Analyze Website:   python main.py analyze-website https://example.com")
    print("\n💡 For more options, use: python main.py --help")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
