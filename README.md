# Netherite Pickaxe
## Author: Tomjhkr
## For ethical purposes only

![image](https://github.com/user-attachments/assets/8422a2cb-3b90-4be1-b37d-c7e854de3a22)

Often times users will leave information in git repositiorys that shouldnt be included.

This tool is used to audit those accidential additions to ensure that you arent leaking any exploitable inforamation. This could also be used for ethical hacking.

This script can
- Search files for specified keywords within a Git repository, including both file contents and commit messages. It supports searching in both local and remote repositories and provides options for exact matches.
- Search commit messages for keywords
- Keywords are defined in the config.py file
- Exclude certian file formats in the config.py file, for example .png

The name comes from the git method used in searching logs, as seen in the [Docs](https://git-scm.com/book/en/v2/Git-Tools-Searching), being that the idea of this is to search git repos extensively, it is more of a netherite pickaxe.

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
python3 netherite-pickaxe.py <repo_path> [-s, --substring] [-l, --long-format] [-i, --include-all] [-n, --not-repo]
```

## Arguments

- `<repo_path>`: Path to the Git repository or URL of the remote repository.
  
## Options

- `-s, --substring`: Search for exact keyword matches instead of substrings.
- `-l, --long-format`: Print out messages showing no matches are found.
- `-i, --include-all`: Dont exclude file extensions specified in config.py.
- `-n --not-repo`: Will do a file search only, for non git initialised folder directorys.
- `-h --help`: Get help.

## Examples

- **Local Repository:**
  
  ```bash
  python3 netherite-pickaxe.py /path/to/local/repo
  ```

- **Remote Repository:**

This clones the repo into a tempary directory

  ```bash
  python3 netherite-pickaxe.py https://github.com/user/repo.git
  ```
  ```bash
  python3 netherite-pickaxe.py git@github.com:user/rep.git
  ```
- **Not Git Local Directory:**

  ```bash
  python3 netherite-pickaxe.py /path/to/folder --not-repo
  ```

