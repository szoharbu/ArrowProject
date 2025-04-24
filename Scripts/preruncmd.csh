#!/bin/csh -f
source ~/.cshrc_custom
source .venv/bin/activate.csh
setenv PYTHONPATH $PWD
echo python Arrow\main.py templates/direct_template.py --arch arm --create_binary True --identifier zohar_work_pc --upload_statistics True --seed 1234
