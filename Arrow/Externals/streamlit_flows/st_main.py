import streamlit as st
# for some reason streamlit fails when trying to import directly from Wrappers, using relative import instead
# from Wrappers.streamlit_flows.st_sidebar import configure_sidebar
# from Wrappers.streamlit_flows.st_layout import create_layout, initialize_session_state
# from Wrappers.streamlit_flows.run_button_logic import handle_run_button
from st_sidebar import configure_sidebar
from st_layout import create_home_layout, create_isa_info_layout, initialize_session_state
from run_button_logic import handle_run_button


# Main app entry point
def main():

    initialize_session_state()

    # Set page configuration for fixed size
    st.set_page_config(
        page_title="Custom Layout",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for fixed-size layout and styling
    st.markdown("""
        <style>
            .main {
                max-width: 1200px;
                margin: 0 auto;
            }
            .fixed-section {
                height: 400px;
                overflow: auto;
            }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    if "current_view" not in st.session_state:
        st.session_state.current_view = "home"  # Default view

    # Call the sidebar function and retrieve values
    #architecture, num_cores, seed = configure_sidebar()
    configure_sidebar()


    # Sidebar Navigation
    if st.session_state.current_view == "home":
        # Call the layout function from the external file
        run_button, download_button, code_input = create_home_layout()

        # Run button logic
        with run_button:
            st.button("Run", on_click=handle_run_button, args=[code_input])
            # st.write("Processing...")

        with download_button:
            asm_file = st.session_state["assembly_output"]
            download_button.download_button(
                label="Download assembly file",
                data=asm_file,
                file_name="test.asm",
                mime="text/plain",
            )

    elif st.session_state.current_view == "isa_info":
        create_isa_info_layout()
    else:
        raise ValueError("Invalid 'current_view'")



if __name__ == "__main__":
    main()
