
### Setup Instructions

1. **Clone the Repository** (as previously described)

   ```bash
   git clone https://github.com/szoharbu/ArrowProject.git
   cd project
   ```

2. **Run the Setup Script**

   The setup script will:
   - Remove old settings (if any)
   - Create a virtual environment
   - Install project dependencies

   Run the following command:
    ```bash
   python Scripts/setup.py
   ```


3. **Activate the Virtual Environment**

   After the setup script completes, activate the virtual environment:

   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/macOS**:
     ```bash
     source venv/bin/activate
     ```

4. **set `PYTHONPATH`**

   Add the project root to the `PYTHONPATH` environment variable. This ensures Python can locate the project's modules:

- **Windows**:
  ```cmd
  set PYTHONPATH=%cd%
- **Linux/macOS**:
     ```bash
     export PYTHONPATH=$(pwd)
     ```
  

5. **Verify the Installation**
   
   Check that the dependencies are installed correctly:

   ```bash
   python -m pip list
   ```

   You should see a list of installed packages matching those in `requirements.txt`.

### Notes

- If you make changes to the project structure or dependencies, re-run the setup script to ensure consistency.
