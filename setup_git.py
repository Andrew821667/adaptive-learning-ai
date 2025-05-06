import os
import subprocess
import argparse

def run_command(command):
    """Запускает команду и выводит результат."""
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def setup_git(repo_name, github_token):
    """Настраивает Git и отправляет код на GitHub."""
    # Проверка наличия Git
    if not run_command("git --version"):
        print("Git is not installed or not in PATH.")
        return False
    
    # Инициализация Git
    if not run_command("git init"):
        print("Failed to initialize Git repository.")
        return False
    
    # Добавление файлов
    if not run_command("git add ."):
        print("Failed to add files to Git.")
        return False
    
    # Создание первого коммита
    if not run_command('git commit -m "Initial commit"'):
        print("Failed to create initial commit.")
        return False
    
    # Добавление удаленного репозитория
    remote_url = f"https://{github_token}@github.com/{github_token.split(':')[0]}/{repo_name}.git"
    if not run_command(f"git remote add origin {remote_url}"):
        print("Failed to add remote repository.")
        return False
    
    # Отправка кода на GitHub
    if not run_command("git push -u origin master"):
        print("Failed to push code to GitHub.")
        return False
    
    print(f"Successfully pushed code to GitHub repository: {repo_name}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Git and push to GitHub")
    parser.add_argument("repo_name", help="Name of the GitHub repository")
    parser.add_argument("github_token", help="GitHub token for authentication (username:token)")
    
    args = parser.parse_args()
    setup_git(args.repo_name, args.github_token)
