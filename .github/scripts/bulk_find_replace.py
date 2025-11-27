#!/usr/bin/env python3
"""
Bulk find and replace script for GitHub organization repositories.
Replaces:
- hybrid-cloud-patterns.io -> validatedpatterns.io (except in apiVersion lines)
- mailto: references -> team-validatedpatterns
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from github import Github
from github.GithubException import GithubException


def clone_repo(repo_url, temp_dir):
    """Clone a repository to a temporary directory."""
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    clone_path = os.path.join(temp_dir, repo_name)
    
    if os.path.exists(clone_path):
        subprocess.run(['rm', '-rf', clone_path], check=True)
    
    subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
    return clone_path


def should_process_file(file_path):
    """Determine if a file should be processed."""
    # Skip binary files and common non-text files
    skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.pdf',
                      '.zip', '.tar', '.gz', '.bz2', '.woff', '.woff2', '.ttf',
                      '.eot', '.otf', '.mp4', '.mp3', '.avi', '.mov'}
    
    # Skip common directories
    skip_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__',
                '.pytest_cache', 'dist', 'build', '.tox', '.eggs'}
    
    file_path_str = str(file_path)
    
    # Check if in skip directory
    for skip_dir in skip_dirs:
        if f'/{skip_dir}/' in file_path_str or file_path_str.startswith(skip_dir):
            return False
    
    # Check extension
    if any(file_path_str.lower().endswith(ext) for ext in skip_extensions):
        return False
    
    return True


def replace_in_file(file_path, dry_run=False):
    """Replace patterns in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Replace hybrid-cloud-patterns.io with validatedpatterns.io
        # But skip lines that contain apiVersion: hybrid-cloud-patterns.io
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            original_line = line
            
            # Skip apiVersion lines
            if re.search(r'apiVersion:\s*hybrid-cloud-patterns\.io', line, re.IGNORECASE):
                new_lines.append(line)
                continue
            
            # Replace hybrid-cloud-patterns.io with validatedpatterns.io
            if 'hybrid-cloud-patterns.io' in line:
                line = line.replace('hybrid-cloud-patterns.io', 'validatedpatterns.io')
                changes_made = True
            
            # Replace mailto: references
            # Pattern: mailto:something@domain -> mailto:team-validatedpatterns
            # Skip if already mailto:team-validatedpatterns
            mailto_pattern = r'mailto:([^\s<>"\'\)]+)'
            if re.search(mailto_pattern, line, re.IGNORECASE):
                # Check if it's already team-validatedpatterns
                if not re.search(r'mailto:team-validatedpatterns', line, re.IGNORECASE):
                    line = re.sub(mailto_pattern, 'mailto:team-validatedpatterns', line, flags=re.IGNORECASE)
                    if line != original_line:
                        changes_made = True
            
            new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        if changes_made and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        elif changes_made:
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def process_repository(repo_path, dry_run=False):
    """Process all files in a repository."""
    changes = []
    
    for root, dirs, files in os.walk(repo_path):
        # Remove .git from dirs to avoid processing it
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            file_path = Path(root) / file
            
            if not should_process_file(file_path):
                continue
            
            if replace_in_file(file_path, dry_run):
                changes.append(str(file_path.relative_to(repo_path)))
    
    return changes


def get_default_branch(repo_path):
    """Get the default branch name for the repository."""
    try:
        result = subprocess.run(['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'], 
                              cwd=repo_path, capture_output=True, text=True, check=True)
        default_branch = result.stdout.strip().replace('refs/remotes/origin/', '')
        return default_branch
    except subprocess.CalledProcessError:
        # Try common branch names
        for branch in ['main', 'master', 'develop']:
            result = subprocess.run(['git', 'show-ref', f'refs/remotes/origin/{branch}'],
                                  cwd=repo_path, capture_output=True)
            if result.returncode == 0:
                return branch
        return 'main'  # Default fallback


