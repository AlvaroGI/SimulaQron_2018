#!/usr/bin/env sh
TEST_PIDS=$(ps aux | grep python | grep -E "Test" | awk {'print $2'})
if [ "$TEST_PIDS" != "" ]
then
        kill -9 $TEST_PIDS
fi

# Default values
n_key=3
attack=0
n_qubits=10
n_test=5
error_threshold=0.2

while getopts n:a:q:t:e: option
do
case "${option}"
in
n) n_key=${OPTARG};;
a) attack=${OPTARG};;
q) n_qubits=${OPTARG};;
t) n_test=${OPTARG};;
e) error_threshold=${OPTARG};;
esac
done

python aliceTest.py --q $n_qubits --e $error_threshold &
python bobTest.py --t $n_test &
python eveTest.py --a $attack &
