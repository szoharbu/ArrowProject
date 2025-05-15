
import os
from Arrow.Externals import run_tool

def main():
    """
    Main script to run your tool 10 times and save the results.
    """
    output_dir = "mini_regression"  # Main output directory
    summary = []  # To store the results of each run

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

    print(f"=== Starting mini regression runs")
    for i in range(5):
        for arch in ['x86','riscv', 'arm']:
            for template in ['random_template.py', 'direct_template.py']:
                template_path = f"templates/{template}"  # Path to your template

                run_str = f"{arch}_{template}_run_{i + 1}"
                subdir = os.path.join(output_dir, run_str )

                # Ensure the subdirectory exists
                os.makedirs(subdir, exist_ok=True)  # Create the directory if it doesn't exist

                # Command to run your tool with the template and output directory
                command = ["python", "Arrow/main.py", template_path, "--output", subdir, "--arch", arch, "--cloud_mode", "True"]

               # Run the tool and collect the success/failure result
                success = run_tool.run_tool(template_path, subdir, command_line=command, run_str=run_str)

                # Add the result to the summary list
                summary.append({
                    "run": run_str,
                    "success": success
                })
    print(f"=== Finished mini regression")

    # Write a summary file to indicate if any test failed
    summary_file = os.path.join(output_dir, "summary.txt")
    with open(summary_file, "w") as f:
        all_success = all(entry["success"] for entry in summary)
        f.write("Summary of mini regression tests:\n")
        for entry in summary:
            status = "PASSED" if entry["success"] else "FAILED"
            f.write(f"{entry['run']}: {status}\n")

        # Add a final line indicating overall result
        if all_success:
            f.write("\nAll tests PASSED\n")
        else:
            f.write("\nSome tests FAILED\n")

if __name__ == "__main__":
    main()
