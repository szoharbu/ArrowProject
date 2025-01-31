''' ----------------- Arrow hierarchy:
ArrowProject/
├── Arrow/                      # Main package for the tool
│   ├── main.py                 # Entry point for the tool
│   └── TODOs                   # Endless list of TODOs
├── Tool/                       # Core logic of the tool
│   ├── asm_blocks/             # Basic asm building blocks - AsmUnit and DataUnit
│   ├── asm_libraries/          # Native assembly flows, like Loop, EventTrigger, Branch...
│   ├── frontend/               # FE operations and interface
│   ├── stages/                 # Tool stages of pre,body and post generation
│   └── ...MGMs                 # Tool managers for generation, ingredient, scenario, memory, register,...
├── Utils/                      # Utility logic of the tool, like Argparse, logger, Configs, Knobs
│   ├── arg_parser/             # Command-line interface
│   ├── configuration_mgm/      # Another standalone repository
│   └── ...                     # Additional files like: logger, seed, singleton
├── external/                   # External repositories
│   ├── db_manager/             # Per-Arch instruction DB
│   ├── binary_generation/      # Per-Arch binary generation
│   ├── streamlit/              # Streamlit-specific front-end logic
│   └── run_tool.py             # External entry point for the tool
├── Submodules/                 # External repositories
│   ├── arrow_content/          # External content repository
│   │   ├── content/            # Content directories, including Templates, Scenarios, Ingredients
│   │   ├── regressions/        # Content directories, including Templates, Scenarios, Ingredients
│   └── ...                     # TBD - Additional external repos
├── tests/                      # Unit and integration tests
├── scripts/                    # Utility scripts
├── requirements.txt            # Dependencies for the project
├── setup.py                    # Setup script for packaging
├── LICENSE                     # GPL-3.0 open source licensing
└── README.md                   # Overview and usage instructions


'''

# TODO:: disconnect google cloud - need to disable its billing

# Done:: add knobs for gen_stages full or gen only , need to think of a good name
# Done:: add some identifier to airtable statistics, so I see if two different users run it.
# TODO:: add riscv compilation


# Done:: add alignment in riscv assembly
# Done:: enforce python 3.12 version or higher, error if not


# TODO:: upload statistics into cloud
    # Done:: add Airtable table and infrastructure + create upload function
        # URL = "https://api.airtable.com/v0/appOJKrcvb4gxH65d/run_statistics"
    # Done:: hide private_TOKEN - using PythonAnywhare API
        # URL = "szoharbu.pythonanywhere.com"
    # Done:: add knobs for upload


# Done:: add internal content repository, which can be added to the external one
# TODO:: improve the Readme.getting started section

# Done:: move db_manager into External repos
# TODO:: refactor User interface and importing!!!! replace usage of AR, Sources, StateManager, Tool imports

# TODO:: implement an array function, that user can set values in X elements, and access they via next, and the memory will get mem + offset
# TODO:: enhance C code function, allow them to receive parameter, and protect all registers usage (or provide a list of allowed GPR which will be the free ones)
# Done:: Reuse memory in some probability instead of generating new ones

# TODO:: extract arm and x86 instruction set

# TODO:: add API to extract queries, should be similar to generate logic
# TODO:: Add API and package under wrapper to upload info to a generic cloud

# TODO:: have a scenario wrapper, later place free_GPR checks there to error when a register wasn't free

'''
Directions:
- Architecture agnostic TG, simple, lite and fast
- Open source, monetize via ? support | advance features like Cloud,MemMgr,MultiCore | ???
    - open all or just peripheral?
- Quick and simple usage via StreamLit API
- Allow users to extend content, utils,
- Map all to Asm/DataUnits, to simplify assembly creation, and later rebuild it
- Cpp integration
- Cloud upload, Authentication?
'''

'''
learning:

ARM learning 
- We can use CPULATOR to run and test ARM and RISCV architecture, and run it step by step 
- in arm, CSPR is the equivalent of eflags, yet not all instructions uses it.  
    for example, if we want ADD instruction to use it, need to write ADDS. 
    TODO:: see how to integrate it as part of generate 
- in arm, only selective few instruction touches memory (like LDR, STR), unlike x86, 
    we can use "ldr r1, =label" to set r1 with the address of the memory label (similar to LINADDR), and later we can "ldr r0, [r1]" which will get the stored value from memory 
    TODO:: see how to take this into calculation, as also the registers are very limited, so maybe heavily rely on stack?  

RISCV learning 
- use RARS jave tool, simply run 'java -jar rars1_6.jar' to open the tool (under C:\\RARS_riscv_assembler directory) 
- in the tool "help" there is a list of all RISVC ISA TODO:: need to convert it into db
- start assembling and clean issues    
# Done:: convert RARS ISA into a json that fit the DB
# Done:: pass assembly and simulation
'''

