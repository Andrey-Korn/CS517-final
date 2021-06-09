
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import networkx as nx
import csv
import argparse

result_directory = 'resultData'
map_directory = 'mapData'

# 16 colors
colors = ['r', 'g', 'b', 'k', '#a6cee3','#ffff99','#b2df8a','#33a02c','#fb9a99','#e31a1c','#ff7f00','#1f78b4','#fdbf6f','#cab2d6','#6a3d9a','#b15928']


def data_generation(N, num_block):
    # create map directory
    if not os.path.exists(map_directory):
        os.makedirs(map_directory)

    file_name = f'./{map_directory}/{N}x{N}_{num_block}blocks.csv'
    result = []

    # random block for start point s
    [s_x2, s_y2] = np.random.randint(N, size=2)
    s_weight = int(np.random.randint(low=1, high=N, size=1))
    result.append([0, s_x2, 0, s_y2, s_weight])

    # random block for internal blocks
    for i in range(num_block-1):
        [x1, x2] = sorted(np.random.randint(N, size=2))
        [y1, y2] = sorted(np.random.randint(N, size=2))
        weight = int(np.random.randint(low=1, high=N, size=1))
        result.append([x1, x2, y1, y2, weight])

    with open(file_name, mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["map"])
        writer.writerow([N])
        writer.writerow([num_block])

        writer.writerows(result)

    return file_name
    
    
def map_plotting(filename):
    """
    :param filename: csv file directory
    :param draw_path: 'up': up->right; 'right'->'right->up'; 'diagonal'
    :return: None
    """

    path_type = None

    # parse map data
    N, num_obstacle = 0, 0
    result = []
    line_count = 0
    with open(filename) as file:
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            # first line in csv is map type
            if line_count == 0:
                path_type = row[0]
            # second line in csv is graph size
            elif line_count == 1:
                N = int(row[0])
            # third line in csv is # obstacles
            elif line_count == 2:
                num_obstacle = int(row[0])
            # add obstacles as a 5-tuple to a list:
            # (x1, x2, y1, y2 of the rectangle, weight)
            else:
                result.append(list(map(int, row)))

            line_count += 1
    assert len(result) == num_obstacle, 'check number of obstacles'

    # map plotting
    G = nx.grid_2d_graph(N, N)

    f,ax = plt.subplots(1,1, figsize=(N, N))
    pos = {(x, y): (x, y) for x, y in G.nodes()}
    nx.draw(G, pos=pos,
        with_labels=False,
        node_size=10,
        ax=ax)
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

    # add color blocks
    for i, boundary in enumerate(result):
        x0, x1, y0, y1, _ = boundary
        ax.add_patch(Rectangle((x0-0.3, y0-0.3), x1-x0+0.6, y1-y0+0.6, linewidth=1, facecolor=colors[i], alpha=0.5))

    # draw path
    width = 0.06
    head_width = 0.2
    head_length = 0.3
    if path_type == 'right':
        for i in range(1, N):
            ax.arrow(0, 0, i-0.25, 0, width = width, head_width=head_width, head_length=head_length, fc='k', ec='k')
            ax.arrow(N-1, 0, 0, i-0.25, width = width, head_width=head_width, head_length=head_length, fc='k', ec='k')
    elif path_type == 'up':
        for i in range(1, N):
            ax.arrow(0, 0, 0, i-0.25, width = width, head_width=head_width, head_length=head_length, fc='k', ec='k')
            ax.arrow(0, N-1, i-0.25, 0, width = width, head_width=head_width, head_length=head_length, fc='k', ec='k')
    elif path_type == 'diagonal':
        for i in range(1, N):
            ax.arrow(i-1, i-1, 0.75, 0, width = width, head_width=head_width, head_length=head_length, fc='k', ec='k')
            ax.arrow(i, i-1, 0, 0.75, width = width, head_width=head_width, head_length=head_length, fc='k', ec='k')
    else:
        pass
    limits = plt.axis('on')

    # save map plotting
    if path_type == 'map':
        f.savefig(f'./{map_directory}/{N}x{N}_{num_obstacle}blocks.png')
    else:
        original_obstacle_count = int(filename[filename.find("_")+1:filename.find("b")])
        f.savefig(f'./{result_directory}/{N}x{N}_{original_obstacle_count}blocks_{path_type}.png')


def main():
    parser = argparse.ArgumentParser(description='Data generation and graphing utility.')
    parser.add_argument("--graph", nargs=1, help='specify file_path of input or result data to graph')
    parser.add_argument("--generate", type=int, nargs=2, action='append', help='generate obstacle map of a certain size and obstacle number.')
    args = parser.parse_args()

    if(args.generate and args.graph):
        parser.error("Please only specify 1 argument type, either --graph or --generate")
        quit()

    if(args.generate):
        data_generation(args.generate[0][0], args.generate[0][1])

    elif(args.graph):
        map_plotting(args.graph[0])

    else:
        print("No flags specified")
        print("please run --help for usage")


if __name__ == '__main__':
    main()
