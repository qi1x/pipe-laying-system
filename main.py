import logging
import sys

import numpy as np  # 导入numpy库
from PyQt5.QtCore import Qt  # 从PyQt5库中导入Qt模块
from PyQt5.QtGui import QPixmap, QPen, QFont  # 从PyQt5库中导入QPixmap、QPen和QFont类
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QGraphicsView,  # 从PyQt5库中导入QApplication、QMainWindow、QGraphicsView等组件类
                             QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QPushButton, QWidget, QHBoxLayout,
                             QGraphicsLineItem, QGraphicsSimpleTextItem, QGraphicsEllipseItem)
from colorlog import ColoredFormatter

# 创建一个日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建一个处理控制台输出的处理程序
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# 创建一个处理保存到日志文件的处理程序
file_handler = logging.FileHandler('application.log')
file_handler.setLevel(logging.INFO)

# 定义带颜色的日志记录格式
color_formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(log_color)s%(levelname)s - %(log_color)s%(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'green',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_yellow',
    }
)
# 设置日志记录格式
console_handler.setFormatter(color_formatter)
file_handler.setFormatter(color_formatter)

# 将处理程序添加到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

coordinates = []  # 初始化坐标列表


class Canvas(QGraphicsView):  # 自定义Canvas类，继承自QGraphicsView类
    def __init__(self, parent=None):  # Canvas类的构造函数
        super().__init__(parent)  # 调用父类的构造函数
        self.setBaseSize(1000, 1000)  # 设置画布基本大小

        self.scene = QGraphicsScene(self)  # 创建一个QGraphicsScene对象
        pixmap = QPixmap("img/map.png")  # 从文件中创建一个QPixmap对象
        pixmap_item = QGraphicsPixmapItem(pixmap)  # 将QPixmap对象添加到场景中
        self.scene.addItem(pixmap_item)  # 将场景添加到视图中
        self.setScene(self.scene)  # 设置场景
        self.mousePressEvent = self.on_mouse_press_event  # 重写鼠标点击事件处理函数

    def on_mouse_press_event(self, event):  # 鼠标点击事件处理函数
        if event.button() == Qt.LeftButton:  # 如果是鼠标左键点击
            pos = self.mapToScene(event.pos())  # 获取点击位置的相对坐标
            self.scene.addEllipse(pos.x() - 2, pos.y() - 2, 4, 4, QPen(Qt.red), Qt.red)  # 在场景中添加一个红色椭圆
            coordinates.append((pos.x(), pos.y()))  # 将坐标添加到坐标列表中
            logger.info(f'已选坐标{coordinates}')  # 打印坐标列表
            logging.info(f"选择的点: x={pos.x()}, y={pos.y()}")


