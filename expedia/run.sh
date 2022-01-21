
# range=(0 1 2 3 4 5 6)
# year=(2021 2021 2021 2021 2022 2022 2022)
# month=(9 10 11 12 1 2 3)
# days=(30 31 30 31 31 28 31)

range=(0 1 2 3 4 5 6)
year=(2021 2022)
month=(9 3)
day=(1 31)

cities=(PVG DTW SEA SFO DFW)





# for flyfrom in ${cities[@]};do
#     for flyto in ${cities[@]};do
# 	if [[ $flyto == $flyfrom ]];then
# 	    continue
# 	fi
# 	for i in ${range[@]};do
# 	    echo "echo" python3 l3.py ${year[$i]} ${month[$i]} 1 ${days[$i]} ${flyfrom} ${flyto}
# 	    echo python3 l3.py ${year[$i]} ${month[$i]} 1 ${days[$i]} ${flyfrom} ${flyto}
# 	    echo sleep 2
# 	done
#     done
# done

for flyfrom in ${cities[@]};do
    for flyto in ${cities[@]};do
	if [[ $flyto == $flyfrom ]];then
	    continue
	fi
	echo python3 webCrawl_expedia.py ${flyfrom} ${flyto} ${year[0]} ${month[0]} ${day[0]} ${year[1]} ${month[1]} ${day[1]} 
	echo sleep 2
	
    done
done





exit


