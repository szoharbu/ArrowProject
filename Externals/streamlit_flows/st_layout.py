import streamlit as st
from streamlit_ace import st_ace

# Initialize session state variables before rendering any widgets
def initialize_session_state():
    # Initialize session state for multiple text areas if they don't exist
    if 'stdout_output' not in st.session_state:
        st.session_state['stdout_output'] = "stdout output will be printed here."
    if 'assembly_output' not in st.session_state:
        st.session_state['assembly_output'] = "assembly output will be printed here."
    if 'progress_line' not in st.session_state:
        st.session_state['progress_line'] = "please insert your code"
    if 'architecture' not in st.session_state:
        st.session_state['architecture'] = "riscv"


def create_home_layout():

    # Create columns for buttons with proper alignment
    run_button, download_button = st.columns([1, 1], gap="large")

    progress_line_text = st.session_state['progress_line']
    # Display the current status
    st.write(f"Status: {progress_line_text}")

    # Using st_ace to create a code input block with syntax highlighting
    code_input = st_ace(
            language="python",  # Highlight as Python
            theme="monokai",  # You can choose other themes like 'github', 'dracula'
            value="""# Write your code here
            
from Utils.configuration_management import Configuration
from Arrow_API import AR
from Arrow_API.resources.segment_manager import SegmentManager_API as SegmentManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager

Configuration.Knobs.Template.scenario_count.set_value(3)
Configuration.Knobs.Template.scenario_query.set_value({"basic_loop_scenario":50,"load_store_stress_scenario":49,Configuration.Tag.REST:1})

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM)
def basic_loop_scenario():
    AR.comment("inside basic_loop_scenario")
    loop_count = AR.rangeWithPeak(10,20,peak=12)
    with AR.Loop(counter=loop_count, counter_direction='increment'):
        AR.comment("inside Loop scope, generating 5 instructions")
        AR.generate(instruction_count=5)

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM)
def load_store_stress_scenario():
    AR.comment("inside load_store_stress_scenario")

    mem = SegmentManager.Memory(init_value=0x456)
    reg = RegisterManager.get_and_reserve()
    AR.generate(dest=mem, comment=f"store to mem")
    AR.generate(dest=reg, src=mem, comment=f"load from mem to reg")
    AR.generate(comment=f"random instruction")
    AR.generate(dest=reg, comment=f"randomly modify reg")
    AR.generate(dest=mem, src=reg, comment=f"store to mem")
    RegisterManager.free(reg)

""",
            height=500,
            key="ace_editor",
        )

    # Display the text areas with unique keys and values
    output_text = st.session_state['stdout_output']
    st.text_area("Output", value=output_text, height=250)
    assembly_text = st.session_state['assembly_output']
    st.text_area("assembly", value=assembly_text, height=250)

    # Buttons at the bottom
    st.markdown("---")

    # Return the button columns for later use in the main file
    return run_button, download_button, code_input



def create_isa_info_layout():

    import os

    st.button("Back", on_click=go_to_home, key=1)


    # base_dir_path = config_manager.get_value('base_dir_path')
    base_dir_path = os.path.join(os.path.dirname(__file__) )
    architecture = st.session_state["architecture"]
    if architecture == "arm":
        db_file_name = 'arm_instructions.json'
    elif architecture == "x86":
        db_file_name = 'x86_instructions.json'
    else:  # RISC-V
        db_file_name = 'riscv_instructions.json'
    db_path = os.path.join(base_dir_path, '..', 'db_manager', 'instruction_jsons' ,db_file_name)

    # Normalize the path to remove mixed separators
    db_path = os.path.normpath(db_path)

    # Check if the log file exists
    if os.path.exists(db_path):
        with open(db_path, "r") as log_file:
            log_content = log_file.read()  # Read the log file content
        # Display the log content in a scrollable text area
        st.text_area(f"file: {db_file_name}", value=log_content, height=400)

        # # Read and parse JSON # TODO:: for some reason, open a json file is significantly slower
        # with open(db_path, "r") as db_file:
        #     json_data = json.load(db_file)
        #
        # # Display JSON using st.json
        # st.json(json_data)
        #

    else:
        st.error(f"Log file not found at: {db_path}")


def go_to_home():
    st.session_state.current_view = "home"
