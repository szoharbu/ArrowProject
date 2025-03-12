
import streamlit as st
from peewee import *
from typing import List, Optional
from extract_db import extract, get_unique_values, return_last_modified_date

asl_path = "https://pdx.talos.nvidia.com/serve/home/nvcpu-sw-co100/asl/1.0/current/debug_arm/x86_64/doc/olympus_asl.html"
usl_path = "https://pdx.talos.nvidia.com/serve/home/nvcpu-sw-co100/usl/1.0/current/debug_arm/x86_64/doc/olympus_usl.html"



# Streamlit UI
st.title("🔍 Instruction Query Explorer")
st.markdown("⚠️ **Disclaimer!**    This tool and database are still under development. "
    f"Errors and inaccuracies may occur. Please verify information with official **[ASL]({asl_path})** and **[USL]({usl_path})** resources."
    "If you notice any mistakes, please contact me at [zbuchris@nvidia.com](mailto:zbuchris@nvidia.com)")



# Sidebar: Project Selection (Separate Section)
st.sidebar.header("📂 Project Settings")

# Define available projects and their corresponding databases
PROJECT_DATABASES = {
    "Olympus": "database_a.db",
    "Rigel": "database_b.db",
}

# Sidebar: Select a Project
selected_project = st.sidebar.selectbox(
    "🔹 Select a Project",
    list(PROJECT_DATABASES.keys()),
    help="Select a project to use a different database."
)

st.sidebar.markdown("---")  # Adds a horizontal line for separation

# Sidebar Input Fields
st.sidebar.header("🔧 Query Parameters")

query_input = st.sidebar.text_area(
    "Custom Query (Peewee Expression)",
    value="",
    placeholder="(Instruction.mnemonic.contains('zip')) & (Instruction.max_latency==2) & (Instruction.steering_class.contains('mx_pred'))",
    help="Example: (Instruction.max_latency==2) or (Instruction.steering_class.contains('mx_pred'))",
    height=120
)


# Sidebar: Source & Destination Filters (Inside Expanders)
with st.sidebar.expander("⚙️ Arch Filters", expanded=False):

    # Mnemonic Field
    mnemonic = st.text_input(
        "Mnemonic",
        value="",
        placeholder="e.g., 'add', 'sub', 'mul'",
        help="Enter an instruction mnemonic (e.g., add, sub, mul)."
    )

    # Fetch unique values from each src_type field
    src1_types = get_unique_values("src1_type")
    src2_types = get_unique_values("src2_type")
    src3_types = get_unique_values("src3_type")
    src4_types = get_unique_values("src4_type")
    all_src_types = list(set(src1_types + src2_types + src3_types + src4_types))
    all_src_types.insert(0, "")    # Add an empty option at the beginning

    # Fetch unique values from each src_type field
    dest1_types = get_unique_values("dest1_type")
    dest2_types = get_unique_values("dest2_type")
    all_dest_types = list(set(dest1_types + dest2_types))
    all_dest_types.insert(0, "")    # Add an empty option at the beginning


    src_type = st.selectbox("Source Type",
                            all_src_types,
                            #["", "GPR", "SIMD_FPR", "SVE", "IMMEDIATE", "LABEL", "SHIFT"],
                            help="Filters instructions where at least ONE operand has this source type.")

    src_size = st.selectbox("Source Size",
                            ["", "8-bit", "16-bit", "32-bit", "64-bit", "128-bit"],
                            help="Filters instructions where at least ONE operand has this source size.")

    dest_type = st.selectbox("Destination Type",
                             #["", "GPR", "SIMD_FPR", "SVE", "IMMEDIATE", "LABEL", "SHIFT"],
                             all_dest_types,
                             help="Filters instructions where at least ONE operand has this destination type.")

    dest_size = st.selectbox("Destination Size",
                             ["", "8-bit", "16-bit", "32-bit", "64-bit", "128-bit"],
                             help="Filters instructions where at least ONE operand has this destination size.")

    # removing the "-bit" suffix
    dest_size = dest_size.split('-')[0]
    src_size = src_size.split('-')[0]




with st.sidebar.expander("⚙️ UArch Filters", expanded=False):
    # Use session state for result limit
    # Query database for all unique steering_class values
    steering_class_list = get_unique_values("steering_class")
    selected_steering_classes = st.multiselect(
        "Steering Class",
        steering_class_list,
        help="Select one or more steering classes. The filter will include ONLY instructions that contain ALL selected classes. (AND operation)"
    )

    # Fetch unique latency values from the database
    max_latency_options = get_unique_values("max_latency")
    max_latency_options.insert(0, "") # Convert numeric values to strings (if needed) and add an empty option
    selected_max_latency = st.selectbox(
        "Max Latency",
        max_latency_options,
        help="Filters instructions based on max MOP latency."
    )


