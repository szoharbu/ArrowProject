import sys
import os
import streamlit as st
import traceback

# # needed to avoid Streamlit cloud matching issues
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Tool")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Externals")))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Submodeles","arrow_content")))
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
        # Create an output directory
        run_dir = "StreamLit"  # StreamLit output directory
        output_dir = os.path.join(run_dir, "output")
        os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

        try:

            st.session_state["progress_line"] = "Processing..."

            # Create a template file to save user-provided code
            template_file = os.path.join(run_dir, "template.py")
            with open(template_file, "w") as f:
                f.write(code_input)


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

            try:
                # run main application logic

                from Utils.singleton_management import SingletonManager
                SingletonManager.reset()  # Reset all singletons

                import Utils
                import Tool
                from Utils.logger_management import Logger
                from Utils.arg_parser import arg_parser
                from Utils.configuration_management import configuration_management
                from Tool.generation_management import generate
                from Tool.memory_management import memory_manager
                Logger.clean_logger()
                reload(Utils.arg_parser.arg_parser)
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

                if not success:
                    raise RuntimeError("Failed to run tool")

                Logger.clean_logger()

            except Exception as e:
                # Catch any exception and display the full traceback
                st.error("An error occurred while running the tool! Check the logs for more details.")

                with st.expander("View Error Log"):
                    st.code(traceback.format_exc(), language="python")  # Display the full traceback

                # Read and display the tool's log file
                stdout_path = os.path.join(output_dir, "test.log")
                with open(stdout_path, "r") as log_file:
                    logs = log_file.read()

                with st.expander("View Tool Logs"):
                    st.code(logs, language="python")  # Show the log content in an expander


            # Read the content of the std_out file
            stdout_path = os.path.join(output_dir, "test.log")
            with open(stdout_path, "r") as f:
                stdout_file = f.read()
            st.session_state["stdout_output"] = stdout_file


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
            # Catch any exception and display the full traceback
            st.error(f"Error while running the tool: {e}")

            with st.expander("View Error log"):
                st.code(traceback.format_exc(), language="python")  # Display the full traceback

            # Read and display the tool's log file
            stdout_path = os.path.join(output_dir, "test.log")
            with open(stdout_path, "r") as log_file:
                logs = log_file.read()

            with st.expander("View Tool Logs"):
                st.code(logs, language="python")  # Show the log content in an expander
