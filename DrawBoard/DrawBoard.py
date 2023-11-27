"""使用opencv和numpy制作绘图板"""

import cv2
import numpy as np


class MainProcess:
    """主流程类,包含6个方法,定义一些用户常用操作"""

    # 建立画笔颜色,尺寸,绘制字体字典用来供用户索引
    dict_pencolor = {
        'blue': (255, 0, 0), 'green': (0, 255, 0), 'red': (0, 0, 255), 'white': (255, 255, 255), 'black': (0, 0, 0),
        'springgreen': (127, 255, 0), 'gold': (0, 215, 255), 'purple': (240, 32, 160), 'yellow': (0, 255, 255)
    }
    list_pen_size = [1, 2, 3, 4]
    list_font = [1, 2, 3, 4]

    def __init__(self, initial_image, download_address):
        """初始化类:初始画布,保存图片的地址,存储image的列表画笔的一些参数:黑色;1号尺寸;1号字体"""

        self.initial_image = initial_image
        self.download_address = download_address
        self.list_save_image = [self.initial_image.copy()]
        self.pen_color = self.dict_pencolor['black']
        self.pen_size = self.list_pen_size[0]
        self.pen_font = self.list_font[0]

    def get_params(self):
        """获得参数"""
        return self.pen_color, self.pen_size, self.pen_font

    def change_params(self):
        """更改参数"""
        # 列出可供选项
        list_color_kinds = list(self.dict_pencolor.keys())
        print('可供选择的画笔颜色有以下几种:{}\n可供选择的画笔尺寸有{}种(从1开始计数)\n可供选择的字体有{}种(从1开始计数)'.format(','.join(list_color_kinds),
                                                                                     len(self.list_pen_size),
                                                                                     len(self.list_font)))
        # 用户进行操作
        while True:
            try:
                list_user_input = input('输入c代表更改画笔颜色,输入s代表更改画笔尺寸,输入f代表更改绘画字体.\n请输入至少一个字母,至多三个字母,字母之间用空格隔开:\n').split(
                    ' ')
                if 1 <= len(list_user_input) <= 3:
                    if 'c' in list_user_input:
                        self.pen_color = self.dict_pencolor[input('请输入更改画笔的颜色:')]
                    if 's' in list_user_input:
                        self.pen_size = self.list_pen_size[eval(input('请输入更改画笔的尺寸:')) - 1]
                    if 'f' in list_user_input:
                        self.pen_font = self.list_font[eval(input('请输入更改画笔的字体:')) - 1]
                    break
                else:
                    print('请按照要求输入!')
            except KeyError:
                print('请按照要求输入!')

    def save_image(self, image):
        """实时保存操作:添加当前image到列表中(入栈)"""
        self.list_save_image.append(image.copy())

    def get_previous_image(self):
        """撤销操作:返回上一个image"""
        return self.list_save_image.pop()

    def download_image(self, image):
        """持久化存储image"""
        cv2.imwrite(f'{self.download_address}\\image.jpg', image)
        print('保存图片成功!')


def get_point_list():
    """获得绘图点等相关信息"""

    def mouse_callback(event, x, y, flags, point_list):
        # 记录用户行为
        point_list.append((event, x, y))

    # 获得用户操作的一系列行为事件
    point_list = []
    # 添加鼠标回调功能
    cv2.setMouseCallback('window', mouse_callback, point_list)

    # 设置小循环
    while True:
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    return point_list


def draw_line(image, pen_color, pen_size):
    # 获得绘图点坐标
    point_list = get_point_list()

    # 查询前两个事件为1的元组,并且将其存储到列表points里面
    points = []
    point_num = 0
    for i in point_list:
        if i[0] == 1 and point_num < 2:
            points.append((i[1], i[2]))
            point_num += 1

    # 两点确定一条直线
    cv2.line(image, points[0], points[1], pen_color, pen_size)


