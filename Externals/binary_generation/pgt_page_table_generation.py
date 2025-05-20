import os
import re
import sys
import shutil
from Utils.configuration_management import get_config_manager
from Utils.logger_management import get_logger

def run_PGT_prototype():
    """
    Imports necessary modules from the PGT environment and calls the setProfile function.
    """
    os.environ["PGT_HOME"] = "/some_path/"
 
    logger = get_logger()

    pgt_home = os.environ.get("PGT_HOME")
    bin_path = os.path.join(pgt_home, "bin", "PGT_UCS4")
    src_path = os.path.join(pgt_home, "src")

    if bin_path not in sys.path:
        sys.path.append(bin_path)
    if src_path not in sys.path:
        sys.path.append(src_path)


    try:
        #import _pgt as pgt
        from _pgt import setProfile, createPlatformMemoryManager, UNTAGGED, addMemory, pgtSetTargetInfo, IS_RME_IMPLEMENTED
        from _pgt import createGranuleProtectionTable, createGptAttributes, createMemoryManager, mapGpt, setMemoryManager
        from _pgt import createAddress, ROOT_PAS, SIZE_512MB, setGptTableMemoryManager, createStg1TS, VMSAv8_64, PL3R, PL3, PL1_RW
        from _pgt import createMmuAttributes, getOutputAddr, generateOutputs, setVerbosity, WARN, ERROR, PL1NS, SET, REALM, SECURE, NON_SECURE
        from _pgt import setGpt, setAutoGptFlag, getAddressObjectValue, blockMemory, blockNamedMemory, mapWithPA, XN_CLEAR, RW_RW, USR_RW, TRUE, FALSE
        from _pgt import setPgtOutputFileFormat, ARM_ASSEMBLY, GENERIC
        from _pgt import Dev, Dev_GRE, Dev_nGnRnE, mapDevice


        from helperFunctions import V9A, V8A, setGptProperties, OUT_SH, CACHE_NON, CACHE_NON # *
        from helperFunctions import setTranslationSystemProp, FillStage1BlockAttributes, ROOT
        from helperFunctions import SIZE_4KB, SIZE_64KB, SIZE_2MB, SIZE_1GB, TG_4KB, TG_64KB, PGS_4KB, PA_48_BITS
        from helperFunctions import map as pgt_map, acquireMemory

        #from customer_mem_map import pgtInitPlatformMemoryMap # *


        setProfile(V9A)
        logger.info("---- Creating Platform Memory Manager - Physical_Stage1_Mapping ::  EL3, ROOT, Stage1") 
        print ("*****************************************************************************************")
        print ("*****  Page Table Generation Started  *****")
        
        
        PMM = createPlatformMemoryManager("pmm", UNTAGGED) # will handle the physical memory
        # VMM = createMemoryManager("vmm", UNTAGGED) # will handle the virtual memory

        # # add a memory region of size 0x1000, va = 0xa000, pa = 0xb000
        # addMemory(VMM, 0x0 , 0x0000180000000 )

        # code_va_addr = 0xa000
        # code_va = acquireMemory(VMM, 0x1000, lower_bound=code_va_addr, upper_bound=code_va_addr + 0x1000, NS=NON_SECURE)

        # code_pa_add = 0x1000
        # code_pa = acquireMemory(PMM, 0x1000, lower_bound=code_pa_addr, upper_bound=code_pa_addr + 0x1000, NS=NON_SECURE)


        print(f"PMM: {PMM}")
        addMemory(PMM, 0x0 , 0x0000180000000 )
        blockMemory(PMM, 0x0 , 0x80000000 ) # block the lower 2GB of memory - leave a section for the TRICKBOX
        blockNamedMemory(PMM, "TRICKBOX", 0x0, 0x14000000) # block the TRICKBOX region

        if(PMM < 0) :
                print ("PGT ERROR : initTarget failed")
                sys.exit(0)

        setVerbosity(WARN)

        pgtSetTargetInfo(IS_RME_IMPLEMENTED, TRUE) # enable RME to allow ROOT and REALM memory regions support

        # create EL3 translation system
        EL3 = createStg1TS("EL3", VMSAv8_64, PL3R)
        setTranslationSystemProp(EL3, TG0=TG_4KB)#, T0SZ=16)
        setMemoryManager(EL3, PMM)


        print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz need to seperate logic per state, and add the PMM and VMM into the state")
        print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz need to seperate logic per state, and add the PMM and VMM into the state")
        # Call create_automated_memory_mapping and capture the returned pages

        pages = create_automated_memory_mapping(EL3)
        print(f"Successfully processed {len(pages) if pages else 0} pages")


        setPgtOutputFileFormat(GENERIC) # GENERIC or ARM_ASSEMBLY
        generateOutputs()


        # PGT tool dump its files at the current working directory. moving it into output/pgt/ 
        config_manager = get_config_manager()
        output_dir = config_manager.get_value('output_dir_path')
        pgt_output_dir = os.path.join(output_dir, "pgt")
        os.makedirs(pgt_output_dir, exist_ok=True)      
        current_dir = os.getcwd() # 
        # Move files from current directory to output directory
        for filename in ["pg.s", "pg.h", "pg.json", "pg.scat", "pg.dat", "pg.hs", "pg_generic.s", "pg_generic.hs"]:
            src_path = os.path.join(current_dir, filename)
            dst_path = os.path.join(pgt_output_dir, filename)
            
            if os.path.exists(src_path):           
                shutil.move(src_path, dst_path)

        # Convert generic assembly to GNU format and also try to assemble it
        gnu_asm_path = convert_generic_to_gnu()
        
        # # Generate an automated linker script based on the processed pages
        # linker_script_path = generate_automated_linker_script(pages)
        # print(f"Generated automated linker script at: {linker_script_path}")
        
        print ("*****  Page Table Generation Complete  *****")
        print ("*****************************************************************************************")



    except ImportError as e:
        print(f"Error importing PGT modules: {e}")
        print(f"Make sure PGT_HOME is correctly set to: {pgt_home}")
        raise RuntimeError(f"Error importing PGT modules: {e}")
    except AttributeError:
        print("Error: setProfile function not found in _pgt module.")

    return 


