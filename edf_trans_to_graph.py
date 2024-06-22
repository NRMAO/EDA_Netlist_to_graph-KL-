import spydrnet as sdn
import networkx as nx
import matplotlib.pyplot as plt

# 加载EDF文件
edf_file_path = 'block_2_mao.edf'
netlist = sdn.parse(edf_file_path)

# 创建有向图
G = nx.DiGraph()



# 将实例添加到图中的函数
def add_to_graph(graph, netlist):
    definition = netlist.libraries[0].definitions[-1]  # 得到需要的硬件

    for instance in definition.children:
        instance_name = instance.name  # 得到每个实例化器件的名字
        cell_name = instance.reference.name  # 得到实例化器件的种类，例如AND等
        graph.add_node(instance_name, label=cell_name)  # 添加节点到图中

        input_ports = [port.name for port in instance.reference.ports if port.direction == sdn.IN]  # 得到所有器件的输入口
        output_ports = [port.name for port in instance.reference.ports if port.direction == sdn.OUT]  # 得到所有器件的输出口

        for pin in instance.pins:  #得到该器件上的所有外界引脚(OuterPins)
            for wire_pin in pin.wire.pins: #遍历所有内部引脚
                if hasattr(wire_pin, 'inner_pin') and pin is not wire_pin:  #得到被连接的器件的引脚
                    if wire_pin.inner_pin.port.direction == sdn.IN and pin.inner_pin.port.direction == sdn.IN:
                        continue  # 如果两个引脚都是输入，则不添加边
                    be_connected_instance_name = wire_pin.instance.name  # 找到被连接的器件
                    graph.add_edge(instance_name, be_connected_instance_name)  # 添加边到图中

                                            
                     
# 调用函数，将实例添加到图中
add_to_graph(G, netlist)

# 绘制图
pos = nx.spring_layout(G)  # 使用Spring布局
labels = nx.get_node_attributes(G, 'label')  # 获取所有节点的label属性
nx.draw(G, pos,  with_labels=True, node_color='lightblue', font_weight='bold', node_size=500, font_size=8)

# 显示图
plt.show()
