$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "Wardrobe Wizard project health check" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$failed = $false

function Test-RequiredPath {
    param (
        [string]$Path,
        [string]$Description
    )

    if (Test-Path $Path) {
        Write-Host "[OK] $Description" -ForegroundColor Green
    }
    else {
        Write-Host "[MISSING] $Description" -ForegroundColor Red
        Write-Host "         Expected path: $Path" -ForegroundColor DarkGray
        $script:failed = $true
    }
}

function Test-WarningPath {
    param (
        [string]$Path,
        [string]$Description
    )

    if (Test-Path $Path) {
        Write-Host "[WARNING] $Description" -ForegroundColor Yellow
        Write-Host "          Found path: $Path" -ForegroundColor DarkGray
    }
    else {
        Write-Host "[OK] $Description" -ForegroundColor Green
    }
}

Test-RequiredPath "app.py" "Main Streamlit app exists"
Test-RequiredPath "data/wardrobe.json" "Sample wardrobe dataset exists"
Test-RequiredPath "src/recommendation_engine.py" "Recommendation engine exists"
Test-RequiredPath "src/item_parser.py" "Item parser exists"
Test-RequiredPath "src/ai_client.py" "AI client exists"
Test-RequiredPath "src/photo_analyzer.py" "Photo analyzer exists"
Test-RequiredPath "src/corgi_mascot.py" "Corgi mascot helper exists"
Test-RequiredPath "docs/ai_safety_and_privacy.md" "AI safety and privacy docs exist"
Test-RequiredPath ".streamlit/config.toml" "Streamlit config exists"
Test-RequiredPath "assets/corgi-wizard.png" "Landing screen corgi image exists"
Test-RequiredPath "assets/corgi-mascot-sticker.png" "In-app corgi mascot sticker exists"
Test-RequiredPath "mcp_server/wardrobe_mcp_server.py" "Optional MCP server exists"
Test-RequiredPath "requirements-mcp.txt" "Optional MCP requirements file exists"

Write-Host ""
Write-Host "Checking for local secrets..." -ForegroundColor Cyan

Test-WarningPath ".env" ".env should stay local and must not be committed"
Test-WarningPath ".streamlit/secrets.toml" "Streamlit secrets file should stay local and must not be committed"

Write-Host ""
Write-Host "Running Python syntax checks..." -ForegroundColor Cyan

$pythonFiles = @("app.py")
$pythonFiles += Get-ChildItem -Path "src" -Filter "*.py" | ForEach-Object { $_.FullName }

if (Test-Path "mcp_server/wardrobe_mcp_server.py") {
    $pythonFiles += "mcp_server/wardrobe_mcp_server.py"
}

foreach ($file in $pythonFiles) {
    Write-Host "Checking $file"

    python -m py_compile $file

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAILED] Python syntax check failed for $file" -ForegroundColor Red
        $failed = $true
    }
    else {
        Write-Host "[OK] Python syntax check passed for $file" -ForegroundColor Green
    }
}

Write-Host ""

if ($failed) {
    Write-Host "Project health check finished with problems." -ForegroundColor Red
    exit 1
}
else {
    Write-Host "Project health check passed." -ForegroundColor Green
    exit 0
}