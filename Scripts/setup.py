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


def set_pythonpath(project_dir):
    """
    Provide instructions for non-PyCharm users to set up PYTHONPATH and run the tool.
    """
    pythonpath_command = f"export PYTHONPATH={project_dir}" if os.name != "nt" else f"set PYTHONPATH={project_dir}"

    print("\nSetup complete! To run the tool:")
    print("1. Activate the virtual environment:")
    if os.name == "nt":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print(f"2. Set the PYTHONPATH environment variable:\n   {pythonpath_command}")
    print("3. Run the tool:\n   python Arrow/main.py templates/direct_template.py")


def main():
    """
    Main entry point for the setup script.
    """
    print("Starting setup...")
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Reset old settings
    reset_old_settings(project_dir)

    # Create virtual environment
    venv_path = create_virtual_environment(project_dir)

    # Install dependencies
    install_dependencies(venv_path)

    # Provide instructions for non-PyCharm users
    set_pythonpath(project_dir)


if __name__ == "__main__":
    main()
