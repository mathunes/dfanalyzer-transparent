import argparse
import os
import subprocess

def is_script_path_valid(script_path):
    if not os.path.exists(script_path):
        print("dfa-tr: this script path does not exists.")
        return False
    return True

def is_script_python(script_path):
    if not script_path.endswith(".py"):
        print("dfa-tr: this is not script python.")
        return False
    return True

def get_script_content(script_path):
    with open(script_path, "r") as file:
        return file.read()

def get_functions_in_script(script_content):
    script_lines = script_content.split('\n')
    functions_names = []

    for script_line in script_lines:
        if script_line.startswith('def') and script_line.endswith('):'):
            functions_names.append(script_line.replace('def', '').split('(')[0].strip())
    
    return functions_names

def run_python_script(script_path):
    try:
        subprocess.run(["python", script_path])
    except subprocess.CalledProcessError as e:
        print(f"dfa-tr: An error occurred while running the script: {e}")
        return False
    return True

def main(arguments):
    script_path = arguments.script

    if is_script_path_valid(script_path):
        if (is_script_python(script_path)):
            functions_names = get_functions_in_script(get_script_content(script_path))

            for function_name in functions_names:
                print(function_name)

            run_python_script(script_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Python script.")
    parser.add_argument("script", help="Path to the Python script.")
    args = parser.parse_args()
    main(args)