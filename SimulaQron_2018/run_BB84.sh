#!/usr/bin/env sh
TEST_PIDS=$(ps aux | grep python | grep -E "Test" | awk {'print $2'})
if [ "$TEST_PIDS" != "" ]
then
        kill -9 $TEST_PIDS
fi

echo ____Enter number of qubits:
read n_qubits

python Alice_BB84.py --n $n_qubits &
python Bob_BB84.py --n $n_qubits &
python Eve_BB84.py --n $n_qubits &
