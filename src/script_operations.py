import os
import shutil
import subprocess

from file_operations import get_file_content

def get_functions_in_script(script_content):
    script_lines = script_content.split('\n')
    functions_names = []

    for script_line in script_lines:
        if script_line.startswith('def') and script_line.endswith('):'):
            functions_names.append(script_line.replace('def', '').split('(')[0].strip())
    
    return functions_names

def get_script_name(script_path):
    return os.path.basename(script_path).replace(".py", "")

def has_function(script_path):
    functions = get_functions_in_script(get_file_content(script_path))
    
    if len(functions) == 0:
        return False

    return True

def create_script_copy(script_path):
    script_copy_path = script_path.replace('.py', '-dfa-copy.py')
    shutil.copy(script_path, script_copy_path)
    return script_copy_path

def delete_script_copy(script_copy_path):
    os.remove(script_copy_path)

def delete_control_file(control_file_path):
    os.remove(control_file_path)

def get_indentation(script_content):
    script_lines = script_content.split('\n')

    for i in range(len(script_lines)):
        if script_lines[i].startswith('def') and script_lines[i].endswith('):'):
            return len(script_lines[i+1]) - len(script_lines[i+1].lstrip())

def remove_script_empty_lines(script_lines):
    return [script_line for script_line in script_lines if script_line.strip()]

def run_python_script(script_path, script_args=None):
    try:
        command = ["python", script_path]
        if script_args:
            command.extend(script_args)
        subprocess.run(command)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the script: {e}")
        return False
    return True