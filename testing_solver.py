import itertools
from subprocess import call
import time
import csv


def run_all_configurations():
	# set names, running time, etc..
	cluster_env = 'geolib'

	#size_list = range(5, 500, 50)
	blocks = [1, 2, 3,4,5,6,7,8,9,10,11,12,13,14]
	counts = 6



	for block in [14, 20]:
		results = []
		for size in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
			temp_time = []
			time_average = 0.
			for _ in range(counts):
				begin_time = time.time()
				cmd = 'python ' + ' map_sat.py ' + ' --size ' + str(size) + ' --blocks ' + str(block)
				call(cmd, shell=True)

				end_time = time.time()

				temp_time.append(end_time - begin_time)
				time_average += (end_time - begin_time)

			results.append(temp_time)
			time_average = time_average / counts
			print(f'{block}-{size}-->time: {time_average}')

		with open(f'./testing/block-fixed-{block}x{block}.csv', mode='w') as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			writer.writerows(results)

	for size in [10, 50, 100]:
		results = []
		for j in blocks:
			temp_time = []
			time_average = 0.
			for _ in range(counts):
				begin_time = time.time()
				cmd = 'python ' + ' map_sat.py ' + ' --size ' + str(size) + ' --blocks ' + str(j)
				call(cmd, shell=True)

				end_time = time.time()

				temp_time.append(end_time - begin_time)
				time_average += (end_time - begin_time)

			results.append(temp_time)
			time_average = time_average / counts
			print(f'{size}-{j}-->time: {time_average}')

		with open(f'./testing/size-fixed-{size}x{size}.csv', mode='w') as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			writer.writerows(results)


if __name__ == '__main__':
	run_all_configurations()
