# PowerShell script to set up virtual environment for Eco-Backend

Write-Host "Setting up Eco-Backend Virtual Environment..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env file from template
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env file with your API keys and database configuration." -ForegroundColor Cyan
} else {
    Write-Host ".env file already exists." -ForegroundColor Yellow
}

# Create src directory if it doesn't exist
if (!(Test-Path "src")) {
    New-Item -ItemType Directory -Path "src"
    Write-Host "Created src directory." -ForegroundColor Yellow
}

Write-Host "`nSetup completed successfully! 🎉" -ForegroundColor Green
Write-Host "`nTo activate the virtual environment in the future, run:" -ForegroundColor Cyan
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "`nTo deactivate, run:" -ForegroundColor Cyan
Write-Host "deactivate" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your Google API key" -ForegroundColor White
Write-Host "2. Install MongoDB locally or use MongoDB Atlas" -ForegroundColor White
Write-Host "3. Run the test script: python src/test_workflow.py" -ForegroundColor White
