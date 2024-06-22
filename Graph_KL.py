from edf_trans_to_graph import add_to_graph  # 导入将EDF文件转化为图的函数
import spydrnet as sdn
import networkx as nx
import matplotlib.pyplot as plt
import random

def calculate_gain(G, node, A, B):
    # 计算将节点移动到另一个社区时的增益
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
                    #计算两点若进行交换的增益
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

# 加载EDF文件
edf_file_path = 'block_2_mao.edf'  # 放入EDF文件的路径
netlist = sdn.parse(edf_file_path)

# 创建有向图
G = nx.DiGraph()
# 调用函数，得到对应的处理后的图
add_to_graph(G, netlist)  

G_undirected = G.to_undirected()  # 将其转换为无向图

communities = list(KL(G_undirected))

# 找出社区间的边
edges_to_remove = []
for edge in G_undirected.edges():
    if (edge[0] in communities[0] and edge[1] in communities[1]) or (edge[0] in communities[1] and edge[1] in communities[0]):
        edges_to_remove.append(edge)

# 绘制图并根据社区划分着色
pos = nx.spring_layout(G_undirected)  # 使用Spring布局
labels = nx.get_node_attributes(G, 'label')  # 获取所有节点的label属性
nx.draw(G_undirected, pos, labels=labels, with_labels=True, node_color='lightblue', font_weight='bold', node_size=500, font_size=8)

# 根据社区划分着色节点
color_map = ['red', 'green']
for i, community in enumerate(communities):
    nx.draw_networkx_nodes(G_undirected, pos, nodelist=community, node_color=color_map[i % len(color_map)])

# 着色被减少的连接
nx.draw_networkx_edges(G_undirected, pos, edgelist=edges_to_remove, edge_color='red', style='dashed')

# 显示图
plt.show()
