import os
import subprocess

def run_tool(template_path, output_dir, command_line, run_str):
    """
    Run the tool with the given template and save output to the specified directory.
    """

    # Run the tool and capture output
    # Create local environment with Arrow tool paths
    env = os.environ.copy()
    if 'ARROW_TOOL_PATH' in os.environ:
        env['PATH'] = os.environ['ARROW_TOOL_PATH']
    
    result = subprocess.run(command_line, capture_output=True, text=True, env=env)

    # Save the result to the specified directory
    result_file = os.path.join(output_dir, "result.txt")
    with open(result_file, "w") as f:
        f.write(result.stdout)
        f.write(result.stderr)

    status = "PASSED" if result.returncode == 0 else "FAILED"
    print(f" TEST {run_str}: {status}")
    # Return the return code for success/failure tracking
    return result.returncode == 0  # True if success, False if failure
