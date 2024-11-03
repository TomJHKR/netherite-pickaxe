import git
import os
from os import listdir
from os.path import isfile, join
import sys
import argparse
import tempfile
import shutil
import subprocess
from config import excluded_extensions, keywords, important_filenames


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

def search_filenames(repo, not_repo):
    found = False
    files_to_search = []
    if not not_repo:
        files_to_search = [file for file in repo.git.ls_files().splitlines()]
    else:
        files_to_search = [file for file in sub_file_search]
    for filepath in files_to_search:
        if filepath.split("/")[-1] in important_filenames:
            print(colour_print(colour_print(f"IMPORTANT FILE:Current WDIR: {filepath}", red),negative))
            found = True

def search_filenames_in_diff(repo):
    main_repo_path = repo.working_dir  # Assuming main repo path is the repo's working directory
    for commit in repo.iter_commits():
        # Check for the keyword in the commit diff
        diff_data = commit.diff(create_patch=True)
        for diff in diff_data:
            if diff_data:
                file_path = diff.a_path
                if file_path:
                    if file_path.split("/")[-1] in important_filenames:
                        print(colour_print(colour_print(f"IMPORTANT FILE:{commit.hexsha[:7]}: {file_path}", red),negative))
                        found = True
    return found

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


def search_in_commit_diffs(repo, keyword, sub=False):
    found = False
    main_repo_path = repo.working_dir  # Assuming main repo path is the repo's working directory
    differences = []
    for commit in repo.iter_commits():
        # Check for the keyword in the commit diff
        diff_data = commit.diff(create_patch=True)
        diff_text = "\n".join([diff.diff.decode('utf-8', errors='ignore') for diff in diff_data])
        diff_match = (not sub and keyword in diff_text.split()) or (sub and keyword in diff_text)

            # Process each line in diff and only print if not in the main repo's path
        if diff_match:
            for diff in diff_data:
                file_path = diff.a_path
                if file_path and (not file_path.startswith(main_repo_path)):  # Ensure path is outside main repo
                    for linenumber, line in enumerate(diff.diff.decode('utf-8', errors='ignore').splitlines(), start=1):
                        if (not sub and keyword in line.split()) or (sub and keyword in line):
                            highlighted_line = highlight_text(line, keyword, green)
                            if f"{file_path}{linenumber}{line}" in differences:
                                continue
                            if not found:
                                print(colour_print("Found in commit diffs:", yellow))
                                found = True
                            print(f"{file_path}:{colour_print(commit.hexsha[:7], light_white)}:{colour_print(linenumber,light_red)}:{highlighted_line.strip()}")
                            differences.append(f"{file_path}{linenumber}{line}")
    return found


def search_branch_diff(repo, keyword, sub=False, include_all=False):
    remote_refs = repo.remote().refs
    for refs in remote_refs:
        commit_feature = repo.head.commit.tree
        commit_origin_dev = repo.commit(refs)
        new_files = []
        deleted_files = []
        modified_files = []

        # Compare diffs
        diff_index = commit_origin_dev.diff(commit_feature)

        # Collect and search new files
        for file in diff_index.iter_change_type('A'):
            if include_file(file.b_path, include_all):
                new_files.append(file)
                search_in_diff(file, keyword, "new", refs, sub)

        # Collect and search deleted files
        for file in diff_index.iter_change_type('D'):
            if include_file(file.a_path, include_all):
                deleted_files.append(file)
                search_in_diff(file, keyword, "deleted", refs, sub)

        # Collect and search modified files
        for file in diff_index.iter_change_type('M'):
            if include_file(file.a_path, include_all):
                modified_files.append(file)
                search_in_diff(file, keyword, "modified", refs, sub)

def include_file(file_path, include_all):
    # Returns True if the file should be included based on extension criteria
    return include_all or not any(file_path.endswith(ext) for ext in excluded_extensions)

