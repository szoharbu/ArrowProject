import sys
import os
import streamlit as st

# # needed to avoid Streamlit cloud matching issues
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Tool")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Externals")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Submodeles","arrow_content")))
from Arrow import main
from importlib import reload

# Function that will run when the Run button is clicked
def handle_run_button(code_input):
    """
    Logic to handle the code execution and updates to text sections.
    """
    # Execute button at the bottom of the page
    if not code_input.strip():
        st.error("Please enter some code or a template before running.")
    else:
        try:

            st.session_state["progress_line"] = "Processing..."

            # Create an output directory
            run_dir = "StreamLit"  # StreamLit output directory

            # Ensure the output directory exists
            if not os.path.exists(run_dir):
                os.makedirs(run_dir)

            # Create a template file to save user-provided code
            template_file = os.path.join(run_dir, "template.py")
            with open(template_file, "w") as f:
                f.write(code_input)

            output_dir = os.path.join(run_dir, "output")

            # Run the tool's main function with the template input
            print(f"Template created at: `{template_file}`")
            st.session_state["progress_line"] = f"Template created at: `{template_file}`"

            # Command to run your tool with the template and output directory
            architecture = st.session_state["architecture"]
            seed = st.session_state["seed"]
            # command = ["python", "Tool/main.py", template_file, "--output", output_dir, "--arch", architecture, "--seed", str(seed), "--cloud_mode", "True" ]
            command = [template_file, "--output", output_dir, "--arch", architecture,"--seed", str(seed), "--cloud_mode", "True"]
            command_str = " ".join(command)
            print(f"Test command line is : `{command_str}`")
            # st.write(f"Test command line is : `{command_str}`")
            #success = run_tool(template_file, output_dir, command_line=command, run_str="StreamLit_run")

            from Utils.singleton_management import SingletonManager
            SingletonManager.reset()  # Reset all singletons

            from Utils.logger_management import Logger
            from Tool.generation_management import generate
            from Tool.memory_management import memory_manager
            import Utils
            import Tool
            #Logger.clean_logger()
            reload(Utils.logger_management)
            reload(Utils.configuration_management.configuration_management)
            reload(Utils.configuration_management.knob_manager)
            reload(Utils.configuration_management.knobs)
            reload(Tool.memory_management.memory_manager)

            # reload(Tool.ingredient_management)
            # from Utils.configuration_management import tags_and_enums
            # reload(tags_and_enums)
            # from Tool.db_manager import models
            # reload(models)
            # from Tool.generation import generate
            # reload(generate)

            success = main.main(command)

            Logger.clean_logger()

            # Read the content of the std_out file
            stdout_path = os.path.join(output_dir, "test.log")
            with open(stdout_path, "r") as f:
                stdout_file = f.read()
            st.session_state["stdout_output"] = stdout_file

            if not success:
                raise RuntimeError("Failed to run tool")

            # Read the content of the asm file
            arch = st.session_state["architecture"]
            if arch == "riscv":
                asm_path = os.path.join(output_dir, "test.s")
            else:
                asm_path = os.path.join(output_dir, "test.asm")
            with open(asm_path, "r") as f:
                asm_file = f.read()
            st.session_state["assembly_output"] = asm_file

            st.session_state["progress_line"] = "Finished"

        except Exception as e:
            st.error(f"Error while running the tool: {e}")