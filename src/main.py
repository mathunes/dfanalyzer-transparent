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
from script_validator import is_script_path_valid, is_script_python
from file_operations import get_file_content
from script_operations import (get_functions_in_script, get_script_name, has_function,
                               create_script_copy, delete_script_copy, delete_control_file,
                               get_indentation, remove_script_empty_lines, run_python_script)
from provenance import (create_prov_control_file, get_prospective_prov, get_retrospective_prov,
                        instrument_copy_script, instrument_copy_script_without_function,
                        add_dfa_write_prov_control_file_function)


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

            delete_control_file(prov_control_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Python script.")
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()
    main(args.args)