def search_in_diff(file, keyword, change_type, branch,sub=False):
    found = False
    try:
        # Get lines based on file type (new, deleted, or modified)
        if change_type in ["new", "deleted"]:
            # Check if data is already a string or if decoding is needed
            if isinstance(file.b_blob.data_stream.read(), bytes):
                lines = file.b_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines()
            else:
                lines = file.b_blob.data_stream.read().splitlines()
        else:
            # Check if diff content is a string or bytes
            if isinstance(file.diff, bytes):
                lines = file.diff.decode('utf-8', errors='ignore').splitlines()
            else:
                lines = file.diff.splitlines()

        # Iterate through lines to find keyword
        for line_number, line in enumerate(lines, start=1):
            if (not sub and keyword in line.split()) or (sub and keyword in line):
                if not found:
                    print(colour_print(f"Branch: {colour_print(branch, red)} - Found in {change_type} file:", yellow))
                found = True
                highlighted_line = highlight_text(line, keyword, green)
                print(f"{colour_print(file.a_path, light_white)}:{colour_print(line_number, light_red)}: {highlighted_line.strip()}")
    except Exception as e:
        print(f"Error processing {file.a_path if file.a_path else file.b_path}: {e}")

def gitlog_search(repo, keyword, sub=False, include_all=False):
    return ""

def get_files_recursive(path):
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            get_files_recursive(full_path)
        else:
            sub_file_search.append(full_path)
            print(full_path)

def main(repo_path, single_keyword, substring, long, include, not_repo,deep):
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
        assign_keywords = keywords
        if single_keyword:
            assign_keywords.clear()
            assign_keywords.append(single_keyword)
        if not_repo:
            get_files_recursive(repo_path)

        print("")
        search_filenames(repo, not_repo)
        if deep and not not_repo:
            search_filenames_in_diff(repo)
        for keyword in assign_keywords:
            print(f"Searching for keyword: {colour_print(colour_print(keyword, blue),negative)}")
            file_search = search_in_files(repo, keyword, substring, include, not_repo)
            if not file_search and long:
                print(colour_print("Nothing found in files", red))
            if not not_repo:
                commit_mesage = search_in_commit_messages(repo, keyword, substring)
                if long and not commit_mesage:
                    print(colour_print("Nothing found in commit messages", red))
                if deep:
                    commit_search = search_in_commit_diffs(repo, keyword, substring)
                    if long and not commit_search:
                        print(colour_print("Nothing found in commit diffs", red))
                search_branch_diff(repo,keyword,substring,include)
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
    print("     python netherite-pickaxe <repo_path> [-S, --single-keyword <keyword>] [-s, --substring] [-l, --long-format] [-i, --include-all] [-n, --not-repo] [-h, --help] [-d, --deep-search]")
    print()
    print(colour_print("Arguments:", blue))
    print("     <repo_path>  Path to the file containing repo or remote repo - see examples.")
    print("     -s, --single-keyword <keyword>  Single keyword to search for.")
    print()
    print(colour_print("Options:", blue))
    print("     -S, --single-keyword    Search for a single keyword.")
    print("     -s, --substring         Search for substring keyword matches instead of exact.")
    print("     -l, --long-format       Print out messages showing no matches are found.")
    print("     -i, --include-all       Dont exclude file extensions specified in config.py.")
    print("     -n, --not-repo          Will do a file search only, for non git initialised folder directorys.")
    print("     -d, --deep-search       Searches super in depth including all commits and differences, can be quite slow.")
    print("     -h, --help              Display usage.")
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
    parser.add_argument("-S","--single-keyword", required=False, help="use single keyword to search", type=str)
    parser.add_argument("-s","--substring", action="store_true", help="Search for substring keyword matches instead of exact.")
    parser.add_argument("-l","--long-format", action="store_true", help="Dont print out messages if no matches are found.")
    parser.add_argument("-i","--include-all", action="store_true", help="Dont exclude file extensions specified in config.py.")
    parser.add_argument("-n","--not-repo", action="store_true", help="Search directory for keywords that isnt a git folder.")
    parser.add_argument("-d","--deep-search", action="store_true", help="Search diffs aswell for a long indepth search.")
    args = parser.parse_args()

    # Run the main function with the provided arguments
    main(args.repo_path, args.single_keyword, args.substring, args.long_format, args.include_all, args.not_repo, args.deep_search)

