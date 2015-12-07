#!/bin/bash 

# Check for arguments
if [ $# -lt 2 ]
  then
    echo "Usage: run_all.sh <Threads> <Runs>"
    exit 1
fi

# Touch the 'timer.flag' file to enable deep timers
touch ./timer.flag

# Create the './outputs' directory if it doesn't exist
mkdir -p ./outputs

# Start timer to keep track of time taken
start_all=`date +%s`

# Let's run all scripts...
echo "Running benchmark for $1 Threads and $2 Runs."
for ((a = 1; a <= $1; a++)); do
  export OMP_NUM_THREADS=$a
  for i in $(ls ./bin); do
    for ((j = 1; j <= $2; j++)); do
      start=`date +%s`
      ./bin/$i > ./outputs/$i.T$a.run$j.out;
      end=`date +%s`
      echo "Finished $i -- Thread $a -- Run $j -- Took $((end-start)) seconds"
    done
  done
done

# Done, let's print total time taken...
end_all=`date +%s`
echo "Done with all. Took $((end_all-start_all)) seconds"