# Done:: remove op1,op2, and enhance query to understand src/dest reg/mem types
# TODO:: integrate streamlit and deploy it
# TODO:: in riscv add I (integer content) , R, arithmetic  and pesudo stress bursts
# Done :: RISCV ending convention

# TODO:: Arch-Agnostic content writing
# TODO:: Implement a function to store values into operands! will make code arch-agnostic
###AR.asm(f'li {reg}, {recursive_count}', comment=f"set the value of {recursive_count} into {reg}")
# Done:: Implement a function to push/pop values to stack! will make code arch-agnostic
###AR.asm(f'addi, sp, sp, -4', comment=f"Decrement stack pointer (allocate space)")
###AR.asm(f'sw {reg}, 0(sp)', comment=f"Store the value of t0 at the top of the stack")
# TODO:: Implement a function to branch to different locations! will make code arch-agnostic
###AR.asm(f'jal ra, {self.fibonacci_block.code_label}', comment=f"Call fib(n)")
# Done:: add capability to ask for specific register base on enumeration, like SP, RA in riscv , to use reg object instead of string
# TODO:: add "push {r1, r2}" and "pop {reglist} into arm.json and support it cd

# Done:: For evert arch, check if assembler, compiler, linker exist, if not warning and stop progress. And add knobs for needed behavior

# TODO:: restructure directories and hierarchies
# TODO:: change directory to distinguish tool internal from external plug-ins
# TODO:: refactor code to distinguish what should be internal (like scenario or ing logic) vs external and open source (like Loop, generate asm,...)
# TODO:: in the new TG, create a hierarchy and separation between the tool and external scripts and libraries
#       some logic, like how to DB, along with the initial json.create
#       other logic like how to assembly or link the files - all should be open for users to view and modify if need
#       even the asm_creation logic, from AsmUnits to the different sections, with the specific "nasm" or "gas" logic...
#       and of course directories like content, regressions, ...
# Done:: Work to define appropriate open source license, and update README, NOTICE, LICENSING and CONTRIBUTING files.

# Done:: Logger
# Done:: replace and improve logger_management functionality!

# TODO::Cloud and streamLit
    # TODO:: explore google firebase for stats upload and possibly authentication
    # Done:: run basic test
    # TODO:: create a better page structure
    # Done:: fix bug with num_core when run under streamlit
    # TODO:: control configurations knobs
    # TODO:: python and internal highlighting
    # TODO:: show APIs, mnemonics,...
    # Done:: add logic to differentiate standalone/cloud -> cloud doesn't need post run assembler and linker.
    # TODO:: add logic to differentiate elf vs baremetal -> eld doesn't need boot and memory struct.
    # TODO:: consider providing an option for user to generate the asm on remote, which include compilation and all, and to receive an elf file as output.

# TODO:: draw block-diagram using draw.io , and create a high level components and relationship flow
# TODO:: Copy arm, riscv mnemonic from manual
# TODO:: add more tkl like branch or push
# TODO:: try to replace and start using Logger and event_manager
# TODO: cloud statistics
# TODO:: upload static information on every run to grafana and grafana Loki


# Done:: eliminate next_ingredient prints by planting the AsmUnit at a later stage

# TODO:: install x86 assembler and linker, and work to clean asm syntax issues
# TODO:: install riscv assembler and linker, and work to clean asm syntax issues
# TODO:: add get_partial to register manager to supported working with 8/16/32bits registers

# TODO:: understand test/template name, so I can use the name and generate test.obj, test.lst,... files
# Done:: review code_switching flow
# Done:: implement inspect to track line number and add it as part of the generation.log

# TODO:: see how to create licensing logic in the tool
# TODO:: Execution::
# TODO:: login into SiFive, using AlonM password
# TODO:: see how to convert asm to obj file, and then convert it to an elf executable file
# Done:: see if we can get memory paging from the elf logic

# TODO:: UX:: create packages separation, so instead of having all under TG, have multiple imports for the different usages, like import knob, import tkl, import API...
# TODO:: rename ingredients with sections!

# TODO:: go over the code, start to finish and clean unwanted code
# Done:: refactor all imports!!, inside the tool folder, avoid using Tool.<somthing> and best to access it with relative path Tool.something.something

