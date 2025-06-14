#!/bin/csh -f
source ~/.cshrc_custom
source .venv/bin/activate.csh
setenv PYTHONPATH $PWD
echo python Arrow/main.py templates/testing_template.py --create_binary True --upload_statistics False --identifier zohar_work_pc --instruction_debug_prints False --memory_debug_prints memory_log --seed 1234