def draw_ellipse(image, pen_color, pen_size):
    # 获得绘图点坐标
    point_list = get_point_list()

    # 查询前三个事件为1的元组,并且将其存储到列表points里面
    points = []
    point_num = 0
    for i in point_list:
        if i[0] == 1 and point_num < 3:
            points.append((i[1], i[2]))
            point_num += 1

    # 确定椭圆圆心
    point = points[0]
    # 确定椭圆长短半轴,由于python3.8才支持欧氏距离公式,故此处造个该公式的小轮子
    long_axis = ((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2) ** 0.5
    short_axis = ((points[0][0] - points[2][0]) ** 2 + (points[0][1] - points[2][1]) ** 2) ** 0.5
    # 画椭圆
    cv2.ellipse(image, point, (int(long_axis), int(short_axis)), 0, 0, 360, pen_color, pen_size)


def draw_polylines(image, pen_color, pen_size):
    # 获得绘图点坐标
    point_list = get_point_list()

    # 查询所有事件为1的元组,并且将其存储到列表points里面
    points = []
    for i in point_list:
        if i[0] == 1:
            points.append((i[1], i[2]))
    # 将点坐标转化成数组形式
    plt = np.array(points, np.int32)

    # 用户选择绘制多边形种类(开环或者闭环)
    k = None
    while True:
        user_input = input('输入t绘制闭环多边形,输入f绘制开环多边形:')
        if user_input == 't':
            k = True
            break
        elif user_input == 'f':
            k = False
            break
        else:
            continue

    # 绘制多边形
    cv2.polylines(image, [plt], k, pen_color, pen_size)


def draw_text(image, pen_color, pen_size, pen_font):
    # 获得绘图点坐标
    point_list = get_point_list()

    # 查询第一个事件为1的元组,并且将其存储到列表points里面
    points = []
    for i in point_list:
        if i[0] == 1:
            points.append((i[1], i[2]))
            break

    # 获取起始坐标点,需要绘制的字符串
    point = points[0]
    text = input('请输入想要绘制的字符串,注意一定要是英文:')
    # 绘制字符串,默认字体大小为1
    cv2.putText(image, text, point, pen_font, 1, pen_color, pen_size)


def main():
    """主函数,耦合MainProcess类和众多函数,并结合while循环构成整个程序"""

    # 加载图片,给出保存图片位置
    org_image = np.full((480, 640, 3), 255, np.uint8)
    # 深拷贝图片,留着原图片给MainProcess.clear_drawingboard()用
    image = org_image.copy()
    # 图片保存至本地的地址
    save_address = r"C:\Users\34803\Desktop"

    # 实例化MainProcess类
    mainprocess = MainProcess(image, save_address)

    # 设置大循环
    while True:
        try:
            # 展示图片
            cv2.imshow('window', image)
            # 获得绘画参数
            pen_color, pen_size, pen_font = mainprocess.get_params()
            # 用户输入指令
            key = cv2.waitKey(1)

            # 更改画笔参数
            if key == ord('c'):
                mainprocess.change_params()
            # 画直线
            if key == ord('l'):
                draw_line(image, pen_color, pen_size)
            # 画椭圆
            if key == ord('e'):
                draw_ellipse(image, pen_color, pen_size)
            # 画多边形
            if key == ord('p'):
                draw_polylines(image, pen_color, pen_size)
            # 画文字,只支持英文
            if key == ord('t'):
                draw_text(image, pen_color, pen_size, pen_font)
            # 保存此刻画布状态
            if key == ord('s'):
                mainprocess.save_image(image)
            # 画布回到上一个保存的状态
            if key == ord('g'):
                image = mainprocess.get_previous_image().copy()
            # 保存图片至本地
            if key == ord('d'):
                mainprocess.download_image(image)
            # 清空修改的痕迹,即将此刻的图片状态修改为原始图片
            if key == ord('o'):
                image = org_image.copy()
            # 退出程序
            if key == ord('q'):
                break

        except IndexError:
            print('索引错误!')


if __name__ == '__main__':
    """使用main函数可以解决传递一些麻烦参数等问题"""
    # 新建画图板窗口
    cv2.namedWindow('window', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('window', 640, 480)

    # 执行绘图功能
    main()

    # 销毁所有窗口
    cv2.destroyAllWindows()
