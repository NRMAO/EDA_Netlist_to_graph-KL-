# EDA_Netlist_to_graph-KL-
这个项目包括Python代码将EDA输出的网表文件.edf 转化为图，并且利用KL算法，多级划分对该图进行处理
需要利用到spydrnet包、networkx包，matplotlib包。

需要准备好输入的电路网表文件.edf（注意在Vivado中不要进行综合！不要进行综合！不要进行综合！）

在Tcl Console终端输入指令<write_edif save_file_path/netlist_file_name.edf>

并且在代码对应处的输入改为自己的电路网表文件
（上传文件中的‘block.edf’仅作为参考文件）
