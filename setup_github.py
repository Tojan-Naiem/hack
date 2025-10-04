#!/usr/bin/env python3
"""
GitHub Repository Setup Script
Automates the process of creating and pushing to GitHub repository
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_git_status():
    """Check if we're in a git repository and on the correct branch"""
    print("🔍 Checking git status...")
    
    # Check if we're in a git repository
    result = run_command("git status", "Checking git repository status")
    if result is None:
        print("❌ Not in a git repository. Please run 'git init' first.")
        return False
    
    # Check current branch
    result = run_command("git branch --show-current", "Checking current branch")
    if result and "quantum-computing-integration" in result:
        print("✅ On quantum-computing-integration branch")
        return True
    else:
        print("⚠️  Not on quantum-computing-integration branch")
        return False

def add_and_commit_files():
    """Add and commit all files"""
    print("📁 Adding files to git...")
    
    # Add all files
    result = run_command("git add .", "Adding all files to staging")
    if result is None:
        return False
    
    # Check if there are changes to commit
    result = run_command("git status --porcelain", "Checking for changes")
    if not result or not result.strip():
        print("ℹ️  No changes to commit")
        return True
    
    # Commit changes
    result = run_command(
        'git commit -m "Add comprehensive workflow documentation and GitHub setup"',
        "Committing changes"
    )
    return result is not None

def setup_remote_repository():
    """Guide user through remote repository setup"""
    print("\n🌐 GitHub Repository Setup")
    print("=" * 50)
    
    print("📋 Manual Steps Required:")
    print("1. Go to https://github.com and create a new repository")
    print("2. Name it 'asteroid-defense-quantum'")
    print("3. Do NOT initialize with README, .gitignore, or license")
    print("4. Copy the repository URL")
    
    # Get repository URL from user
    repo_url = input("\n🔗 Enter your GitHub repository URL: ").strip()
    
    if not repo_url:
        print("❌ No repository URL provided")
        return False
    
    # Add remote origin
    result = run_command(f"git remote add origin {repo_url}", "Adding remote repository")
    if result is None:
        # Try removing existing remote first
        run_command("git remote remove origin", "Removing existing remote")
        result = run_command(f"git remote add origin {repo_url}", "Adding remote repository")
    
    return result is not None

def push_to_github():
    """Push the branch to GitHub"""
    print("\n🚀 Pushing to GitHub...")
    
    # Push the branch
    result = run_command(
        "git push -u origin quantum-computing-integration",
        "Pushing quantum-computing-integration branch to GitHub"
    )
    
    if result is None:
        print("❌ Failed to push to GitHub")
        print("💡 Common solutions:")
        print("   - Check your GitHub credentials")
        print("   - Make sure the repository exists")
        print("   - Try using a personal access token")
        return False
    
    print("✅ Successfully pushed to GitHub!")
    return True

def create_main_branch():
    """Create and push main branch"""
    print("\n🌿 Creating main branch...")
    
    # Create main branch from current branch
    result = run_command("git checkout -b main", "Creating main branch")
    if result is None:
        return False
    
    # Push main branch
    result = run_command("git push -u origin main", "Pushing main branch to GitHub")
    return result is not None

def main():
    """Main setup function"""
    print("🚀 Asteroid Defense Quantum Computing - GitHub Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app/quantum_optimizer.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check git status
    if not check_git_status():
        print("❌ Git setup issues. Please resolve and try again.")
        sys.exit(1)
    
    # Add and commit files
    if not add_and_commit_files():
        print("❌ Failed to commit files")
        sys.exit(1)
    
    # Setup remote repository
    if not setup_remote_repository():
        print("❌ Failed to setup remote repository")
        sys.exit(1)
    
    # Push to GitHub
    if not push_to_github():
        print("❌ Failed to push to GitHub")
        sys.exit(1)
    
    # Ask if user wants to create main branch
    create_main = input("\n❓ Do you want to create a main branch? (y/n): ").strip().lower()
    if create_main == 'y':
        if create_main_branch():
            print("✅ Main branch created and pushed successfully!")
        else:
            print("⚠️  Failed to create main branch, but quantum branch is uploaded")
    
    print("\n🎉 Setup Complete!")
    print("=" * 30)
    print("✅ All files uploaded to GitHub")
    print("✅ Repository ready for presentation")
    print("✅ Documentation included")
    print("\n📋 Next steps:")
    print("1. Verify files on GitHub")
    print("2. Update repository description")
    print("3. Add collaborators if needed")
    print("4. Present to committee!")

if __name__ == "__main__":
    main()
