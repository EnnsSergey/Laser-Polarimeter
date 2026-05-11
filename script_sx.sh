sy=50
d=12
for (( i = 1; i <= 100; i++ ))
do
	sx=$(( 10*$i ))
	for (( k = 0; k <= 10; k++ ))
	do
		qsub main.sh $k $sx $sy $d
	done
done

