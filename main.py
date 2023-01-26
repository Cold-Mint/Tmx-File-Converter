import os
import shutil
import xml.etree.ElementTree as ET

tmxPath = ""
exportPath = ""
# 瓦片文件输出目录
tilesPath = ""
# 房间模板输出目录
roomTemplatePath = ""
# 瓦片id字典(firstgid和瓦片id的映射)
idDict = {}
# 房间信息
roomData = {}
# 空id
EmptyId = "Empty"
# 游戏内的图层
layers = {"BackgroundWall", "BackgroundDecoration", "Ground", "Entity", "Player", "Foreground"}


# 复制文件
def copyfile(srcfile, dstpath):  # 复制函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.copy(srcfile, dstpath + fname)  # 复制文件
        print("copy %s -> %s" % (srcfile, dstpath + fname))


# 解析TileSet
def parseTileSet(xmlElement):
    sourcePath = xmlElement.attrib.get("source")
    # 截取tmx的父级目录 rfind倒找字符串 txmPath[:index] :的意思是从开头截取
    directoryPath = tmxPath[:tmxPath.rfind('\\')] + '\\'
    fullPath = directoryPath + sourcePath
    exist = os.path.exists(fullPath)
    if exist:
        tree = ET.parse(fullPath)
        root = tree.getroot()
        print("tileSet属性,名称" + root.attrib.get("name") + ",Tile总数" + root.attrib.get("tilecount"))
        for child in root:
            if child.tag == "image":
                imageSource = child.attrib.get("source")
                imagePath = directoryPath + imageSource
                if os.path.exists(imagePath):
                    # 图像存在,拷贝文件
                    copyfile(imagePath, tilesPath)
                    # 写配置文件
                    id = imageSource[:imageSource.index(".")]
                    idDict[xmlElement.attrib.get("firstgid")] = id
                    data = "tile:\n  id: " + id + "\n  path: " + imageSource
                    yamlFile = open(tilesPath + id + ".tile.yaml", "w", )
                    yamlFile.write(data)
                    yamlFile.close()
                else:
                    print("图像路径" + imagePath + "不存在。")
    else:
        print("位于" + fullPath + "的tsx引用,已丢失。")


# 处理图层(layer数据,待输出的文本数据)
# 返回新数据
def parseLayer(xmlElement):
    for child in xmlElement:
        if child.tag == "data":
            layerName = xmlElement.attrib.get("name")
            if layerName in layers:
                print("解析图层:" + layerName)
                # 处理数据
                index = 0
                for tile in child.text.split(","):
                    tile = tile.replace("\n", "")
                    if len(roomData) - 1 < index:
                        if tile == "0":
                            roomData[index] = EmptyId
                        else:
                            roomData[index] = "    - id: " + idDict[tile] + "\n      layer: " + layerName
                    else:
                        if roomData[index] == EmptyId:
                            roomData[index] = "    - id: " + idDict[tile] + "\n      layer: " + layerName
                    index += 1
            else:
                print("无法解析的图层 " + layerName)


if __name__ == '__main__':
    code = "run"
    while code == "run":
        path = input(
            "如果你没有安装Tiled，请前往http://blog.mapeditor.org/安装。\n输入exit即可退出程序。\n请输入tmx文件路径(必须由Tiled导出):\n")
        if path == "exit":
            print("再见！")
            code = "exit"
        else:
            tmxPath = path
            exist = os.path.exists(path)
            # D:\Project\Tiled\default\未命名.tmx
            # C:\Users\Lenovo\Desktop\exportPath
            if not exist:
                print("tmx文件不存在！")
            else:
                loop = "true"
                while loop == "true":
                    exportPath = input("输入输出目录,必须是文件夹哦:\n")
                    tilesPath = exportPath + "\\tiles\\"
                    roomTemplatePath = exportPath + "\\roomTemplates\\"
                    if os.path.exists(exportPath):
                        files = os.listdir(exportPath)  # 读入文件夹
                        fileNum = len(files)  # 统计文件夹中的文件个数
                        if not fileNum == 0:
                            print("输出目录不可用，必须是空目录！")
                        else:
                            loop = "false"
                    else:
                        # 文件夹不存在，新建一个。
                        os.makedirs(exportPath)
                        loop = "false"
                # 输出记录文件
                recordFile = open(exportPath + "\\README.txt", "w", encoding='utf8')
                recordFile.write(
                    "This file is exported by Tmx file converter. \nTmx File converter website :https://github.com/Cold-Mint/Tmx-File-Converter\nDeveloped by coldmint")
                recordFile.close()
                roomData.clear()
                idDict.clear()
                # 这里指定 空id
                idDict["0"] = EmptyId
                tree = ET.parse(path)
                root = tree.getroot()
                if root.tag.__str__() == "map":
                    width = root.attrib.get("width")
                    height = root.attrib.get("height")
                    total = int(width) * int(height)
                    print("地图信息,宽度" + width + ",高度" + height + ",合计" + str(total) + "个瓦片。")
                    # 如果文件夹不存在，创建
                    if not os.path.exists(roomTemplatePath):
                        os.makedirs(roomTemplatePath)
                    roomTemplateId = input("输入房间模板id:")
                    data = "roomTemplate:\n  id: " + roomTemplateId + "\n  width: " + width + "\n  height: " + height + "\n  data: "
                    for child in root:
                        tag = child.tag
                        if tag == "tileset":
                            parseTileSet(child)
                        elif tag == "layer":
                            parseLayer(child)
                    print("组织房间数据...")
                    if len(roomData) > 0:
                        for line in roomData.values():
                            if line == EmptyId:
                                data = data + "\n    - id: " + EmptyId
                            else:
                                data = data + "\n" + line
                        print(data)
                    else:
                        print("无效的瓦片放置数据，没有可识别的图层。")
                    yamlFile = open(roomTemplatePath + roomTemplateId + ".roomTemplate.yaml", "w", encoding='utf8')
                    yamlFile.write(data)
                    yamlFile.close()
                else:
                    print("根节点不是map！")
            print("执行完毕。\n---------")
