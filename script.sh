dir="/home/enns/LaserPolarimeter"

for (( i = 1; i <= 10; i++ ))
do
	for (( j = 1; j <= 10; j++ ))
	do
		sx=$((100*$i))
		sy=$((10*$j))
		for (( k = 0; k < 10;  k++ ))
		do
			qsub main.sh $k $sx $sy
		done
	done

done
