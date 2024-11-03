import git
import os
import sys
import argparse
import tempfile
import shutil
from config import excluded_extensions, keywords


red = "\033[91m"
green = "\033[32m"
end = "\033[0m"
blue = "\033[34m"
bold = "\033[1m"
yellow = '\033[93m'
dark_gray = "\033[90m"
light_gray = "\033[37m"


def highlight_text(text, keyword, colour):
    ## Highlights the keyword in the text with ANSI red color codes
    return text.replace(keyword, f"{colour}{keyword}{end}")

def colour_print(text,colour):
    return f"{colour}{text}{end}"

def search_in_files(repo, keyword, exact_match=False):
    ## Searches for the keyword in the content of files tracked by Git
    found = False
    files_to_search = [file for file in repo.git.ls_files().splitlines() 
                       if not any(file.endswith(ext) for ext in excluded_extensions)]
    for file_path in files_to_search:
        with open(os.path.join(repo.working_dir, file_path), 'r', encoding='utf-8', errors='ignore') as file:
            for line_number, line in enumerate(file, start=1):
                if (exact_match and keyword in line.split()) or (not exact_match and keyword in line):
                    if not found:
                        print(colour_print("\nFound in file contents:",yellow))
                    found = True
                    highlighted_line = highlight_text(line, keyword, green)
                    print(f"{file_path}:{line_number}: {highlighted_line.strip()}")
    return found

def search_in_commit_messages(repo, keyword, exact_match=False):
    ## Searches for the keyword in commit messages.
    found = False
    for commit in repo.iter_commits():
        if (exact_match and keyword in commit.message.split()) or (not exact_match and keyword in commit.message):
            if not found:
                print(colour_print("\nFound in commit messages:",yellow))
            found = True
            highlighted_message = highlight_text(commit.message, keyword, green)
            print(f"Commit {commit.hexsha[:7]}: {highlighted_message.strip()}")
    return found

def main(repo_path, exact_match, long=False):
    usage()
    # Determine if `repo_path` is a URL (remote repo) or a local path
    is_remote = repo_path.startswith("http://") or repo_path.startswith("https://") or repo_path.startswith("git@")
    
    if is_remote:
        # Clone the remote repo to a temporary directory
        temp_dir = tempfile.mkdtemp()
        print(f"Cloning remote repository to temporary directory: {temp_dir}")
        repo = git.Repo.clone_from(repo_path, temp_dir)
    else:
        # Use the local repository path
        repo = git.Repo(repo_path)


    # Perform searches for each keyword
    try:
        for keyword in keywords:
            print(f"Searching for keyword: {colour_print(keyword, blue)}")
            file_search = search_in_files(repo, keyword, exact_match)
            if not file_search and long:
                print(colour_print("Nothing found in files", red))
            commit_search = search_in_commit_messages(repo, keyword, exact_match)
            if not commit_search and long:
                print(colour_print("Nothing found in commit messages", red))
    finally:
        # Clean up the temporary directory if cloned
        if is_remote:
            shutil.rmtree(temp_dir)
            print(f"Deleted temporary directory: {temp_dir}")

def usage():
    ascii_art = """⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣀⡿⠿⠿⠿⠿⠿⠿⢿⣀⣀⣀⣀⣀⡀⠀⠀
⠀⠀⠀⠀⠀⠀⠸⠿⣇⣀⣀⣀⣀⣀⣀⣸⠿⢿⣿⣿⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠻⠿⠿⠿⠿⠿⣿⣿⣀⡸⠿⢿⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣿⣿⣿⣧⣤⡼⠿⢧⣤⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣿⣿⣿⣿⠛⢻⣿⡇⠀⢸⣿⡇
⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣿⣿⣿⣿⠛⠛⠀⢸⣿⡇⠀⢸⣿⡇
⠀⠀⠀⠀⠀⠀⢠⣤⣿⣿⣿⣿⠛⠛⠀⠀⠀⢸⣿⡇⠀⢸⣿⡇
⠀⠀⠀⠀⢰⣶⣾⣿⣿⣿⠛⠛⠀⠀⠀⠀⠀⠈⠛⢳⣶⡞⠛⠁
⠀⠀⢰⣶⣾⣿⣿⣿⡏⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠁⠀⠀
⢰⣶⡎⠉⢹⣿⡏⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⣿⣷⣶⡎⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""
    print(ascii_art)
    print(colour_print("Usage:", blue))
    print("python netherite-pickaxe <repo_path> [--exact] [--ignore-null]")
    print()
    print(colour_print("Arguments:", blue))
    print(colour_print("  <keywords_file>  Path to the file containing newline-separated keywords.", green))
    print()
    print(colour_print("Options:", blue))
    print(colour_print("  --exact          Search for exact keyword matches instead of substrings.", green))
    print(colour_print("  --long-format    Dont print out messages if no matches are found.", green))
    print()
    print(colour_print("Examples:", blue))
    print(colour_print("  Local repository:", green))
    print(colour_print("    python netherite-pickaxe.py /path/to/local/repo --exact", green))
    print(colour_print("  Remote repository:", green))
    print(colour_print("    python netherite-pickaxe.py https://github.com/user/repo.git --exact", green))
    print()
    print(colour_print("Description:", blue))
    print(colour_print("  This script searches for keywords in the specified Git repository.", green))
    print(colour_print("  It searches both in file contents and commit messages.", green))


# Set up command-line argument parsing
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    parser = argparse.ArgumentParser(description="Search for keywords in a Git repository.")
    parser.add_argument("repo_path", help="Path to the Git repository or URL of the remote repository")
    parser.add_argument("--exact", action="store_true", help="Search for exact keyword matches instead of substrings.")
    parser.add_argument("--long-format", action="store_true", help="Dont print out messages if no matches are found.")
    args = parser.parse_args()


    # Run the main function with the provided arguments
    main(args.repo_path, args.exact, args.long_format)