def convert_generic_to_gnu():
    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    pgt_output_dir = os.path.join(output_dir, "pgt")
    
    input_file = os.path.join(pgt_output_dir, "pg_generic.s")
    output_file = os.path.join(pgt_output_dir, "pg_generic_gnu.s")
    
    # Extract PGT labels and values
    label_values = {}
    with open(input_file, 'r') as infile:
        for line in infile:
            line = line.strip()
            if line.startswith("ASM_LABEL") and "ASM_DCQ" in line:
                parts = line.split("ASM_LABEL")[1].split("ASM_DCQ")
                if len(parts) == 2:
                    label = parts[0].strip()
                    if label.startswith("(") and label.endswith(")"):
                        label = label[1:-1].strip()
                    
                    value = parts[1].strip()
                    if value.startswith("(") and value.endswith(")"):
                        value = value[1:-1].strip()
                    
                    label_values[label] = value
    
    # Write the converted file
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        outfile.write("// Auto-generated from pg_generic.s\n\n")
        outfile.write(".text\n\n")
        
        for line in infile:
            line = line.strip()
            
            if not line:
                outfile.write("\n")
                continue
            
            if line.startswith("#include"):
                outfile.write(f"// {line}\n")
                continue
                
            if line.startswith("ASM_AREA_CODE_M"):
                section_name = line.split("(")[1].split(")")[0].strip()
                outfile.write(f".section .text.{section_name.lower()}\n")
                continue
                
            if line.startswith("ASM_AREA_DATA_RW"):
                section_name = line.split("(")[1].split(")")[0].strip()
                outfile.write(f".section .data.{section_name.lower()}\n.align 3\n")
                continue
                
            if line.startswith("ASM_ALIGN"):
                alignment = line.split("(")[1].split(")")[0].strip()
                outfile.write(f".align {alignment}\n")
                continue
                
            if line.startswith("ASM_EXPORT"):
                symbol = line.split("ASM_EXPORT")[1].strip()
                outfile.write(f".global {symbol}\n")
                continue
                
            if line.startswith("ASM_LABEL"):
                label = line.split("(")[1].split(")")[0].strip()
                outfile.write(f"{label}:\n")
                continue
                
            if "ASM_DCQ" in line:
                value = line.split("ASM_DCQ")[1].strip()
                if value.startswith("(") and value.endswith(")"):
                    value = value[1:-1].strip()
                outfile.write(f"    .quad {value}\n")
                continue
            
            # Any other lines, add as comments
            if line:
                outfile.write(f"    // {line}\n")
    
    # Create a simple constants file with the symbols defined directly
    constants_file = os.path.join(pgt_output_dir, "pgt_constants.s")
    with open(constants_file, 'w') as f:
        f.write("// PGT Constants defined as global variables\n")
        f.write(".section .data\n")
        f.write(".align 3\n\n")
        
        # Define each constant as a global variable
        for label, value in label_values.items():
            f.write(f".global {label}\n")
            f.write(f"{label}:\n")
            f.write(f"    .quad {value}\n\n")
    
    print(f"Converting {input_file} to GNU format at {output_file}")
    print(f"Generated constants file at {constants_file}")
    
    return output_file


