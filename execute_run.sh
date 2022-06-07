#!/bin/bash

python prepare_dataset.py -f myconfig.yml
python analysis_one_run.py -f myconfig.yml
python collect_bins_results.py -f myconfig.yml
python plot_run_lightcurves.py -f myconfig.yml -cp false