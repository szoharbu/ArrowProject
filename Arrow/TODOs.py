'''
Arrow/
├── Arrow/                      # Main package for the tool
│   ├── core/                   # Core logic of the tool
│   ├── flows/                  # Outer workflows
│   ├── io/                     # Input/output operations
│   ├── utils/                  # Utility functions
│   ├── main.py                 # Entry point for the tool
│   └── cli.py                  # Command-line interface
├── external/                   # External repositories
│   ├── content/                # External content repository
│   ├── instruction_db/         # Another standalone repository
│   └── ...                     # Additional external repos
├── front_end/                  # Front-end files for the tool
│   ├── __init__.py             # Optional if you use Python here
│   ├── static/                 # Static files (CSS, JS, images)
│   ├── templates/              # HTML templates (if using frameworks like Flask)
│   └── streamlit/              # Streamlit-specific front-end logic
├── tests/                      # Unit and integration tests
├── scripts/                    # Utility scripts
├── requirements.txt            # Dependencies for the project
├── setup.py                    # Setup script for packaging
└── README.md                   # Overview and usage instructions
'''

# TODO:: arg parser
# DONE:: take care of output directory and other command line inputs
# Done:: add arg_parser to control Content directory path, allow users to override it

# TODO:: logger
# DONE:: create a logger management

# TODO:: configuration manager
# DONE:: create a configuration manager logic, which should be something similar to singelton
# DONE:: add template file there
# Done:: add output file there, this is problematic as the output is part of the logger_management setting which get init before!

# TODO:: register manager
# Done:: refactor register_manager to support both x86 and riscv registers !
# Done:: in riscv, when using get try providing t_registers, and when using get_and_preserve try providing s_registers
# TODO:: enhance riscv register manager, to better allocate temp, saved, and other register types
# TODO:: preserve a base_register, need to be per scenario, stored as a state field