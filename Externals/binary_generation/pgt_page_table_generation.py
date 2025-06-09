import os
import random
import sys
import shutil
from Tool.state_management import get_state_manager
from Utils.configuration_management import get_config_manager
from Utils.logger_management import get_logger
from Tool.memory_management.memory_logger import get_memory_logger


def run_PGT_prototype():
    """
    Imports necessary modules from the PGT environment and calls the setProfile function.
    """
    os.environ["PGT_HOME"] = "/home/scratch.zbuchris_cpu/wa_pgt/hw/ext_ip/arm/V8/ack_oct24__r6p0-00eac0_olym/validation/fastpgt/Interface/Release"
 
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
        from _pgt import createAddress, ROOT_PAS, SIZE_512MB, setGptTableMemoryManager, createStg1TS, createStg2TS, createVirtStg1TS, mapAlias, getLeafBlock
        from _pgt import VMSAv8_64, PL3R, PL3, PL2R, PL2S, PL2NS, PL1_RW, PL1NS, LEVEL_0
        from _pgt import createMmuAttributes, getOutputAddr, generateOutputs, setVerbosity, WARN, ERROR, PL1NS, SET, REALM, SECURE, NON_SECURE
        from _pgt import setGpt, setAutoGptFlag, getAddressObjectValue, blockMemory, blockNamedMemory, mapWithPA, XN_CLEAR, RW_RW, USR_RW, TRUE, FALSE
        from _pgt import setPgtOutputFileFormat, ARM_ASSEMBLY, GENERIC
        from _pgt import Dev, Dev_GRE, Dev_nGnRnE, mapDevice

        from helperFunctions import V9A, V8A, setGptProperties, OUT_SH, CACHE_NON, CACHE_NON # *
        from helperFunctions import setTranslationSystemProp, FillStage1BlockAttributes, ROOT
        from helperFunctions import SIZE_4KB, SIZE_64KB, SIZE_2MB, SIZE_1GB, TG_4KB, TG_64KB, PGS_4KB, PA_48_BITS


        memory_logger = get_memory_logger()
        memory_logger.info(f"\n\n") 
        memory_logger.info(f"---- Creating Platform Memory Manager - Physical_Stage1_Mapping ::  EL3, ROOT, Stage1",print_both=True) 
        memory_logger.info(f"*****  Page Table Generation Started  *****") 


        '''
            - idealy the tool should be able to randomize a EL and a matching paging structure. 
                -   EL3 stage1 - root  (done)
                -   EL2 stage1 - realm
                    -   start with EL3, load the EL2 MSRs, and then eret to el2 
                    - need top create another 
                            EL3 = createStg1TS(f"EL2", VMSAv8_64, PL2R/pl2S/pl2NS)  (realm/secure/non-secure))
                            setTranslationSystemProp(EL2, TG0=TG_4KB)
                            setMemoryManager(EL2, PMM)
                -   EL2 stage1 - secure   
                    -   start with EL3, load the EL2 MSRs, and then eret to el2 
                -   EL1 stage1+stage2 
                    - re
                


                        # STAGE1+STAGE2

                        EL1NS_2=createStg2TS("EL1NS_2", VMSAv8_64)
                        setTranslationSystemProp(EL1NS_2, TG0=TG_4KB, START_LEVEL=LEVEL_0)
                        stage2_attr=createMmuAttributes()
                        map(EL1NS_2, createAddress(0x1000000), SIZE_2MB, stage2_attr, 8)

                        EL1NS_1=createVirtStg1TS("EL1NS_1", VMSAv8_64, EL1NS_2, 0)

                        ipmm = createMemoryManager("ipmm", UNTAGGED)        
                        addMemory(ipmm, 0x1000000, 0x2000000)                  
                        setMemoryManager(EL1NS_1, ipmm)                      
                        setTranslationSystemProp(EL1NS_1, TG0=TG_4KB)

                        stage1_attr=createMmuAttributes()
                        map(EL1NS_1, createAddress(0x0), SIZE_4KB, stage1_attr) 
                        blk1 = getLeafBlock(EL1NS_1, createAddress(0x0))
                        mapAlias(EL1NS_1, createAddress(0x4000), SIZE_4KB, stage1_attr, blk1) 
       
        '''

        setProfile(V9A)
        
        PMM = createPlatformMemoryManager(f"pmm", UNTAGGED) # will handle the physical memory
        addMemory(PMM, 0x0 , 0x0000280000000 )
        blockMemory(PMM, 0x0 , 0x80000000 ) # block the lower 2GB of memory - leave a section for the TRICKBOX
        blockNamedMemory(PMM, "TRICKBOX", 0x13000000, 0x14000000) # block the TRICKBOX region

        if(PMM < 0) :
            raise RuntimeError("PGT ERROR : initTarget failed")

        setVerbosity(WARN)   

        state_manager = get_state_manager()
        cores_states = state_manager.get_all_states()
        for core_state in cores_states:
            state_manager.set_active_state(core_state)
            curr_state = state_manager.get_active_state()
            memory_logger.info(f"================ enable_mmu - running GPT for {curr_state.state_name}")

            pgtSetTargetInfo(IS_RME_IMPLEMENTED, TRUE) # enable RME to allow ROOT and REALM memory regions support

            # create EL3 translation system
            #EL3 = createStg1TS(f"EL3_{core_state}", VMSAv8_64, PL3R)
            EL3 = createStg1TS(f"EL3_{curr_state.state_name}", VMSAv8_64, PL3R)
            setTranslationSystemProp(EL3, TG0=TG_4KB)#, T0SZ=16)
            setMemoryManager(EL3, PMM)

            
            EL1NS=createStg1TS(f"EL1NS_{curr_state.state_name}", VMSAv8_64, PL1NS)
            #EL1NS=createStg1TS(f"EL1NS_{curr_state.state_name}", VMSAv8_64, PL1_RW)
            setTranslationSystemProp(EL1NS, TG0=TG_4KB, T0SZ=16)
            setMemoryManager(EL1NS, PMM)

            pages = create_automated_memory_mapping(PMM, EL3, EL1NS)

            memory_logger.info(f"Successfully processed {len(pages) if pages else 0} pages")
            memory_logger.info(f"================ enable_mmu - running GPT for {curr_state.state_name} - {len(pages) if pages else 0} pages were processed", print_both=True)


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
        
        memory_logger.info(f"*****  Page Table Generation Complete  *****\n\n")


    except ImportError as e:
        print(f"Error importing PGT modules: {e}")
        print(f"Make sure PGT_HOME is correctly set to: {pgt_home}")
        raise RuntimeError(f"Error importing PGT modules: {e}")
    except AttributeError as e:
        print(f"Error: Attribute error: {e}")
        raise RuntimeError(f"Error importing PGT modules: {e}")
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
        f.write(".section .data.pgt_constants\n")  # Use specific section name that matches linker script
        f.write(".align 3\n\n")
        
        # Define each constant as a global variable
        for label, value in label_values.items():
            f.write(f".global {label}\n")
            f.write(f"{label}:\n")
            f.write(f"    .quad {value}\n\n")
    
    memory_logger = get_memory_logger()
    memory_logger.info(f"Converting {input_file} to GNU format at {output_file}")
    memory_logger.info(f"Generated constants file at {constants_file}")
    
    return output_file


