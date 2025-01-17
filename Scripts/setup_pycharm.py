import os
import subprocess
import sys
import shutil

def reset_old_settings(project_dir):
    """Reset old PyCharm settings to ensure a clean slate."""
    idea_path = os.path.join(project_dir, ".idea")
    scripts_dir = os.path.join(project_dir, "scripts")

    # Remove .idea folder
    if os.path.exists(idea_path):
        shutil.rmtree(idea_path)
        print(f"Removed old PyCharm settings: {idea_path}")

    # Remove old scripts
    if os.path.exists(scripts_dir):
        shutil.rmtree(scripts_dir)
        print(f"Removed old scripts: {scripts_dir}")

def install_dependencies():
    """Install required Python dependencies."""
    # Locate the requirements.txt file relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_dir, '..', 'requirements.txt')

    if not os.path.exists(requirements_path):
        print(f"ERROR: Could not find requirements file at {requirements_path}")
        return

    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])

def setup_interpreter(project_dir):
    """Configure the Python interpreter in PyCharm."""
    misc_path = os.path.join(project_dir, ".idea", "misc.xml")

    # Example interpreter path: Adjust this to match your virtual environment or system Python
    interpreter_path = os.path.join(project_dir, "venv", "bin", "python") if os.name != "nt" else os.path.join(project_dir, "venv", "Scripts", "python.exe")

    # Create .idea/misc.xml if it doesn't exist
    os.makedirs(os.path.dirname(misc_path), exist_ok=True)

    # Update or create the interpreter settings
    misc_content = f"""
    <project version="4">
      <component name="ProjectRootManager" version="2" languageLevel="PYTHON38">
        <output url="file://$PROJECT_DIR$/out" />
        <python>
          <option name="sdkHome" value="{interpreter_path}" />
        </python>
      </component>
    </project>
    """

    with open(misc_path, "w") as f:
        f.write(misc_content)

    print(f"Python interpreter configured at: {interpreter_path}")

def create_pycharm_run_configurations(project_dir):
    """Generate PyCharm run configurations."""
    run_config_dir = os.path.join(project_dir, ".idea", "runConfigurations")
    os.makedirs(run_config_dir, exist_ok=True)

    # Example configuration for running main.py with default parameters
    run_config = """
    <component name="ProjectRunConfigurationManager">
      <configuration default="false" name="Direct Run" type="PythonConfigurationType" factoryName="Python">
        <module name="project" />
        <option name="SCRIPT_NAME" value="$PROJECT_DIR$/Arrow/main.py" />
        <option name="PARAMETERS" value="templates/direct_template.py" />
        <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
      </configuration>
      <configuration default="false" name="Random Run" type="PythonConfigurationType" factoryName="Python">
        <module name="project" />
        <option name="SCRIPT_NAME" value="$PROJECT_DIR$/Arrow/main.py" />
        <option name="PARAMETERS" value="templates/random_template.py" />
        <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
      </configuration>
    </component>
    """

    config_path = os.path.join(run_config_dir, "Run_Tool.xml")
    with open(config_path, "w") as f:
        f.write(run_config)

    print(f"PyCharm run configurations created at: {config_path}")

def create_wrapper_scripts(project_dir):
    """Create wrapper scripts for command-line usage."""
    scripts_dir = os.path.join(project_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    # Create a shell script for Linux/Mac
    shell_script = f"""#!/bin/bash
    python {os.path.join(project_dir, 'main.py')} --param1 default_value --param2 42
    """
    with open(os.path.join(scripts_dir, "run_tool.sh"), "w") as f:
        f.write(shell_script)
    os.chmod(os.path.join(scripts_dir, "run_tool.sh"), 0o755)

    # Create a batch script for Windows
    batch_script = f"""@echo off
    python {os.path.join(project_dir, 'main.py')} --param1 default_value --param2 42
    """
    with open(os.path.join(scripts_dir, "run_tool.bat"), "w") as f:
        f.write(batch_script)

    print(f"Wrapper scripts created in {scripts_dir}.")

def main():
    print("Starting setup...")

    # Locate the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))

    # 0. Reset old settings
    reset_old_settings(project_dir)

    # 1. Install Python dependencies
    install_dependencies()

    # 2. Set up Python interpreter
    setup_interpreter(project_dir)

    # 3. Create PyCharm run configurations
    create_pycharm_run_configurations(project_dir)

    # 4. Create wrapper scripts for command-line usage
    create_wrapper_scripts(project_dir)

    print("Setup complete. You're ready to go!")

if __name__ == "__main__":
    main()
