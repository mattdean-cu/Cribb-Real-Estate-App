import os

# Customize these:
EXTENSIONS = ('.py', '.js', '.ts', '.jsx', '.html', '.css', '.json')
EXCLUDE_DIRS = {'node_modules', '.git', '__pycache__', 'venv', 'env', 'dist', 'build', '.idea', '.vscode'}

def print_relevant_structure(root_dir, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Modify dirnames in-place to skip unwanted dirs
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            level = dirpath.replace(root_dir, "").count(os.sep)
            indent = "    " * level
            f.write(f"{indent}{os.path.basename(dirpath)}/\n")

            for file in filenames:
                if file.endswith(EXTENSIONS):
                    f.write(f"{indent}    {file}\n")

print_relevant_structure("server", "structure.txt")
#print_relevant_structure("client", "structure.txt")