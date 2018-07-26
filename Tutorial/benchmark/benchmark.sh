#!/bin/bash



t=`date "+%Y-%m-%d"`


##GPU Scenarios
for gpu_type in k80 p100; do
	if [ $gpu_type == "k80" ]; then
		for num_gpu in 1 2 3 4; do
			echo "     GPU Job"
			echo "     NUM_GPU = $num_gpu"
			echo "     GPU_TYPE = $gpu_type"
			echo "     Date = $t" 
			ofile="$t-GPU-$gpu_type:$num_gpu";sbatch -p GPU-shared --gres=gpu:$gpu_type:$num_gpu -o ./results/$ofile gpuJob.sh

	    done
	else [ $gpu_type == "p100" ]
		for num_gpu in 1 2; do
			echo "     GPU Job"
			echo "     NUM_GPU = $num_gpu"
			echo "     GPU_TYPE = $gpu_type"
			echo "     Date = $t" 
			ofile="$t-GPU-$gpu_type:$num_gpu";sbatch -p GPU-shared --gres=gpu:$gpu_type:$num_gpu -o ./results/$ofile gpuJob.sh
        done
    fi
done

##CPU Only Scenarios
for partition in RM;do
	for num_cores in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28; do

		echo "     CPU Only Job"
		echo "     NUM_CORES = $num_cores"
		echo "     PARTITION = $partition"
		echo "     Date = $t"
		ofile="$t-CPU-$partition:$num_cores";sbatch -p $partition -N 1 --ntasks-per-node=$num_cores -o ./results/$ofile gpuJob.sh

	done
done



