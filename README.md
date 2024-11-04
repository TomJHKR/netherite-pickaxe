# Netherite Pickaxe
## Author: Tomjhkr
## For ethical purposes only

![image](https://github.com/user-attachments/assets/8422a2cb-3b90-4be1-b37d-c7e854de3a22)

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Arguments](#arguments)
5. [Options](#options)
6. [Examples](#examples)
7. [Configuration](#configuration)
8. [How It Works](#how-it-works)
9. [Limitations](#limitations)
10. [Contributing](#contributing)
11. [License](#license)
12. [Acknowledgments](#acknowledgments)

## Overview
The **Netherite Pickaxe** is a powerful tool designed to audit Git repositories for accidental additions that could leak sensitive information. By searching through both file contents and commit messages, this script can help ensure that no exploitable data is included in your repositories.
Often times users will leave information in git repositiorys that shouldnt be included.

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
- 
You can install the required library using pip:

```bash
pip install GitPython
```

To install **Netherite Pickaxe**, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/netherite-pickaxe.git
cd netherite-pickaxe
pip install -r requirements.txt
```

## Usage

```bash
python3 netherite-pickaxe.py <repo_path> [-S, --single-keyword <keyword>] [-s, --substring] [-l, --long-format] [-i, --include-all] [-n, --not-repo]
```

Replace `[repository_path]` with the path to the Git repository you want to audit, and `[keyword]` with the keyword you want to search for if you are not using the default list.

## Arguments

- `<repo_path>`: Path to the Git repository or URL of the remote repository.
- `-S, --single-keyword <keyword>`: Search for a single keyword only.
  
## Options

- `-S, --single-keyword`: Used to search a single keyword rather than using the list.
- `-s, --substring`: Search for exact keyword matches instead of substrings.
- `-l, --long-format`: Print out messages showing no matches are found.
- `-i, --include-all`: Dont exclude file extensions specified in config.py.
- `-n, --not-repo`: Will do a file search only, for non git initialised folder directorys.
- `-d, --deep-search`: Used to perform an extensive search which includes all commits and differences, can take a while.
- `-h, --help`: Get help.

## Examples

- **Local Repository:**
  
  ```bash
  python3 netherite-pickaxe.py /path/to/local/repo
  ```

- **Remote Repository:**
This clones the repo into a temporary directory
  ```bash
  python3 netherite-pickaxe.py https://github.com/user/repo.git
  ```
  ```bash
  python3 netherite-pickaxe.py git@github.com:user/repo.git
  ```
- **Not Git Local Directory:**

  ```bash
  python3 netherite-pickaxe.py /path/to/folder --not-repo
  ```
## Configuration

Before running the script, configure the following settings in the `config.py` file:

- **keywords**: List of keywords to search for in the repository. Modify this list as needed to fit your auditing needs.
- **excluded_extensions**: List of file extensions to exclude from the search (e.g., `.png`, `.jpg`). This helps to filter out non-text files that are unlikely to contain relevant information.
- **important_filenames**: Specific filenames that are considered significant and will be flagged during the search.

  ## How It Works

1. **Keyword Search**: The script scans through files in the repository and commit messages for specified keywords.
2. **File and Commit Analysis**: It can search through the differences in commits to catch keywords that may have been added or removed over time.
3. **Support for Local and Remote Repositories**: The tool supports both local Git repositories and remote repositories (via cloning to a temporary directory).

## Limitations

- The script may not handle large repositories efficiently, especially when performing deep searches that include all commits and differences.
- Encoding issues might occur with non-UTF-8 encoded files, which could lead to incomplete results.
- The performance may vary depending on the size of the repository and the complexity of the search.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please fork the repository, create a new branch for your feature or fix, and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thank you to the maintainers of [GitPython](https://gitpython.readthedocs.io/en/stable/) for providing a powerful interface for interacting with Git repositories.
- Inspiration for the name "Netherite Pickaxe" comes from the extensive search capabilities of the tool, similar to the mining aspect in games.