class MainWindow(QMainWindow):  # 自定义MainWindow类，继承自QMainWindow类
    def __init__(self):  # MainWindow类的构造函数
        super().__init__()  # 调用父类的构造函数

        self.canvas = Canvas()  # 创建Canvas对象
        layout = QVBoxLayout()  # 创建垂直布局管理器
        layout.addWidget(self.canvas)  # 将Canvas组件添加到布局中

        central_widget = QWidget()  # 创建QWidget对象
        central_widget.setLayout(layout)  # 设置布局
        self.setCentralWidget(central_widget)  # 设置中心窗口

        bottom_navigation = QWidget()  # 创建底部导航栏
        bottom_navigation_layout = QHBoxLayout()  # 创建水平布局管理器

        zoom_in_button = QPushButton('放大', self)  # 创建“放大”按钮
        zoom_out_button = QPushButton('缩小', self)  # 创建“缩小”按钮
        kruskal_button = QPushButton('使用Kruskal算法计算', self)  # 创建“使用Kruskal算法计算”按钮
        bottom_navigation_layout.addWidget(zoom_in_button)  # 将“放大”按钮添加到底部导航栏布局中
        bottom_navigation_layout.addWidget(zoom_out_button)  # 将“缩小”按钮添加到底部导航栏布局中
        bottom_navigation_layout.addWidget(kruskal_button)  # 将“使用Kruskal算法计算”按钮添加到底部导航栏布局中
        clear_tree_button = QPushButton('清除生成树', self)
        clear_points_button = QPushButton('清除所有选择的点', self)
        bottom_navigation_layout.addWidget(clear_tree_button)
        bottom_navigation_layout.addWidget(clear_points_button)

        clear_tree_button.clicked.connect(self.clear_tree)
        clear_points_button.clicked.connect(self.clear_points)
        self.last_log_time = None  # 跟踪最后一次记录日志的时间

        zoom_in_button.clicked.connect(self.zoom_in)  # 绑定“放大”按钮的点击事件
        zoom_out_button.clicked.connect(self.zoom_out)  # 绑定“缩小”按钮的点击事件
        kruskal_button.clicked.connect(
            lambda: self.calculate_minimum_spanning_tree('Kruskal'))  # 绑定“使用Kruskal算法计算”按钮的点击事件

        bottom_navigation.setLayout(bottom_navigation_layout)  # 设置底部导航栏布局
        bottom_navigation.setFixedHeight(40)  # 设置底部导航栏高度

        layout.addWidget(bottom_navigation)  # 将底部导航栏添加到布局中

    def clear_tree(self):
        if coordinates:
            items_to_remove = []
            for item in self.canvas.scene.items():
                if isinstance(item, QGraphicsLineItem) or isinstance(item, QGraphicsSimpleTextItem):
                    items_to_remove.append(item)

            for item in items_to_remove:
                self.canvas.scene.removeItem(item)
        logging.info("清除最小生成树.")

    def clear_points(self):
        self.clear_tree()
        global coordinates
        if coordinates:
            coordinates.clear()
            items_to_remove = []
            for item in self.canvas.scene.items():
                if isinstance(item, QGraphicsEllipseItem):
                    items_to_remove.append(item)

            for item in items_to_remove:
                self.canvas.scene.removeItem(item)
        logging.info("清除所有选择的点.")

    def zoom_in(self):  # 放大操作的槽函数
        self.canvas.scale(1.2, 1.2)  # 对画布进行放大

    def zoom_out(self):  # 缩小操作的槽函数
        self.canvas.scale(0.8, 0.8)  # 对画布进行缩小

    def calculate_minimum_spanning_tree(self, algorithm):
        global coordinates

        if algorithm == 'Kruskal':
            result = self.kruskal()
            logging.info("计算最小生成树结果:")
            for edge in result:
                logging.info(f"边: {edge}")
        else:
            raise

        for edge in result:
            node1 = edge[0]
            node2 = edge[1]
            weight = edge[2]
            start_point = coordinates[node1]
            end_point = coordinates[node2]
            self.canvas.scene.addLine(start_point[0], start_point[1], end_point[0], end_point[1],
                                      QPen(Qt.blue, 2))
            text = self.canvas.scene.addSimpleText(f"{weight * 200 / 115:.2f}m", QFont("Arial", 8))
            text.setPos((start_point[0] + end_point[0]) / 2, (start_point[1] + end_point[1]) / 2)

    def kruskal(self):
        edges = []  # 创建边列表
        for i in range(len(coordinates)):  # 遍历顶点
            for j in range(i + 1, len(coordinates)):  # 遍历其他顶点
                dist = np.sqrt(  # 计算距离
                    (coordinates[i][0] - coordinates[j][0]) ** 2 + (coordinates[i][1] - coordinates[j][1]) ** 2)
                edges.append((i, j, dist))  # 将结果添加到边列表
        edges.sort(key=lambda x: x[2])  # 对边列表进行排序

        parent = [i for i in range(len(coordinates))]  # 创建父节点列表
        rank = [0] * len(coordinates)  # 创建等级列表
        mst = []  # 创建最小生成树列表
        for edge in edges:  # 遍历边
            x, y, weight = edge  # 获取边的起点、终点和权重
            x_root = self.find(parent, x)  # 获取x的根节点
            y_root = self.find(parent, y)  # 获取y的根节点
            if x_root != y_root:  # 如果根节点不同
                mst.append((x, y, weight))  # 将结果添加到最小生成树中
                self.union(parent, rank, x_root, y_root)  # 进行合并操作

        return mst  # 返回最小生成树

    def find(self, parent, i):  # 查找函数
        if parent[i] == i:  # 如果父节点就是自己
            return i  # 返回自己
        return self.find(parent, parent[i])  # 递归查找父节点

    def union(self, parent, rank, x, y):  # 合并函数
        x_root = self.find(parent, x)  # 获取x的根节点
        y_root = self.find(parent, y)  # 获取y的根节点

        if rank[x_root] < rank[y_root]:  # 如果x的等级小于y的等级
            parent[x_root] = y_root  # 将x的根节点设置为y的根节点
        elif rank[x_root] > rank[y_root]:  # 如果x的等级大于y的等级
            parent[y_root] = x_root  # 将y的根节点设置为x的根节点
        else:  # 如果等级相等
            parent[y_root] = x_root  # 将y的根节点设置为x的根节点
            rank[x_root] += 1  # 增加x的等级


if __name__ == '__main__':
    logging.info("启动应用程序.")
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.aboutToQuit.connect(lambda: logging.info("关闭应用程序."))
    sys.exit(app.exec_())
