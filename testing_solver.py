import itertools
from subprocess import call
import time
import csv

'''
observation
    1) block size matters. If block_size >= 15 or so, the solver will run a lot of time.
    2) graph size can vary for a large ranges
'''


def run_all_configurations():
	# set names, running time, etc..
	cluster_env = 'geolib'

	#size_list = range(5, 500, 50)
	blocks = [5, 10, 15, 20]
	counts = 6

	# try different blocks given different map size
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

	# try different map size given different blocks
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

if __name__ == '__main__':
	run_all_configurations()
