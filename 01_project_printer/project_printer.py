import os
import sys
import mimetypes
import fnmatch
import argparse
from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPattern

language_dict = {
            '.bat': 'batch',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.css': 'css',
            '.dart': 'dart',
            '.dockerfile': 'docker',
            'Dockerfile': 'docker',
            '.gradle': 'groovy',
            '.h': 'c_header',
            '.hpp': 'cpp_header',
            '.html': 'html',
            '.ini': 'ini',
            '.ipynb': 'json',
            '.java': 'java',
            '.jl': 'julia',
            '.js': 'javascript',
            '.json': 'json',
            '.jsx': 'jsx',
            '.kt': 'kotlin',
            '.lua': 'lua',
            '.m': 'objective-c',
            '.makefile': 'makefile',
            'Makefile': 'makefile',
            '.md': 'markdown',
            '.php': 'php',
            '.pl': 'perl',
            '.plist': 'xml',
            '.ps1': 'powershell',
            '.py': 'python',
            '.r': 'r',
            '.rb': 'ruby',
            '.rs': 'rust',
            '.sass': 'sass',
            '.scss': 'scss',
            '.sh': 'bash',
            '.sql': 'sql',
            '.swift': 'swift',
            '.ts': 'typescript',
            '.tsx': 'tsx',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
        }

def parse_args():
    parser = argparse.ArgumentParser(description="A program to print the contents of a project.")
    parser.add_argument("--path", type=str, help="The path to the project to print")
    parser.add_argument("--output", type=str, help="The output file to write to", default="project_contents.txt")
    parser.add_argument("--ignore", action="store_true", help="Respect .gitignore files")
    return parser.parse_args()

def get_pathspec(gitignore_path):
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            gitignore_content = f.read()
            return PathSpec.from_lines(GitWildMatchPattern, gitignore_content.splitlines())
    else:
        print("Warning: No .gitignore file found.")
        return None
    
def is_binary(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type.startswith('image') or 'application' in mime_type
    return False

def print_project_files(project_root_path, pathspec, output_file):
    with open(output_file, "w") as f:
        for root, dirs, files in os.walk(project_root_path):
            for file_name in files:
                abs_file_path = os.path.join(root, file_name)
                rel_file_path = os.path.relpath(abs_file_path, project_root_path)
                
                # print file content only if it is not binary and not ignored
                # Only print file names for binary files not ignored
                if pathspec and pathspec.match_file(rel_file_path):
                    continue
                elif is_binary(rel_file_path):
                    f.write(f'{rel_file_path}\n\n')
                else:
                    _, ext = os.path.splitext(file_name)
                    language = language_dict.get(ext, 'plaintext')
                    f.write(f'{rel_file_path}')
                    f.write(f'```{language}\n')
                    try:
                        with open(abs_file_path, 'r') as file:
                            f.write(file.read())
                    except UnicodeDecodeError:
                        f.write(f"Binary of unsupported encoding\n")
                    f.write('```\n')

def generate_output_filename(base_name):
    index = 0
    current_name = base_name
    while os.path.exists(current_name):
        index += 1
        current_name = f"{base_name}_{index}.txt"
    return current_name

def main():
    # Parse the arguments
    args = parse_args()

    # Check if the path exists
    if not os.path.exists(args.path):
        print(f"Error: The path '{args.path}' does not exist.")
        sys.exit(1)

    # Load the gitignore file if necessary
    pathspec = None
    if args.ignore:
        gitignore_path = os.path.join(args.path, ".gitignore")
        pathspec = get_pathspec(gitignore_path)

    # Generate the output filename if necessary
    output_filename = generate_output_filename(args.output)

    # Print the project files
    print_project_files(args.path, pathspec, output_filename)

    

if __name__ == "__main__":
    main()