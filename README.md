# Netherite Pickaxe

![image](https://github.com/user-attachments/assets/8422a2cb-3b90-4be1-b37d-c7e854de3a22)

This script searches for specified keywords within a Git repository, including both file contents and commit messages. It supports searching in both local and remote repositories and provides options for exact matches.

The name comes from the git method used in searching logs [Docs](https://git-scm.com/book/en/v2/Git-Tools-Searching), being that the idea of this is to search git repos extensively, it is more of a netherite pickaxe.

This can also be used to search files in a normal directory thats not a git folder, using the --not-repo flag set. 

## Installation

To use this script, ensure you have the following prerequisites:

- Python 3.x
- GitPython library

You can install the required library using pip:

```bash
pip install GitPython
```

## Usage

```bash
python netherite-pickaxe.py <repo_path> [-s, --substring] [-l, --long-format] [-i, --include-all] [-n, --not-repo]
```

## Arguments

- `<repo_path>`: Path to the Git repository or URL of the remote repository.
  
## Options

- `-s, --substring`: Search for exact keyword matches instead of substrings.
- `-l, --long-format`: Don't print out messages if no matches are found.
- `-i, --include-all`: Dont exclude file extensions specified in config.py.
- `-n --not-repo`: Will do a file search only, for non git initialised folder directorys.
- `-h --help`: Get help.

## Examples

- **Local Repository:**
  
  ```bash
  python netherite-pickaxe /path/to/local/repo
  ```

- **Remote Repository:**

  ```bash
  python netherite-pickaxe https://github.com/user/repo.git
  ```
- **Not Git Local Directory:**

  ```bash
  python netherite-pickaxe /path/to/folder --not-repo
  ```

