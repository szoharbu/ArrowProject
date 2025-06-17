#!/bin/csh -f
source ~/.cshrc_custom
source .venv/bin/activate.csh
setenv PYTHONPATH $PWD
echo run_arrow.py templates/testing_template.py --create_binary True --upload_statistics False --identifier zohar_work_pc --instruction_debug_prints False --memory_debug_prints memory_log --seed 1234


#
# setenv CC /home/utils/gcc-13.3.0-ld/bin/gcc
# setenv CXX /home/utils/gcc-13.3.0-ld/bin/g++