import os
import time
import click
import subprocess
from pathlib import Path
import ruamel.yaml as yaml
from ..colorml.utils import parse_config, get_timestamp_string

BASEFOLDER = "/scratch/kjablonk/colorml/colorml"
SUBMISSION = """
#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=10:00:0
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=gpu

slmodules -s x86_E5v2_Mellanox_GPU
module load gcc cuda cudnn mvapich2 openblas
source ~/anaconda3/bin/activate colorml
srun python -m colorml.run_training {}
"""

scalers = ["standard", "minmax"]
activations = ["relu", "selu"]
architectures = [
    ([64, 32, 16], [16, 8, 4, 3]),
    ([32, 16, 8], [8, 4, 3]),
    ([64, 8, 8], [8, 4, 3]),
    ([64, 16], [16, 8, 4, 3]),
    ([16, 8, 8], [8, 8, 3]),
]


@click.command("cli")
@click.option("--submit", is_flag=True)
def main(submit=False):
    for i, scaler in enumerate(scalers):
        for j, activation in enumerate(activations):
            for k, architecture in enumerate(architectures):
                basename = "_".join([get_timestamp_string(), i, j, k])
                configfile = write_config_file(
                    basename, scaler, activation, architecture
                )
                slurmfile = write_submission_script(configfile, basename)

                if submit:
                    subprocess.call(
                        "sbatch {}".format("{}.slurm".format(slurmfile)),
                        shell=True,
                        cwd=basename,
                    )
                    time.sleep(2)


def write_submission_script(configfile, basename):
    submission = SUBMISSION.format(configfile)
    slurmfile = os.path.join(BASEFOLDER, basename + ".slurm")
    with open(slurmfile, "w") as fh:
        fh.write(slurmfile)
    return slurmfile


def write_config_file(basename, scaler, activation, architecture):
    config = parse_config(
        "/scratch/kjablonk/colorml/colorml/models/models/test_config.yaml"
    )
    config["scaler"] = scaler
    config["model"]["activation_function"] = activation
    config["model"]["units"] = architecture[0]
    config["model"]["head_units"] = architecture[1]
    outname = os.path.join(BASEFOLDER, "models/models/", basename + ".yaml")
    with open(outname, "w",) as outfile:
        yaml.dump(config, outfile)

    return outfile


if __name__ == "__main__":
    main()