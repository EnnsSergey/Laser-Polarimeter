sx=230
sy=70
#d=12
for (( i = 1; i <= 40; i++ ))
do
	d=$i
	for (( k = 0; k <= 10; k++ ))
	do
		qsub main.sh $k $sx $sy $d
	done
done