# Done:: add time-stamp
# Done:: add file and line number
# TODO:: understand how to do releases
# Done:: create a memory_json log to track all used/allcoated memory, and build used intervals and data if needed
# TODO:: create an external input file for user configuration, like core_count, architecture, forbid-range

# BUGS!!!
# DONE:: fix scenario biasing (in test_stage/do_scenario) to take input from scenario_query knob and not hard-coded
# DONE:: fix a bug when using core_count > 1, some bug with state_manager

# Done:: DIRECT!!!
# DONE:: create a direct version template!

# QUESTIONS?
# Done:: decide what to do with TG_API to decouple all the TOOL.XXX UX APIs
# TODO:: link python installation and retry to build a release using setup.py

# TODO:: Database, Peewee and smart generate
# DONE:: do pip install peewee, implement a function that convert the json into an sql db
# DONE:: make sure querying is working as expected
# DONE:: do a function that extract entries based on query
# TODO:: extract riscv from riscv-opcode github repo
# Done:: create x86 db, enhance generate_x86 to start using query
# Done:: create arm db, enhance generate_arm to start using query
# Done:: in DB, add another flavor not to randomize certain instructions, like branch with label
# TODO:: review DB entries in x86 and riscv json file, and set relevant instruction with "random_generate": "False"


# TODO:: Generate
# TODO:: WIP:: enhance generate to get valid entries, and generate it
# Done:: improve generate to take src/dest operands into account and provide relevant queries


# TODO:: ASM_UNIT
# Done:: refactor asm writing logic into using asm_units that will be published only at test end.
# Done:: modify code_blocks to maintain list of asm_units.
# Done:: modify generate, comment and asm to add items to code_block list. using event_manager?
# TODO:: enhance logic to use hints, like linears, mem type, ...
# TODO:: rewrite asm_logger to initiate only at post stage. delete existing
# Done:: At test end, create a json with all code blocks and units. Enhance comments based on hint link memtype and linear address,...
#       And print the final as file. Should be easy as arm and risk has fix instr sizes
# Done:: create a generation.json log
# TODO:: decide if looger is still needed as is? or move it to a later time


# TODO:: Arch-agnostic support
# DONE:: create correct hierarchy to separate between Arm and riscv, where is the correct place to do it all??
# Done:: create an Arch state, and precondition scenarios based on that tags
# TODO:: Optional? support user-defined area per Arch, where they can override it and add their notation
# Done:: UX:: refactor Architecture query, and use Config.Arch.<x86/riscv> to provide bool

# Done:: branch_to_segment API
# Done::  enhance BranchToSegment to use call-ret when inside a with scope, and jump when run as one-way without a with scope
# Done:: later, replace the logic in the test_body to use one-way instead of with-scope
# Done:: separate logic between riscv and x86, use riscv mnemonics
# Done:: fix the issue that standalone require func()() instead of just one instantiation.

# TODO:: arg parser
# DONE:: take care of output directory and other command line inputs
# TODO:: Logger get called before argparser, which avoid replacing the output directory
# TODO:: override knob_manager values from the command line
# Done:: move arg_parser sooner
# Done:: add arg_parser to control Content directory path, allow users to override it


# TODO:: Stages
# DONE:: create separate stages for init, body, final
# TODO:: improve the inner code that switch between cores, and call scenarios
# TODO:: create a scenario_wrapper with logic

# TODO:: state manager
# DONE:: implement basic logic of state_manager
# DONE:: implement switch_state function under TKL
# Done:: preserve a base_register, need to be per scenario, stored as a state field
# Done:: refactor memory logic, allocate 2G range pre core, then allocate boot_code, code, data segments, reserve a GPR to point to range base
# Done:: improve state_manager to be more core oriented, and hold additional core info. add logic to allocate memory region per core, and allocate base_reg
# TODO:: Need to make sure its working, and switching register/memory mangers every switch_state
# TODO:: in many places, use the current_state to extract info like active_code_segment and such

# TODO:: configuration manager
# TODO:: improve knob_manager to override assignment "=" operator, and fix issues I have there
# DONE:: create a configuration manager logic, which should be something similar to knob manager just make it a read_only dictionary!
# DONE:: add template file there
# TODO:: add output file there, this is problematic as the output is part of the logger_management setting which get init before!

# TODO:: flavor manager
# TODO:: add flavor manager logic, the ability to cluster several ings into a single story

# TODO:: knob manager
# DONE:: add all knobs at certain locations, create a simpler API
# DONE:: modify the knob manager read_only attributes not to set the parameter at start, first need to reach the inputs, template ans such
#        and only later set those that are not defines at the evaluate stage and then block them for read only!
# DONE:: add control from command line

