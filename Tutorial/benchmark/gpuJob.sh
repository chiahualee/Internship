#!/bin/bash
#SBATCH --job-name=benchmark
##SBATCH --partition=GPU-shared
##SBATCH --nodes=1
##SBATCH --gres=gpu:p100:1
#SBATCH --time=00:40:00
module load AI/anaconda3-5.1.0_gpu
source activate $AI_ENV
time python nbTutorial.py