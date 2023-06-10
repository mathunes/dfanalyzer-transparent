import argparse
from dfa_lib_python.dataflow import Dataflow
from dfa_lib_python.transformation import Transformation
from dfa_lib_python.attribute import Attribute
from dfa_lib_python.attribute_type import AttributeType
from dfa_lib_python.set import Set
from dfa_lib_python.set_type import SetType
from dfa_lib_python.task import Task
from dfa_lib_python.dataset import DataSet
from dfa_lib_python.element import Element
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

def get_file_content(file_path):
    with open(file_path, "r") as file:
        return file.read()

def get_functions_in_script(script_content):
    script_lines = script_content.split('\n')
    functions_names = []

    for script_line in script_lines:
        if script_line.startswith('def') and script_line.endswith('):'):
            functions_names.append(script_line.replace('def', '').split('(')[0].strip())
    
    return functions_names

def get_script_name(script_path):
    return os.path.basename(script_path).replace(".py", "")

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
    script_content = get_file_content(script_copy_path)
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


                file.write(indentation + f'dfa_write_prov_control_file(f\'>>> {function_name} : {function_parameters_with_value} \') \n')
            
            if i < len(script_lines) - 1 and 'return ' in script_lines[i + 1]:
                return_ref = script_lines[i + 1].replace('return ', '').strip()

                if isinstance(return_ref, list):
                    return_ref = ' '.join(map(str, return_ref))
                
                file.write(indentation + f'dfa_write_prov_control_file(\'<<< {function_name} : \' + str({return_ref})) \n')

            if i < len(script_lines) - 1 and not script_lines[i + 1].startswith(indentation) and not 'return ' in script_lines[i]:
                file.write(indentation + f'dfa_write_prov_control_file(\'<<< {function_name} \') \n')

# ADD FUNCTIONS TO READ CONTROL TEMP FILE AND STORE PROV DATA

def create_call_transformation(dflow, transf_output, transf_input, transf2, i):

    transf = Transformation('call_' + str(i))

    transf_output.set_type = SetType.INPUT
    # transf_output.dependency = transf2._tag

    # transf_input.set_type = SetType.OUTPUT

    transf.set_sets([transf_output, transf_input])

    return transf


def get_prospective_prov(script_name, prov_control_path):
    prov_control_content = get_file_content(prov_control_path)
    
    prov_control_lines = remove_script_empty_lines(prov_control_content.split('\n'))

    dataflow_tag = script_name

    dflow = Dataflow(dataflow_tag)

    function_called_count = 0

    for i in range(len(prov_control_lines)):

        prov_control_line = prov_control_lines[i]

        if prov_control_line.startswith(">>>"):
            function_name = prov_control_line.split(":")[0].replace(">>>", "").strip()

            attributes = prov_control_line.split(":")[1].strip().split(";")

            attributes = [attribute for attribute in attributes if attribute != ""]

            i_attribute_list = []

            for attribute in attributes:
                i_attribute_list.append(Attribute(attribute.split(" = ")[0].strip().upper(), AttributeType.TEXT))

            transf_input = Set("i_set_" + function_name, SetType.INPUT, i_attribute_list)

            if function_called_count > 0:
                dflow.add_transformation(create_call_transformation(dflow, transf_output, transf_input, transf, function_called_count))

            if prov_control_lines[i+1].startswith(">>>"):
                transf_output = Set("inside_" + function_name, SetType.OUTPUT, [])

                transf = Transformation(function_name)

                transf.set_sets([transf_input, transf_output])
                
                dflow.add_transformation(transf)

        else:
            transf_output = Set("o_set_" + function_name, SetType.OUTPUT, [])

            transf = Transformation(function_name)

            transf.set_sets([transf_input, transf_output])
            
            dflow.add_transformation(transf)
        
        function_called_count += 1
    
    dflow.save()




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
            script_name = get_script_name(script_path)

            functions_names = get_functions_in_script(get_file_content(script_path))

            script_copy_path = create_script_copy(script_path)
            prov_control_path = create_prov_control_file(script_path)

            instrument_copy_script(script_copy_path)

            run_python_script(script_copy_path)

            get_prospective_prov(script_name, prov_control_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Python script.")
    parser.add_argument("script", help="Path to the Python script.")
    args = parser.parse_args()
    main(args)