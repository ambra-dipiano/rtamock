# Prepare dataset

```bash
python prepare_dataset.py -f <myconfig.yml>
```

# Execute analysis single run

```bash
python analysis_one_run.py -f <myconfig.yml>
```

# Collect run results from single bins

```bash
python collect_bins_results.py -d $DATA/<ARCHIVE_FOLDER>/<RUNID>/<BINS_PARENT_FOLDER> -r <RUNID>
```

# Plot lightcurves of list of runs

```bash
python plot_lightcurves.py -f <myconfig.yml> -cp <true|false>
```