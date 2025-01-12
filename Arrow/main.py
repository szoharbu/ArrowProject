import time

def main(args=None):
    start_time = time.time()

    print("==== Arrow main")

    try:
        #read_inputs()          # Read inputs, read template, read configuration, ARM/riscv, ...
        #evaluate_section() # review all configs and knobs, set them according to some logic and seal them ... register here also set the asm_logger
        #init_section()           # initialize the state, register, memory and other managers.
        #test_section()           # boot, body (foreach core, foreach scenario), test final

        mid_time = time.time()
        print(f"test generation end after {mid_time-start_time}")

        #final_section()         # post flows?


    except Exception as e:
        end_time = time.time()
        print(f"test failed after {end_time-start_time}")
    else:
        end_time = time.time()
        print(f"test total end after {end_time-start_time}")

    return True


if __name__ == "__main__":
    main()
