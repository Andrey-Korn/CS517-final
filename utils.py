import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import networkx as nx
import csv

# 16 colors
colors = ['r', 'g', 'b', 'k', '#a6cee3','#ffff99','#b2df8a','#33a02c','#fb9a99','#e31a1c','#ff7f00','#1f78b4','#fdbf6f','#cab2d6','#6a3d9a','#b15928']


def data_generation(N, num_block, plotting=False):
    file_name = f'./dataset/{N}x{N}_{num_block}blocks.csv'
    result = []

    # random block for start point s
    [s_x2, s_y2] = np.random.randint(N, size=2)
    result.append([0, s_x2, 0, s_y2])

    # random block for internal blocks
    for i in range(num_block-1):
        [x1, x2] = sorted(np.random.randint(N, size=2))
        [y1, y2] = sorted(np.random.randint(N, size=2))
        result.append([x1, x2, y1, y2])

    with open(file_name, mode='w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow([N])
        writer.writerow([num_block])

        writer.writerows(result)


    if plotting:
        G = nx.grid_2d_graph(N, N)

        f,ax = plt.subplots(1,1, figsize=(N, N))
        pos = {(x, y): (x, y) for x, y in G.nodes()}
        nx.draw(G, pos=pos,
                with_labels=False,
                node_size=10,
                ax=ax)
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

        # add color blocks
        cmap = plt.get_cmap('jet', 20)
        cmap.set_under('gray')
        for i, boundary in enumerate(result):
            x0, x1, y0, y1 = boundary
            ax.add_patch(Rectangle((x0-0.3, y0-0.3), x1-x0+0.6, y1-y0+0.6, linewidth=1, facecolor=colors[i], alpha=0.5))

        limits = plt.axis('on')
        f.savefig(f'./dataset/{N}x{N}_{num_block}blocks.png')


    return file_name




def main():
    data_generation(20, 10, plotting=True)


if __name__ == '__main__':
    main()
