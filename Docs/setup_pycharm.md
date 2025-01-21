
### Setup Instructions for PyCharm Users

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
   - Generate PyCharm-specific run configuration

   Run the following command:
    ```bash
   python Scripts/setup_pycharm.py
   ```


3. **Open the project in PyCharm**

   - *Open the project folder (ArrowProject) in PyCharm*:
   - *The virtual environment and run configurations will be automatically detected and ready to use.*:

### Notes

- If you make changes to the project structure or dependencies, re-run the setup script to ensure consistency.
- For advanced usage or development, consider setting up additional PyCharm run configurations (commented out in the setup script).