def create_branch_and_pr(repo, repo_path, changes, dry_run=False):
    """Create a branch, commit changes, and open a PR."""
    if not changes:
        print(f"No changes needed in {repo.name}")
        return None
    
    branch_name = 'bulk-find-replace-update'
    default_branch = get_default_branch(repo_path)
    
    try:
        # Check if branch already exists
        try:
            existing_branch = repo.get_branch(branch_name)
            if existing_branch:
                print(f"Branch {branch_name} already exists in {repo.name}, skipping")
                return None
        except GithubException:
            pass  # Branch doesn't exist, which is what we want
        
        if dry_run:
            print(f"[DRY RUN] Would create branch and PR for {repo.name} with {len(changes)} changed files")
            return None
        
        # Ensure we're on the default branch
        subprocess.run(['git', 'checkout', default_branch], cwd=repo_path, check=True)
        
        # Create and checkout branch
        subprocess.run(['git', 'checkout', '-b', branch_name], cwd=repo_path, check=True)
        
        # Stage all changes
        subprocess.run(['git', 'add', '-A'], cwd=repo_path, check=True)
        
        # Check if there are any changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo_path)
        if result.returncode == 0:
            print(f"No changes to commit in {repo.name}")
            subprocess.run(['git', 'checkout', default_branch], cwd=repo_path)
            return None
        
        # Commit changes
        commit_message = """Bulk find and replace: hybrid-cloud-patterns.io -> validatedpatterns.io

- Replaced hybrid-cloud-patterns.io with validatedpatterns.io (excluding apiVersion references)
- Updated mailto: references to team-validatedpatterns

This PR was automatically generated by the bulk find and replace workflow."""
        
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=repo_path, check=True)
        
        # Push branch
        subprocess.run(['git', 'push', 'origin', branch_name], cwd=repo_path, check=True)
        
        # Create PR
        pr_title = "Bulk find and replace: hybrid-cloud-patterns.io -> validatedpatterns.io"
        pr_body = f"""This PR updates references from `hybrid-cloud-patterns.io` to `validatedpatterns.io` and updates mailto references.

**Changes:**
- Replaced `hybrid-cloud-patterns.io` with `validatedpatterns.io` (excluding `apiVersion` references)
- Updated `mailto:` references to `team-validatedpatterns`

**Files changed:** {len(changes)}

This PR was automatically generated by the bulk find and replace workflow."""
        
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base=default_branch
        )
        
        print(f"Created PR #{pr.number} in {repo.name}: {pr.html_url}")
        return pr
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating branch/PR for {repo.name}: {e}")
        return None
    except GithubException as e:
        print(f"GitHub API error for {repo.name}: {e}")
        return None


def main():
    github_token = os.environ.get('GITHUB_TOKEN')
    organization = os.environ.get('ORGANIZATION')
    repositories_input = os.environ.get('REPOSITORIES', '').strip()
    dry_run = os.environ.get('DRY_RUN', 'false').lower() == 'true'
    
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    if not organization:
        print("Error: ORGANIZATION environment variable is required")
        sys.exit(1)
    
    g = Github(github_token)
    org = g.get_organization(organization)
    
    # Parse repository list if provided
    selected_repos = None
    if repositories_input:
        selected_repos = [r.strip() for r in repositories_input.split(',') if r.strip()]
        print(f"Processing selected repositories: {', '.join(selected_repos)}")
    else:
        print(f"Processing all repositories in organization: {organization}")
    
    print(f"Dry run mode: {dry_run}")
    
    temp_dir = '/tmp/bulk_find_replace'
    os.makedirs(temp_dir, exist_ok=True)
    
    repos_processed = 0
    repos_with_changes = 0
    prs_created = 0
    repos_skipped = 0
    found_repos = set()
    
    try:
        for repo in org.get_repos():
            # Filter by selected repositories if provided
            if selected_repos:
                if repo.name not in selected_repos:
                    repos_skipped += 1
                    continue
                found_repos.add(repo.name)
            repos_processed += 1
            print(f"\n[{repos_processed}] Processing {repo.name}...")
            
            # Skip archived repositories
            if repo.archived:
                print(f"  Skipping archived repository")
                continue
            
            # Skip empty repositories
            if repo.size == 0:
                print(f"  Skipping empty repository")
                continue
            
            try:
                # Clone repository
                repo_path = clone_repo(repo.clone_url, temp_dir)
                
                # Configure git user for commits
                subprocess.run(['git', 'config', 'user.name', 'github-actions[bot]'], 
                             cwd=repo_path, check=True)
                subprocess.run(['git', 'config', 'user.email', 
                             'github-actions[bot]@users.noreply.github.com'], 
                             cwd=repo_path, check=True)
                
                # Process files
                changes = process_repository(repo_path, dry_run)
                
                if changes:
                    repos_with_changes += 1
                    print(f"  Found {len(changes)} files with changes")
                    
                    # Create branch and PR
                    pr = create_branch_and_pr(repo, repo_path, changes, dry_run)
                    if pr:
                        prs_created += 1
                else:
                    print(f"  No changes needed")
                    
            except Exception as e:
                print(f"  Error processing {repo.name}: {e}")
                continue
    
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            subprocess.run(['rm', '-rf', temp_dir], check=False)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Repositories processed: {repos_processed}")
    if selected_repos:
        print(f"  Repositories skipped (not in selection): {repos_skipped}")
        not_found = set(selected_repos) - found_repos
        if not_found:
            print(f"  WARNING: Selected repositories not found: {', '.join(sorted(not_found))}")
    print(f"  Repositories with changes: {repos_with_changes}")
    print(f"  PRs created: {prs_created}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