def create_automated_memory_mapping(PMM, EL3, EL1NS):
    """
    Create memory mappings using the automated approach by processing existing pages.
    """
    memory_logger = get_memory_logger()
    memory_logger.info("Using automated memory mapping approach")
    
    from Tool.state_management import get_current_state
    from Utils.configuration_management import Configuration

    #import _pgt as pgt
    from _pgt import createAddress, PL3R, KERN_RW, PL1_RW, createMmuAttributes, mapWithPA, XN_CLEAR, mapDevice, Dev, Dev_nGnRnE, ROOT, NON_SECURE
    from _pgt import blockMemory
    from helperFunctions import setTranslationSystemProp, FillStage1BlockAttributes, ROOT, SIZE_2MB, SIZE_4KB, Normal_WB_TRW
    
    
    # Get current state and page table manager
    current_state = get_current_state()
    core_page_tables = current_state.enabled_page_tables

   
    # Trickbox device memory 
    trickbox_size = SIZE_2MB               
    trickbox_va = createAddress(0x13000000) 
    trickbox_attr = createMmuAttributes()
    FillStage1BlockAttributes(trickbox_attr, NS=ROOT, XN=XN_CLEAR, AP=PL1_RW, MEM_ATTR_OUTER=Dev, MEM_ATTR_INNER=Dev_nGnRnE)
    mapDevice(EL3, "TRICKBOX", trickbox_va, trickbox_size, trickbox_attr)

    # PGT Constants region mapping (VA=PA identity mapping for EL3) 
    constants_size = SIZE_4KB * 4  # 16KB for constants  
    constants_va = createAddress(0x801c0000) # 4KB aligned for 16KB constants region
    constants_pa = createAddress(0x801c0000)
    constants_attr = createMmuAttributes()
    # Force ALL pages to use Normal memory - this will make PGT assign Normal to Attr0
    FillStage1BlockAttributes(constants_attr, NS=ROOT, XN=XN_CLEAR, AP=PL1_RW, MEM_ATTR_OUTER=Normal_WB_TRW, MEM_ATTR_INNER=Normal_WB_TRW)
    # Map in 4KB chunks to avoid 2MB block alignment issues
    for i in range(4):  # Map 4 x 4KB = 16KB
        chunk_va = createAddress(0x801c0000 + i * 0x1000)
        chunk_pa = createAddress(0x801c0000 + i * 0x1000)
        mapWithPA(EL3, chunk_va, chunk_pa, SIZE_4KB, constants_attr)
    memory_logger.info(f"Mapped constants region at VA=PA=0x801c0000, size=16KB using 4KB pages")

    for page_table in core_page_tables:
        all_pages = page_table.get_pages()
        memory_logger.info(f"Found {len(all_pages)} pages in page table at {page_table.page_table_name}")
    
        # Group pages by type for better handling
        code_pages = page_table.get_pages_by_type(Configuration.Page_types.TYPE_CODE)
        data_pages = page_table.get_pages_by_type(Configuration.Page_types.TYPE_DATA)
        
        memory_logger.info(f"Processing {len(code_pages)} code pages and {len(data_pages)} data pages")
     
        # Create PGT mappings for code pages
        for idx, page in enumerate(code_pages):
            context = page_table.execution_context
            # print(f"Processing {current_state.state_name}-{mmu.mmu_name} - code page {idx}: {page} in {context.value}")
            memory_logger.info(f"Processing {current_state.state_name} - {page_table.page_table_name} - code page {idx}: {page} in {context.value}")
            code_size = page.size
            code_va = createAddress(page.va) 
            code_pa = createAddress(page.pa) 
            blockMemory(PMM, page.pa, page.pa + page.size) # block the memory region from the PA region. 
            code_attr = createMmuAttributes()
            if context == Configuration.Execution_context.EL3:
                # Force ALL pages to use Normal memory - this will make PGT assign Normal to Attr0
                FillStage1BlockAttributes(code_attr, NS=ROOT, XN=XN_CLEAR, AP=PL1_RW, MEM_ATTR_OUTER=Normal_WB_TRW, MEM_ATTR_INNER=Normal_WB_TRW)
                mapWithPA(EL3, code_va, code_pa, code_size, code_attr)
            elif context == Configuration.Execution_context.EL1_NS:
                # Force ALL pages to use Normal memory - this will make PGT assign Normal to Attr0 
                FillStage1BlockAttributes(code_attr, NS=NON_SECURE, XN=XN_CLEAR, AP=KERN_RW, MEM_ATTR_OUTER=Normal_WB_TRW, MEM_ATTR_INNER=Normal_WB_TRW)
                mapWithPA(EL1NS, code_va, code_pa, code_size, code_attr)

        # Create PGT mappings for data pages
        for idx, page in enumerate(data_pages):
            context = page_table.execution_context
            # print(f"Processing {current_state.state_name}-{mmu.mmu_name} - data page {idx}: {page} in {context.value}")
            memory_logger.info(f"Processing {current_state.state_name}-{page_table.page_table_name} - data page {idx}: {page} in {context.value}")
            data_size = page.size
            data_va = createAddress(page.va) 
            data_pa = createAddress(page.pa) 
            blockMemory(PMM, page.pa, page.pa + page.size) # block the memory region from the PA region. 
            data_attr = createMmuAttributes()
            if context == Configuration.Execution_context.EL3:
                # Force ALL pages to use Normal memory - this will make PGT assign Normal to Attr0
                FillStage1BlockAttributes(data_attr, NS=ROOT, XN=XN_CLEAR, AP=PL1_RW, MEM_ATTR_OUTER=Normal_WB_TRW, MEM_ATTR_INNER=Normal_WB_TRW)
                mapWithPA(EL3, data_va, data_pa, data_size, data_attr)
            elif context == Configuration.Execution_context.EL1_NS:
                # Force ALL pages to use Normal memory - this will make PGT assign Normal to Attr0  
                FillStage1BlockAttributes(data_attr, NS=NON_SECURE, XN=XN_CLEAR, AP=PL1_RW, MEM_ATTR_OUTER=Normal_WB_TRW, MEM_ATTR_INNER=Normal_WB_TRW)
                mapWithPA(EL1NS, data_va, data_pa, data_size, data_attr)

    memory_logger.info(f"Completed memory mapping process for {current_state.state_name}")

    return all_pages



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

