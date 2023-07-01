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
                file.write(indentation + f'dfa_write_prov_control_file(\'<<< {function_name} : \') \n')

def get_prospective_prov(script_name, prov_control_path):
    prov_control_content = get_file_content(prov_control_path)
    
    prov_control_lines = prov_control_content.split('\n')

    dataflow_tag = script_name

    dflow = Dataflow(dataflow_tag)

    function_called_count = 0

    for prov_control_line in prov_control_lines:
        if prov_control_line.startswith(">>>"):
            function_name = prov_control_line.split(":")[0].replace(">>>", "").strip()

            attributes = prov_control_line.split(":")[1].strip().split(";")

            attributes = [attribute for attribute in attributes if attribute != ""]

            i_attribute_list = []

            for attribute in attributes:
                i_attribute_list.append(Attribute(attribute.split(" = ")[0].strip().upper(), AttributeType.TEXT))

            transf_input = Set("i_" + function_name, SetType.INPUT, i_attribute_list)

            if function_called_count > 0:
                transf_aux = Transformation("call_function_" + function_name)
                
                transf_output.set_type(SetType.INPUT)
                transf_output.dependency = transf._tag
                transf_input.set_type(SetType.OUTPUT)

                transf_aux.set_sets([transf_output, transf_input])

                dflow.add_transformation(transf_aux)

            transf_input.set_type(SetType.INPUT)

            transf_output = Set("o_" + function_name, SetType.OUTPUT, [Attribute('RETURNED_DATA', AttributeType.TEXT)])

            transf = Transformation(function_name)

            transf.set_sets([transf_input, transf_output])
            
            dflow.add_transformation(transf)

            function_called_count += 1
    
    dflow.save()

def get_retrospective_prov(script_name, prov_control_path, functions_names):
    prov_control_content = get_file_content(prov_control_path)
    
    prov_control_lines = prov_control_content.split('\n')

    dataflow_tag = script_name

    tasks = {}

    for i, prov_control_line in enumerate(prov_control_lines, start=1):
        if prov_control_line.startswith(">>>"):
            function_name = prov_control_line.split(":")[0].replace(">>>", "").strip()
            tasks[function_name] = Task(i, dataflow_tag, function_name)

    for prov_control_line in prov_control_lines:
        if prov_control_line.startswith(">>>"):
            function_name = prov_control_line.split(":")[0].replace(">>>", "").strip()

            attributes_values = prov_control_line.split(":")[1].strip().split(";")

            attributes_values = [attribute_value for attribute_value in attributes_values if attribute_value != ""]

            i_attributes_values_list = []

            for attribute_value in attributes_values:
                i_attributes_values_list.append(attribute_value.split(" = ")[1].strip())

            task_input = DataSet("i_" + function_name, [Element(i_attributes_values_list)])
            tasks[function_name].add_dataset(task_input)
            tasks[function_name].begin()

        elif prov_control_line.startswith("<<<"):
            function_name = prov_control_line.split(":")[0].replace("<<<", "").strip()

            returned_data = prov_control_line.split(":")[1].strip().replace("'", "\\'")

            task_output = DataSet("o_" + function_name, [Element([returned_data])])

            tasks[function_name].add_dataset(task_output)
            tasks[function_name].end()

def instrument_copy_script_without_function(script_copy_path, script_args):
    script_content = get_file_content(script_copy_path)
    script_lines = remove_script_empty_lines(script_content.split('\n'))

    script_name = get_script_name(script_copy_path).replace('-', '_')

    with open(script_copy_path, 'w') as file:
        file.write(add_dfa_write_prov_control_file_function('    ') + '\n')

        file.write(f'dfa_write_prov_control_file(f\'>>> {script_name} : {script_args} \') \n')

        for i in range(len(script_lines)):
            file.write(script_lines[i] + '\n')

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

def main(arguments):
    script_path = arguments[0]

    if is_script_path_valid(script_path):
        if (is_script_python(script_path)):
            script_name = get_script_name(script_path)

            script_copy_path = create_script_copy(script_path)

            prov_control_path = create_prov_control_file(script_path)

            if (has_function(script_path)):

                functions_names = get_functions_in_script(get_file_content(script_path))

                instrument_copy_script(script_copy_path)

                run_python_script(script_copy_path)

                get_prospective_prov(script_name, prov_control_path)

                get_retrospective_prov(script_name, prov_control_path, functions_names)

            else:
                
                script_args = ''

                if len(arguments) > 1:
                    script_args = concatenated_string = "; ".join(f"argument_{i} = {arg}" for i, arg in enumerate(arguments[1:], start=1))

                instrument_copy_script_without_function(script_copy_path, script_args)

                run_python_script(script_copy_path, arguments)

                get_prospective_prov(script_name, prov_control_path)

                get_retrospective_prov(script_name, prov_control_path, [script_name])
                
            delete_script_copy(script_copy_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Python script.")
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()
    main(args.args)