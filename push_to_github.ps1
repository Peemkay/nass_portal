# Check if git is initialized
if (-not (Test-Path -Path ".git")) {
    Write-Host "Initializing git repository..."
    git init
}

# Configure git if needed
$userEmail = git config --get user.email
if (-not $userEmail) {
    Write-Host "Configuring git user email..."
    git config --global user.email "chakin700@yahoo.com"
}

$userName = git config --get user.name
if (-not $userName) {
    Write-Host "Configuring git user name..."
    git config --global user.name "Nigerian Army School of Signals"
}

# Add all files to staging
Write-Host "Adding files to staging..."
git add .

# Commit changes
Write-Host "Committing changes..."
git commit -m "Fixed maintenance mode functionality"

# Check if remote origin exists
$remoteExists = git remote -v | Select-String -Pattern "origin"
if (-not $remoteExists) {
    Write-Host "Adding GitHub remote..."
    $repoUrl = Read-Host -Prompt "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git)"
    git remote add origin $repoUrl
}

# Get the current branch name
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    $currentBranch = "main"
}

# Push to GitHub
Write-Host "Pushing to GitHub on branch $currentBranch..."
git push -u origin $currentBranch

Write-Host "Done!"
