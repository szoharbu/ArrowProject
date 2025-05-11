import os
import sys
from Utils.configuration_management import get_config_manager

def run_PGT_prototype():
    """
    Imports necessary modules from the PGT environment and calls the setProfile function.
    """
    os.environ["PGT_HOME"] = "/some_path/"
 
    pgt_home = os.environ.get("PGT_HOME")
    bin_path = os.path.join(pgt_home, "bin", "PGT_UCS4")
    src_path = os.path.join(pgt_home, "src")

# ... your run_set_profile function call ...

    if bin_path not in sys.path:
        sys.path.append(bin_path)
    if src_path not in sys.path:
        sys.path.append(src_path)

    try:
        from _pgt import setProfile, createPlatformMemoryManager, UNTAGGED, addMemory, pgtSetTargetInfo, IS_RME_IMPLEMENTED
        from _pgt import createGranuleProtectionTable, createGptAttributes, createMemoryManager, mapGpt
        from _pgt import createAddress, ROOT_PAS, SIZE_512MB, setGptTableMemoryManager, createStg1TS, VMSAv8_64, PL3R
        from _pgt import createMmuAttributes, getOutputAddr, generateOutputs

        from helperFunctions import V9A, setGptProperties, OUT_SH, CACHE_NON, CACHE_NON # *
        from helperFunctions import setTranslationSystemProp, FillStage1BlockAttributes, ROOT
        from helperFunctions import SIZE_4KB, SIZE_2MB, SIZE_1GB, TG_4KB, PGS_4KB, PA_48_BITS
        from helperFunctions import map as pgt_map

        #from customer_mem_map import pgtInitPlatformMemoryMap # *

        setProfile(V9A)
        
        PMM = createPlatformMemoryManager("pmm", UNTAGGED)
        addMemory(PMM, 0x000000000000 , 0x80000000000 )
        #PMM = pgtInitPlatformMemoryMap();
        if(PMM < 0) :
                print ("PGT ERROR : initTarget failed")
                sys.exit(0)
        # PMM = Memory Manager ID predefined to be used for accessing Platform Memory Map
        PMM = 0

        pgtSetTargetInfo(IS_RME_IMPLEMENTED, True)

        #Create & configure GPT
        GPT = createGranuleProtectionTable("GPT");
        setGptProperties(GPT, PGS=PGS_4KB, PPS=PA_48_BITS, SH=OUT_SH, IRGN=CACHE_NON, ORGN=CACHE_NON)

        #Create & configure GPT Attributes
        gptAttrID = createGptAttributes()

        #Create table MM for GPT
        GMM = createMemoryManager("GMM", UNTAGGED)
        addMemory(GMM, 0x40000000, 0x60000000)
        mapGpt(GPT, createAddress(0x40000000), ROOT_PAS, SIZE_512MB, gptAttrID, 1)
        setGptTableMemoryManager(GPT, GMM)

        # Create, Config, map STAGE1+STAGE2 TS

        S1TS=createStg1TS("S1TS", VMSAv8_64, PL3R)
        setTranslationSystemProp(S1TS, TG0=TG_4KB)
        stage1_attr=createMmuAttributes()
        FillStage1BlockAttributes(stage1_attr, NS=ROOT)

        pgt_map(S1TS, createAddress(0x3000000), SIZE_2MB, stage1_attr)
        paID = getOutputAddr(S1TS, createAddress(0x3000000))

        #Gpt mappings for S1TS PA
        mapGpt(GPT, paID, ROOT_PAS, SIZE_1GB, gptAttrID, 1)

        generateOutputs()

        # config_manager = get_config_manager()
        # output_dir = config_manager.get_value('output_dir_path')
        # original_output_dir = os.environ.get("OUTPUT_DIR")
        # os.environ["OUTPUT_DIR"] = output_dir

        # generateOutputs()

        # os.environ.pop("OUTPUT_DIR")
        # if original_output_dir is not None:
        #     os.environ["OUTPUT_DIR"] = original_output_dir


    except ImportError as e:
        print(f"Error importing PGT modules: {e}")
        print(f"Make sure PGT_HOME is correctly set to: {pgt_home}")
        raise RuntimeError(f"Error importing PGT modules: {e}")
    except AttributeError:
        print("Error: setProfile function not found in _pgt module.")

    return 

