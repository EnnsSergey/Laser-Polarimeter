dir="/home/enns/LaserPolarimeter"
for (( i =0 ; i < 100;  i++ ))
do
	qsub main.sh $i
done
