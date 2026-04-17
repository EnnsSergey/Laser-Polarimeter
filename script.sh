dir="/home/enns/LaserPolarimeter"

#sx=50
sy=50
for (( i = 0; i <= 100; i++ ))
do
	sx=$((10*$i))
	for (( k = 0; k < 10; k++ ))
	do 
		qsub main.sh $k $sx $sy
	done

done
