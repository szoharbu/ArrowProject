import os
import subprocess
import sys
import shutil

def reset_old_settings(project_dir):
    """Reset old PyCharm settings to ensure a clean slate."""
    idea_path = os.path.join(project_dir, ".idea")
    venv_path = os.path.join(project_dir, "venv")

    # Remove .idea folder
    if os.path.exists(idea_path):
        shutil.rmtree(idea_path)
        print(f"Removed old PyCharm settings: {idea_path}")

    # Remove old virtual environment
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
        print(f"Removed old virtual environment: {venv_path}")

def create_virtual_environment(project_dir):
    """Create a virtual environment if it doesn't already exist."""
    venv_path = os.path.join(project_dir, "venv")

    if not os.path.exists(venv_path):
        print("Creating a virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"Virtual environment created at: {venv_path}")
    else:
        print("Virtual environment already exists. Skipping creation.")

    return venv_path

def install_dependencies(venv_path):
    """Install required Python dependencies inside the virtual environment."""
    pip_executable = os.path.join(venv_path, "bin", "pip") if os.name != "nt" else os.path.join(venv_path, "Scripts", "pip.exe")

    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'requirements.txt')

    if not os.path.exists(requirements_path):
        print(f"ERROR: Could not find requirements file at {requirements_path}")
        return

    print("Installing Python dependencies...")
    subprocess.check_call([pip_executable, "install", "-r", requirements_path])

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
    </component>
    """

    config_path = os.path.join(run_config_dir, "Run_Tool.xml")
    with open(config_path, "w") as f:
        f.write(run_config)

    print(f"PyCharm run configurations created at: {config_path}")

def main():
    print("Starting setup...")

    # Locate the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))

    # 0. Reset old settings
    reset_old_settings(project_dir)

    # 1. Create a virtual environment
    venv_path = create_virtual_environment(project_dir)

    # 2. Install dependencies
    install_dependencies(venv_path)

    # # 3. Create PyCharm run configurations
    # create_pycharm_run_configurations(project_dir)

    # # 4. Print final instructions
    # activation_command = "source venv/bin/activate" if os.name != "nt" else "venv\\Scripts\\activate"
    # print(f"Setup complete. To activate the virtual environment, run:\n\n{activation_command}\n")

if __name__ == "__main__":
    main()
