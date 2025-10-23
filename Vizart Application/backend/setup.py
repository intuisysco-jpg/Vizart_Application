"""
Setup script for Vizart AI Backend
"""

import os
import subprocess
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "static/uploads",
        "static/results",
        "models",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False
    return True

def download_models():
    """Download pre-trained AI models"""
    print("Downloading AI models...")
    models_dir = Path("models")

    # Create models directory if it doesn't exist
    models_dir.mkdir(exist_ok=True)

    # For now, we'll skip model downloads as they're quite large
    # In a real implementation, you would download models from a CDN
    print("⚠ Model downloads skipped in setup. Models will be downloaded on first use.")

def setup_database():
    """Setup database tables"""
    print("Setting up database...")
    try:
        # This would typically involve running database migrations
        # For now, we'll just note that database setup is required
        print("⚠ Database setup required. Please ensure PostgreSQL is running.")
        return True
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_template = Path(".env.example")

    if not env_file.exists() and env_template.exists():
        print("Creating .env file from template...")
        with open(env_template, 'r') as template:
            content = template.read()

        with open(env_file, 'w') as env:
            env.write(content)

        print("✓ Created .env file")
        print("⚠ Please edit .env file with your configuration")
    else:
        print("✓ .env file already exists or template missing")

def main():
    """Main setup function"""
    print("🚀 Setting up Vizart AI Backend...")
    print("=" * 50)

    # Create directories
    create_directories()
    print()

    # Create .env file
    create_env_file()
    print()

    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during requirements installation")
        return 1

    print()

    # Download models
    download_models()
    print()

    # Setup database
    if not setup_database():
        print("❌ Setup failed during database setup")
        return 1

    print("=" * 50)
    print("✅ Setup completed successfully!")
    print()
    print("Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Ensure PostgreSQL and Redis are running")
    print("3. Run: uvicorn main:app --reload")
    print("4. Visit: http://localhost:8000/docs")

    return 0

if __name__ == "__main__":
    sys.exit(main())