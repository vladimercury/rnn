i=0
while [[ $i -lt 10 ]]
do
echo "ITERATION $i"
/usr/bin/python3.6 /home/mercury/PycharmProjects/rnn/run-pc-net.py
let i=$i+1
done