import streamlit as st
import random

# Sidebar configuration
def configure_sidebar():
    st.sidebar.markdown("<h2>Settings</h2>", unsafe_allow_html=True)

    # Section 1: Configuration knobs
    with st.sidebar.expander("Configuration Knobs", expanded=True):
        # Initialize session state key if it doesn't exist
        if "architecture" not in st.session_state:
            st.session_state["architecture"] = "riscv"  # Default value

        # Create the selectbox with the value from session_state
        architecture = st.selectbox("Architecture", ["riscv", "arm", "x86"])

        #TODO:: at the moment I'm overriding the architecture selection, until I will succeed in changing Arch and DB
        architecture = "riscv"

        # Update session state when the selectbox value changes
        st.session_state["architecture"] = architecture

        #num_cores = st.slider("Number of Cores", 1, 4, 1)

        # Check if the random number exists in session_state
        if "seed" not in st.session_state:
            st.session_state.seed = random.randint(10000, 1000000)  # Generate and store it
        seed = st.number_input("Seed Value",  value=st.session_state.seed, step=1)
        st.session_state["seed"] = seed


    # Section 2: API Section
    with st.sidebar.expander("API Documentation", expanded=False):
        st.markdown("""
        ```python
        def calculate(input):
            return input * 2
        ```
        This function takes an input and doubles its value.
        """)

    # Add custom CSS for left-aligning button text
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] button {
            width: 100% !important; /* Make buttons take full width */
            text-align: left !important; /* Align text to the left */
            justify-content: flex-start !important; /* Ensure proper alignment */
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # Section 3: Mnemonic Section
    if st.session_state.current_view == "home":
        st.sidebar.button("ISA info", on_click=go_to_ISA_INFO)
    elif st.session_state.current_view == "isa_info":
        st.sidebar.button("Back", on_click=go_to_home, key=2)
    else:
        raise ValueError("Invalid 'current_view'")


    # # Return important values for further use
    # return architecture, num_cores, seed

def go_to_home():
    st.session_state.current_view = "home"

def go_to_ISA_INFO():
    st.session_state.current_view = "isa_info"