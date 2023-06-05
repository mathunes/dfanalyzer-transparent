import argparse
import os
import subprocess
import shutil

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

def create_script_copy(script_path):
    script_copy_path = script_path.replace('.py', '-dfa-copy.py')
    shutil.copy(script_path, script_copy_path)
    return script_copy_path

def create_prov_control_file(script_path):
    directory = os.path.dirname(script_path)
    prov_control_file = os.path.join(directory, 'dfa-prov-control-file.txt')
    
    with open(prov_control_file, 'w') as file:
        pass

    return prov_control_file

def get_indentation(script_content):
    script_lines = script_content.split('\n')

    for i in range(len(script_lines)):
        if script_lines[i].startswith('def') and script_lines[i].endswith('):'):
            return len(script_lines[i+1]) - len(script_lines[i+1].lstrip())

def remove_script_empty_lines(script_lines):
    return [script_line for script_line in script_lines if script_line.strip()]

def add_dfa_write_prov_control_file_function(indentation):
    return f"def dfa_write_prov_control_file(log):\n{indentation}with open('dfa-prov-control-file.txt', 'a') as file:\n{indentation + indentation}file.write(log + '\\n')"



def instrument_copy_script(script_copy_path):
    script_content = get_script_content(script_copy_path)
    script_lines = remove_script_empty_lines(script_content.split('\n'))
    indentation = ' ' * get_indentation(script_content)
    function_name = ''

    with open(script_copy_path, 'w') as file:
        file.write(add_dfa_write_prov_control_file_function(indentation) + '\n')
    
        for i in range(len(script_lines)):
            file.write(script_lines[i] + '\n')

            if script_lines[i].startswith('def') and script_lines[i].endswith('):'):
                function_name = script_lines[i].replace('def', '').split('(')[0].strip()
                function_parameters = script_lines[i].split('(')[1].split(')')[0].split(',')
                function_parameters = [function_parameter.strip() for function_parameter in function_parameters if function_parameter.strip()]
                
                if len(function_parameters) > 0:
                    function_parameters_with_value = '; '.join([f'{item} = \' + str({item}) + \'' for item in function_parameters])
                else:
                    function_parameters_with_value = ''


                file.write(indentation + f'dfa_write_prov_control_file(f\'CALL FUNCTION {function_name} WITH FOLLOWING PARAMETERS: {function_parameters_with_value} \') \n')
            
            if i < len(script_lines) - 1 and 'return ' in script_lines[i + 1]:
                return_ref = script_lines[i + 1].replace('return ', '').strip()

                if isinstance(return_ref, list):
                    return_ref = ' '.join(map(str, return_ref))
                
                file.write(indentation + f'dfa_write_prov_control_file(\'RETURN FUNCTION {function_name} WITH FOLLOWING VALUE: \' + str({return_ref})) \n')

            if i < len(script_lines) - 1 and not script_lines[i + 1].startswith(indentation) and not 'return ' in script_lines[i]:
                file.write(indentation + f'dfa_write_prov_control_file(\'RETURN FUNCTION {function_name} \') \n')




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

            script_copy_path = create_script_copy(script_path)
            create_prov_control_file(script_path)

            instrument_copy_script(script_copy_path)

            run_python_script(script_copy_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Python script.")
    parser.add_argument("script", help="Path to the Python script.")
    args = parser.parse_args()
    main(args)