# Use session state for result limit
col1, col2 = st.sidebar.columns([2, 2])  # Wider column for results, smaller for input
with col1:
    run_query = st.button("🔄 Run Query")  # Query button in first column

with col2:
    result_limit = st.number_input(
        "Max Results", min_value=10, max_value=5000, value=100, step=50, label_visibility="collapsed",
        help="Increase this number to show more results."
    )  # Number input in second column



# Run Button
#if st.sidebar.button("🔄 Run Query"):
if run_query:

    if selected_project != "Olympus":
        st.error(f"Project {selected_project} is not yet supported")
    else:

        instructions = extract(selected_project,
                               instr_query=query_input if query_input.strip() else None,
                               mnemonic=mnemonic if mnemonic.strip() else None,
                               src_size=src_size if src_size.strip() else None,
                               src_type=src_type if src_type.strip() else None,
                               dest_size=dest_size if dest_size.strip() else None,
                               dest_type=dest_type if dest_type.strip() else None,
                               steering_classes=selected_steering_classes if selected_steering_classes else None,
                               max_latency=int(selected_max_latency) if selected_max_latency else None,
                               )


        total_instructions = len(instructions)
        instructions_to_show = instructions[:result_limit]

        # Determine whether to show all or limited results
        st.subheader(f"📄 Matching Instructions: {len(instructions)}")
        if total_instructions > result_limit:
            st.subheader(f"    Showing {result_limit} of {total_instructions} Instructions")

        if instructions_to_show:
            for inst in instructions_to_show:
                with st.expander(f"{inst.id}"):
                    st.markdown(f"### `{inst.mnemonic}` ")
                    st.markdown(f"{inst.description} ")
                    st.code(inst.syntax)
                    st.subheader("Operands:")
                    if inst.operands:
                        for op in inst.operands:
                            operand_txt = f"• OP{op.index}: {op.text} type={op.type}, role={op.role}"
                            if op.is_optional:
                                operand_txt += " (Optional)"
                            st.text(operand_txt)
                    else:
                        st.text(f"• No operands")
                    st.subheader("Attributes:")
                    st.text(f"•  mop count: {inst.mop_count}")
                    st.text(f"•  max_latency: {inst.max_latency}")
                    st.text(f"•  steering_classes: {inst.steering_class}")

                    st.subheader("Resources:")
                    if inst.usl_flow != "N/A":
                        asl_link = asl_path + f"#{inst.usl_flow}"
                        usl_link = usl_path + f"#{inst.usl_flow}"
                        st.markdown(f"🔗 **[ASL::{inst.id}]({asl_link})**")
                        st.markdown(f"🔗 **[USL::{inst.id}]({usl_link})**")
                    else:
                        st.markdown(f"🔗 N/A")

# Sidebar: About / Support Info
st.sidebar.markdown("---")  # Adds a horizontal line for separation
st.sidebar.markdown("📖 **About This Tool**")
st.sidebar.markdown("A utility that helps query and explore instruction data efficiently.")

st.sidebar.markdown("💡 **Feedback & Support**")
st.sidebar.markdown("For suggestions, issues, or questions, contact **Zohar Buchris** at [zbuchris@nvidia.com](mailto:zbuchris@nvidia.com)")


st.sidebar.markdown("---")  # Adds a horizontal line for separation
st.sidebar.markdown("📝 **JSON Database**")

# Download Jsons
col3, col4 = st.sidebar.columns([2, 2])  # Wider column for results, smaller for input

time = return_last_modified_date()
st.sidebar.markdown(time)

# Read the JSON file
arm_asl_instructions_json_path = "C:/Users/zbuchris/PycharmProjects/ArrowProject/Externals/db_manager/instruction_jsons/arm_asl_instructions.json"
with open(arm_asl_instructions_json_path, "r", encoding="utf-8") as f:
    asl_json_data = f.read()  # Read file content as string
with col3:
    st.download_button(
        label="📥 ASL JSON",
        data=asl_json_data,
        file_name="arm_asl_instructions.json",
        mime="application/json",
        help="Click to download ASL as a JSON file."
    )

# Read the JSON file
arm_usl_instructions_json_path = "C:/Users/zbuchris/PycharmProjects/ArrowProject/Externals/db_manager/instruction_jsons/arm_usl_instructions.json"
with open(arm_usl_instructions_json_path, "r", encoding="utf-8") as f:
    usl_json_data = f.read()  # Read file content as string
with col4:
    st.download_button(
        label="📥 USL JSON",
        data=usl_json_data,
        file_name="arm_usl_instructions.json",
        mime="application/json",
        help="Click to download USL as a JSON file."
    )