def create_automated_memory_mapping(EL3):
    """
    Create memory mappings using the automated approach by processing existing pages.
    """
    print("Using automated memory mapping approach")
    
    from Tool.state_management import get_current_state
    from Utils.configuration_management import Configuration

    #import _pgt as pgt
    from _pgt import createAddress, PL3R, PL1_RW, createMmuAttributes, mapWithPA, XN_CLEAR, mapDevice, Dev, Dev_nGnRnE, ROOT
    from helperFunctions import setTranslationSystemProp, FillStage1BlockAttributes, ROOT, SIZE_2MB

    
    # Get current state and page table manager
    current_state = get_current_state()
    page_table_manager = current_state.page_table_manager
    memory_manager = current_state.memory_manager
    

    # Trickbox device memory 
    trickbox_size = SIZE_2MB               
    trickbox_va = createAddress(0x0) 
    trickbox_attr = createMmuAttributes()
    FillStage1BlockAttributes(trickbox_attr, NS=ROOT, XN=XN_CLEAR, AP=PL1_RW, MEM_ATTR_OUTER=Dev, MEM_ATTR_INNER=Dev_nGnRnE)
    mapDevice(EL3, "TRICKBOX", trickbox_va, trickbox_size, trickbox_attr)


    all_pages = page_table_manager.get_page_table_entries()
    print(f"Found {len(all_pages)} pages in page table")
    
    # Group pages by type for better handling
    code_pages = page_table_manager.get_page_table_entries_by_type(Configuration.Page_types.TYPE_CODE)
    data_pages = page_table_manager.get_page_table_entries_by_type(Configuration.Page_types.TYPE_DATA)
    
    print(f"Processing {len(code_pages)} code pages and {len(data_pages)} data pages")
     
    # Create PGT mappings for code pages
    for idx, page in enumerate(code_pages):
        print(f"Processing code page {idx}: {page}")
        code_size = page.size
        code_va = createAddress(page.va) 
        code_pa = createAddress(page.pa) 
        #code_pa_addr = 0x90000000 # createAddress(0xb0000000)   # Pick a suitable PA address
        #code_pa = acquireMemory(PMM, code_size, PA_LOWER_BOUND=code_pa_addr, PA_UPPER_BOUND=code_pa_addr + code_size) # this will acquire the memory 
        code_attr = createMmuAttributes()
        FillStage1BlockAttributes(code_attr, NS=ROOT, XN=XN_CLEAR, AP=PL1_RW)
        #pgt_map(EL3, code_va, code_size, code_attr)
        mapWithPA(EL3, code_va, code_pa, code_size, code_attr)

    # Create PGT mappings for data pages
    for idx, page in enumerate(data_pages):
        print(f"Processing data page {idx}: {page}")
        data_size = page.size
        data_va = createAddress(page.va) 
        data_pa = createAddress(page.pa) 
        #code_pa_addr = 0x90000000 # createAddress(0xb0000000)   # Pick a suitable PA address
        #code_pa = acquireMemory(PMM, code_size, PA_LOWER_BOUND=code_pa_addr, PA_UPPER_BOUND=code_pa_addr + code_size) # this will acquire the memory 
        data_attr = createMmuAttributes()
        FillStage1BlockAttributes(data_attr, NS=ROOT, XN=XN_CLEAR, AP=PL1_RW)
        #pgt_map(EL3, code_va, code_size, code_attr)
        mapWithPA(EL3, data_va, data_pa, data_size, data_attr)


    print(f"Completed memory mapping process")
    # All of these pages are now available for the test to use via memory_manager





        # elif example == "EL3_Stage1_GPT_Mapping":
        #     setProfile(V9A)
        #     PMM = createPlatformMemoryManager("pmm", UNTAGGED)
        #     addMemory(PMM, 0x000000000000 , 0x0000100000000 )
        #     if(PMM < 0) :
        #             print ("PGT ERROR : initTarget failed")
        #             sys.exit(0)
        #     # PMM = Memory Manager ID predefined to be used for accessing Platform Memory Map
        #     PMM = 0

        #     pgtSetTargetInfo(IS_RME_IMPLEMENTED, True)

        #     #Create & configure GPT
        #     GPT = createGranuleProtectionTable("GPT");
        #     setGptProperties(GPT, PGS=PGS_4KB, PPS=PA_48_BITS, SH=OUT_SH, IRGN=CACHE_NON, ORGN=CACHE_NON)

        #     #Create & configure GPT Attributes
        #     gptAttrID = createGptAttributes()

        #     #Create table MM for GPT
        #     GMM = createMemoryManager("GMM", UNTAGGED)        
        #     addMemory(GMM, 0x40000000, 0x60000000)
        #     mapGpt(GPT, createAddress(0x40000000), ROOT_PAS, SIZE_512MB, gptAttrID, 1)
        #     setGptTableMemoryManager(GPT, GMM)                      

        #     # Create, Config, map STAGE1+STAGE2 TS
        #     S1TS=createStg1TS("S1TS", VMSAv8_64, PL3R)
        #     setTranslationSystemProp(S1TS, TG0=TG_4KB)
        #     stage1_attr=createMmuAttributes()
        #     FillStage1BlockAttributes(stage1_attr, NS=ROOT)
        #     pgt_map(S1TS, createAddress(0x3000000), SIZE_2MB, stage1_attr, 8)
        #     paID = getOutputAddr(S1TS, createAddress(0x3000000))

        #     #Gpt mappings for S1TS PA
        #     mapGpt(GPT, paID, ROOT_PAS, SIZE_1GB, gptAttrID, 1)

        # elif example == "EL3_Stage1_Automatic_GPT_Mapping":
        #     setProfile(V9A)
        #     PMM = createPlatformMemoryManager("pmm", UNTAGGED)
        #     addMemory(PMM, 0x000000000000 , 0x0000100000000 )
        #     if(PMM < 0) :
        #             print ("PGT ERROR : initTarget failed")
        #             sys.exit(0)
        #     # PMM = Memory Manager ID predefined to be used for accessing Platform Memory Map
        #     PMM = 0
        #     setVerbosity(ERROR)

        #     pgtSetTargetInfo(IS_RME_IMPLEMENTED, True)

        #     #Create & configure GPT
        #     GPT = createGranuleProtectionTable("GPT");
        #     setGptProperties(GPT, PGS=PGS_4KB, PPS=PA_48_BITS, SH=OUT_SH, IRGN=CACHE_NON, ORGN=CACHE_NON)
        #     setAutoGptFlag(SET)
        #     setGpt(PMM, GPT)

        #     #Create table MM for GPT
        #     GMM = createMemoryManager("GMM", UNTAGGED)
        #     paID = acquireMemory(PMM, 0x200000, SECURITY=ROOT)
        #     addMemory(GMM, getAddressObjectValue(paID), getAddressObjectValue(paID) + 0x200000)
        #     setGptTableMemoryManager(GPT, GMM)                      

        #     # Create, Config, map STAGE1 TS
        #     S1TS=createStg1TS("S1TS", VMSAv8_64, PL3R)
        #     setTranslationSystemProp(S1TS, TG0=TG_4KB)
        #     stage1_attr=createMmuAttributes()
        #     FillStage1BlockAttributes(stage1_attr, NS=ROOT)
        #     pgt_map(S1TS, createAddress(0x0), SIZE_4KB, stage1_attr)
        #     FillStage1BlockAttributes(stage1_attr, NS=REALM)
        #     pgt_map(S1TS, createAddress(0x8000), SIZE_4KB, stage1_attr)
        #     FillStage1BlockAttributes(stage1_attr, NS=SECURE)
        #     pgt_map(S1TS, createAddress(0xc000), SIZE_4KB, stage1_attr)
        #     FillStage1BlockAttributes(stage1_attr, NS=NON_SECURE)
        #     pgt_map(S1TS, createAddress(0x10000), SIZE_4KB, stage1_attr)

