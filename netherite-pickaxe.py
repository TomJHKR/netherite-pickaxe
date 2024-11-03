import git
import os
from os import listdir
from os.path import isfile, join
import sys
import argparse
import tempfile
import shutil
from config import excluded_extensions, keywords


red = "\033[91m"
green = "\033[32m"
end = "\033[0m"
dark_blue = "\033[0;34m"
blue = "\033[1;34m"
bold = "\033[1m"
yellow = '\033[93m'
dark_gray = "\033[90m"
light_gray = "\033[37m"
negative = "\033[7m"
light_red = "\033[1;31m"
light_green = "\033[1;32m"
light_white = "\033[1;37m"

sub_file_search = []


def highlight_text(text, keyword, colour):
    ## Highlights the keyword in the text with ANSI red color codes
    return text.replace(keyword, f"{colour}{keyword}{end}")

def colour_print(text,colour):
    return f"{colour}{text}{end}"

def search_in_files(repo, keyword, sub=False, include_all=False, not_repo=False):
    ## Searches for the keyword in the content of files tracked by Git
    found = False
    files_to_search = []
    if not not_repo:
        files_to_search = [file for file in repo.git.ls_files().splitlines() 
                       if not any(file.endswith(ext) and not include_all for ext in excluded_extensions)]
    else:
        files_to_search = [file for file in sub_file_search 
                           if not any(file.endswith(ext) and not include_all for ext in excluded_extensions)]
    for file_path in files_to_search:
        with open((os.path.join(repo.working_dir, file_path) if not not_repo else file_path), 'r', encoding='utf-8', errors='ignore') as file:
            for line_number, line in enumerate(file, start=1):
                if (not sub and keyword in line.split()) or (sub and keyword in line):
                    if not found:
                        print(colour_print("Found in file contents:",yellow))
                    found = True
                    highlighted_line = highlight_text(line, keyword, green)
                    print(f"{colour_print(file_path,light_white)}:{colour_print(line_number,light_red)}: {highlighted_line.strip()}")
    return found

def search_in_commit_messages(repo, keyword, sub=False):
    ## Searches for the keyword in commit messages.
    found = False
    for commit in repo.iter_commits():
        if (not sub and keyword in commit.message.split()) or (sub and keyword in commit.message):
            if not found:
                print(colour_print("Found in commit messages:",yellow))
            found = True
            highlighted_message = highlight_text(commit.message, keyword, green)
            print(f"Commit {commit.hexsha[:7]}: {highlighted_message.strip()}")
    return found

def get_files_recursive(path):
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            get_files_recursive(full_path)
        else:
            sub_file_search.append(full_path)
            print(full_path)

def main(repo_path, substring, long, include, not_repo):
    usage()
    # Determine if `repo_path` is a URL (remote repo) or a local path
    is_remote = repo_path.startswith("http://") or repo_path.startswith("https://") or repo_path.startswith("git@")
    if not not_repo:
        if is_remote:
            # Clone the remote repo to a temporary directory
            temp_dir = tempfile.mkdtemp()
            print(f"Cloning remote repository to temporary directory: {temp_dir}")
            repo = git.Repo.clone_from(repo_path, temp_dir)
        else:
            # Use the local repository path
            repo = git.Repo(repo_path)
    else:
        repo = repo_path


    # Perform searches for each keyword
    try:
        if not_repo:
            get_files_recursive(repo_path)
        for keyword in keywords:
            print("")
            print(f"Searching for keyword: {colour_print(colour_print(keyword, blue),negative)}")
            file_search = search_in_files(repo, keyword, substring, include, not_repo)
            if not file_search and long:
                print(colour_print("Nothing found in files", red))
            if not not_repo:
                commit_search = search_in_commit_messages(repo, keyword, substring)
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
    print("     python netherite-pickaxe <repo_path> [-s, --substring] [-l, --long-format] [-i, --include-all] [-n, --not-repo] [-h, --help]")
    print()
    print(colour_print("Arguments:", blue))
    print("     <repo_path>  Path to the file containing repo or remote repo - see examples.")
    print()
    print(colour_print("Options:", blue))
    print("     -s, --substring      Search for substring keyword matches instead of exact.")
    print("     -l, --long-format    Print out messages showing no matches are found.")
    print("     -i, --include-all    Dont exclude file extensions specified in config.py.")
    print("     -n, --not-repo       Will do a file search only, for non git initialised folder directorys.")
    print("     -h, --help           Display usage.")
    print()
    print(colour_print("Examples:", blue))
    print("     Local repository:")
    print("         python netherite-pickaxe.py /path/to/local/repo")
    print("     Remote repository:")
    print("         python netherite-pickaxe.py https://github.com/user/repo.git")
    print()
    print(colour_print("Description:", blue))
    print("     This script searches for keywords in the specified Git repository.")
    print("     It searches both in file contents and commit messages.")
    print("     It can also search standard directorys with the --not-repo flag set.")


# Set up command-line argument parsing
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    parser = argparse.ArgumentParser(description="Search for keywords across git folders or standard folders.")
    parser.add_argument("repo_path", help="Path to the Git repository, URL of the remote repository or local folder")
    parser.add_argument("-s","--substring", action="store_true", help="Search for substring keyword matches instead of exact.")
    parser.add_argument("-l","--long-format", action="store_true", help="Dont print out messages if no matches are found.")
    parser.add_argument("-i","--include-all", action="store_true", help="Dont exclude file extensions specified in config.py.")
    parser.add_argument("-n","--not-repo", action="store_true", help="Search directory for keywords that isnt a git folder.")
    args = parser.parse_args()

    # Run the main function with the provided arguments
    main(args.repo_path, args.substring, args.long_format, args.include_all, args.not_repo)

