import os

if __name__ == '__main__':
    path = input("请输入tmx文件路径(必须由Tiled导出)\n如果你没有安装Tiled，请前往http://blog.mapeditor.org/安装。")
    exist = os.path.exists(path)
    if not exist:
        print("文件不存在！")