# TODO:: event-manager
    # TODO:: need to create an event-manager with publish and registers, ...

# Done:: add a wrapper script to run regression


# TODO:: ingredinet manager
    # Done:: need to add priority weight logic to scenario selection. at the moment it only check tags and precondition
    # Done:: need to add priority weight logic to ingredient selection. at the moment it only check tags and precondition
    # TODO:: need to figure out pros-cons of using ScenarioDecorator and ScenarioWrapper VS using just IngredientDecorator
    # TODO:: add an ingredientWrapper with add_precond logic, and add the return type List[IngsWrapper] to get_random_ingredients
    # Done:: Add boot section as part of ingredients. That will be pushed to the json

# TODO:: register manager
    # Done:: refactor register_manager to support both x86 and riscv registers !
    # Done:: in riscv, when using get try providing t_registers, and when using get_and_preserve try providing s_registers
    # TODO:: enhance riscv register manager, to better allocate temp, saved, and other register types
    # TODO:: preserve a base_register, need to be per scenario, stored as a state field

# TODO:: memory manager
    # DONE:: create a memlib with interval logic, and use it at Memory_block initialization
    # Done:: preserve a base_register, need to be per scenario, store as a state field. and ensure memory access are using it
    # TODO:: improve heuristics to allocate memory per core, and maintain linear and physical separation
    # Done:: create memory manager with code and data blocks, separation between code, data, boot
    # Done:: create memory pools for shared and reserved, add shared=true logic
    # TODO:: add heuristics to understand initial logic, take forbiden_range into consideration
    # Done:: enhance Memory operand returned object
    # Done:: in Memory, when in x86, add qword/dword and other hints to assembler
    # Done:: Memory : use dynamic init when memory get generated
    # Done:: Memory : add unique name to each of the requested memory, also when name is provided (maybe have 2 attributes name and unique_name)
    # TODO:: currently memory always uses dynamic_init and later [reg] , need to add offset capabilities
    # Done:: create a memoryBlock, and allow each Memory to be part of a memory block, if Memory is generate without a memoryBlock auto define a block of that size
    # Done:: reuse bigger blocks, and take partial blocks to reuse label with preserved registers
    # Done:: refactor DataUnit to work with Byte_representation instead on huge integer.
    # TODO:: If someone if printing it should print all the information, and provide an api for mem.label_reg(reg) that will print the memory operand like 0(reg).
            # Also replace all such previous usages when in baremetal we need different logic
    # Done:: NEED TO MAKE SURE DATAUNIT AND ASM GENERATION TREAT THE MEMORY BLOCK AND ALL ITS SIZES CORRECTLY AND SEQUENTIALLY!!!!!!!!!!!!!!!!


# TODO:: scenario manager
    # TODO:: review the way the manager get initiated
    # DONE:: need to check scenario distribution, in some cases it doesn't seem like its calculate logic right
    # DONE:: need to add priority logic in place, at the moment its looking at tags only!

# TODO:: APIs
    # Done:: UX:: create Event Trigger
    # Done:: separate Memory from MemoryBlock
    # Done:: implement rangeWithPeak
    # TODO:: add more APIs, like event_trigger, Branch, function, safe_regs,...
    # Done:: add comment into AR.asm("nop",comment="nop instruction")
    # Done:: move choices, rangeWithPeak from Tool to Utils
    # Done:: add Adaptive_choice in addition to Choice to support less uniform behavior and extend random variations.

# TODO:: AR API
    # DONE:: decouple FE from Tool, create additional TG class from the Tool class, and all init will be there
    # TODO:: migrate more APIs to be under AR. migrate content toward it
    # TODO:: need to think what to do with decorators and such?

# TODO:: Instructions
    # Done:: take care of ISA DB queries to enhance generate
    # Done:: enhance generation based on query results
    # TODO:: have an instruction object, to append either instruction object with mnemonics,operands,... or pure string and later asm print it
    # TODO:: reduce usage of print_asm and instead use generateInstruction
    # TODO:: add another layer on top of AsmUnit called Instruction, that hold the string as well as the AsmUnit inside. not sure its a good idea to use raw AsmUnit. yet how will it work with TG.asm?

# TODO:: Tagging
    # Done:: add tagging and precondition logic to scenarios
    # Done:: add tagging and precondition logic to ingredient as well
    # Done:: in tags query, support both dict and list


# Done:: seed consistency
# Done:: create a mini_regression wrapper
