from edf_trans_to_graph import add_to_graph  # 导入将EDF文件转化为图的函数
import spydrnet as sdn
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

def calculate_gain(G, node, A, B):
    internal_edges = sum(1 for neighbor in G.neighbors(node) if neighbor in A)  # 计算该点在该区内的连接边数
    external_edges = sum(1 for neighbor in G.neighbors(node) if neighbor in B)  # 计算该点在与其他区的连接边数
    return external_edges - internal_edges  # 得到增益

def KL(G, max_iter=10):
    nodes = list(G.nodes())
    random.shuffle(nodes)  # 随机打乱节点顺序
    # 将图随机分为两个部分
    A = set(nodes[:len(nodes) // 2])
    B = set(nodes[len(nodes) // 2:])
    
    def swap_nodes(A, B):
        gains = []
        while True:
            max_gain = float('-inf')
            best_pair = None
            # 计算所有可能的交换对及其增益
            for a in A:
                for b in B:
                    gain = calculate_gain(G, a, A, B) + calculate_gain(G, b, B, A) - 2 * (G.has_edge(a, b) or G.has_edge(b, a))
                    if gain > max_gain:
                        max_gain = gain
                        best_pair = (a, b)
            if max_gain <= 0:
                break
            gains.append((max_gain, best_pair))
            # 执行最佳交换
            A.remove(best_pair[0])
            B.remove(best_pair[1])
            A.add(best_pair[1])
            B.add(best_pair[0])
        return gains
    
    for _ in range(max_iter):
        gains = swap_nodes(A, B)
        if not gains or gains[-1][0] <= 0:
            break
    return A, B

def coarsen_graph(G):
    matching = nx.max_weight_matching(G, maxcardinality=True)
    coarse_G = nx.Graph()
    
    pos = nx.spring_layout(G)  # 获取当前图的布局
    for u, v in matching:
        new_node = (u, v)
        coarse_G.add_node(new_node)
        coarse_G.nodes[new_node]['pos'] = (np.array(pos[u]) + np.array(pos[v])) / 2  # 合并节点的位置为其组成节点的位置的平均值
        for neighbor in G.neighbors(u):
            if neighbor not in (u, v):
                coarse_G.add_edge(new_node, neighbor)
        for neighbor in G.neighbors(v):
            if neighbor not in (u, v):
                coarse_G.add_edge(new_node, neighbor)
    
    single_nodes = set(G.nodes()) - set(u for u, v in matching) - set(v for u, v in matching)
    for node in single_nodes:
        coarse_G.add_node(node)
        coarse_G.nodes[node]['pos'] = pos[node]  # 保留单个节点的位置
    
    return coarse_G

# 对图进行粗粒度的划分
def coarsening(G, min_size=10):
    coarsened_graphs = [G]
    while G.number_of_nodes() > min_size:
        G = coarsen_graph(G)
        coarsened_graphs.append(G)
    return coarsened_graphs

#对图进行细一步的向内的划分
def refinement(G, coarsened_graphs, partitions):
    for i in range(len(coarsened_graphs) - 1, 0, -1):
        G = coarsened_graphs[i - 1]
        coarse_G = coarsened_graphs[i]
        partition = partitions[i]

        refined_partition = [set(), set()]
        for supernode in coarse_G.nodes():
            if isinstance(supernode, tuple):
                u, v = supernode
                if u in partition[0] or v in partition[0]:
                    refined_partition[0].update([u, v])
                else:
                    refined_partition[1].update([u, v])
            else:
                if supernode in partition[0]:
                    refined_partition[0].add(supernode)
                else:
                    refined_partition[1].add(supernode)

        partitions[i - 1] = refined_partition
        partitions[i - 1] = KL(G)
    
    return partitions[0]

#将图展示的步骤进行打包成函数
def plot_communities(G, communities):
    pos = nx.spring_layout(G)  # 使用Spring布局
    labels = nx.get_node_attributes(G, 'label')  # 获取所有节点的label属性
    nx.draw(G, pos, labels=labels, with_labels=True, node_color='lightblue', font_weight='bold', node_size=500, font_size=8)

    # 根据社区划分着色节点
    color_map = ['red', 'green']
    for i, community in enumerate(communities):
        nx.draw_networkx_nodes(G, pos, nodelist=community, node_color=color_map[i % len(color_map)])
    
    # 找出社区间的边
    edges_to_remove = []
    for edge in G.edges():
        if (edge[0] in communities[0] and edge[1] in communities[1]) or (edge[0] in communities[1] and edge[1] in communities[0]):
            edges_to_remove.append(edge)
    
    # 着色被减少的连接
    nx.draw_networkx_edges(G, pos, edgelist=edges_to_remove, edge_color='red', style='dashed')

    # 显示图
    plt.show()

# 加载EDF文件
edf_file_path = 'block_2_mao.edf'  # 放入EDF文件的路径
netlist = sdn.parse(edf_file_path)

# 创建有向图
G = nx.DiGraph()
# 调用函数，得到对应的处理后的图
add_to_graph(G, netlist)  

G_undirected = G.to_undirected()  # 将其转换为无向图

# 进行图的粗化
coarsened_graphs = coarsening(G_undirected)

# 在最粗的图上进行划分
partitions = []
for graph in coarsened_graphs:
    partitions.append(KL(graph))

# 细化划分结果
final_partition = refinement(G_undirected, coarsened_graphs, partitions)

# 绘制最终的社区划分结果
plot_communities(G_undirected, final_partition)
