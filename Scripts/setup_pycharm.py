import os
import subprocess
import sys
import shutil


def reset_old_settings(project_dir):
    """
    Remove old PyCharm settings and virtual environment, if present.
    Ensures a clean slate before setup.
    """
    idea_path = os.path.join(project_dir, ".idea")
    venv_path = os.path.join(project_dir, ".venv")

    if os.path.exists(idea_path):
        shutil.rmtree(idea_path)
        print(f"Removed old PyCharm settings: {idea_path}")

    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
        print(f"Removed old virtual environment: {venv_path}")


def create_virtual_environment(project_dir):
    """
    Create a new virtual environment in the project directory.
    """
    venv_path = os.path.join(project_dir, ".venv")
    if not os.path.exists(venv_path):
        print("Creating a virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
        print(f"Virtual environment created at: {venv_path}")
    else:
        print("Virtual environment already exists. Skipping creation.")
    return venv_path


def install_dependencies(venv_path):
    """
    Install project dependencies from requirements.txt into the virtual environment.
    """
    pip_executable = os.path.join(venv_path, "Scripts", "pip.exe") if os.name == "nt" else os.path.join(venv_path, "bin", "pip")
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'requirements.txt')

    if os.path.exists(requirements_path):
        print("Installing dependencies...")
        subprocess.check_call([pip_executable, "install", "-r", requirements_path])
        print("Dependencies installed successfully.")
    else:
        print(f"ERROR: requirements.txt not found at {requirements_path}")
        sys.exit(1)


def create_pycharm_run_configurations(project_dir):
    """
    Generate PyCharm run configurations in the .idea folder.
    """
    run_config_dir = os.path.join(project_dir, ".idea", "runConfigurations")
    os.makedirs(run_config_dir, exist_ok=True)

    run_config = f"""
    <component name="ProjectRunConfigurationManager">
      <configuration default="false" name="direct_run" type="PythonConfigurationType" factoryName="Python">
        <module name="{os.path.basename(project_dir)}" />
        <option name="SCRIPT_NAME" value="$PROJECT_DIR$/Arrow/main.py" />
        <option name="PARAMETERS" value="templates/direct_template.py" />
        <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
      </configuration>
    </component>
    """

    config_path = os.path.join(run_config_dir, "Run_Main.xml")
    with open(config_path, "w") as f:
        f.write(run_config.strip())
    print(f"PyCharm run configurations created at: {config_path}")


def main():
    """
    Main entry point for the PyCharm-specific setup script.
    """
    print("Starting PyCharm setup...")
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Reset old settings
    reset_old_settings(project_dir)

    # Create virtual environment
    venv_path = create_virtual_environment(project_dir)

    # Install dependencies
    install_dependencies(venv_path)

    # Create PyCharm configurations
    create_pycharm_run_configurations(project_dir)

    print("\nPyCharm setup complete! Open the project in PyCharm to use the configured settings.")


if __name__ == "__main__":
    main()
