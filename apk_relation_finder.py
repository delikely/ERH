# -*- coding: utf-8 -*-
# Date:2022/3/29
# Author: 饭饭

import argparse
import os
import re
import json
import time
import zipfile
from androguard.core.bytecodes import apk
from androguard.core.androconf import show_logging
import logging
from alive_progress import alive_bar

banner ='''
 \\          =o) 
 (o>         /\\ 
_(()_apk2apk_\_V_
 //           \\ 
               \\
    -- Powered by Delikely
'''

def get_file_list(dir,filter_list):
    file_list = []
    for path, folders, files in os.walk(dir):
        for file in files:
            for filter in filter_list:
                if str(file).endswith(filter):
                    file_path = os.path.join(path, file)
                    file_list.append(file_path.replace("\\","/"))
    return file_list

def package_path_relation(filesystem_dir):
    packages = []
    package_to_path = {}
    path_to_package = {}
    apk_file_list = get_file_list(filesystem_dir,[".apk"])
    for apk_file in apk_file_list:
        package = package_name_extract(apk_file)
        if package:
            packages.append(package)
            path = apk_file.replace(filesystem_dir,"")
            if not str(path).startswith("/"):
                path = "/" + path
            package_to_path[package] = path
            path_to_package[path] = package
    return packages,package_to_path,path_to_package


def package_name_extract(apk_file):
    show_logging(level=logging.ERROR)
    package_name = ""
    try:
        app = apk.APK(apk_file)
        package_name = app.get_package()
    except Exception as e:
        print("解析失败",apk_file,e)
    return package_name
    
def match_keyword_apk_dex(apk_path, keyword):
    with zipfile.ZipFile(apk_path, 'r') as z:
        for filename in z.namelist():
            content = z.read(filename)
            matches = re.findall(keyword, content)
            if matches:
                return matches
            

def apk_relation_finder(filesystem_dir,project):
    if filesystem_dir[-1] != "/":
        filesystem_dir += "/"

    packages,package_to_path,path_to_package = package_path_relation(filesystem_dir)
    apk_file_list = get_file_list(filesystem_dir,[".apk",".vdex","vdex"])

    apk_relations = {}

    apk_num = len(apk_file_list)
    with alive_bar(apk_num) as bar:
        for apk_file in apk_file_list:
            try:
                with open(apk_file,"br") as f:
                    apk_data = f.read()
                    for package in packages:
                        # fliter own package name
                        try:
                            if package == path_to_package[str(apk_file).replace(filesystem_dir,"")]:
                                continue
                        except:
                            pass

                        # search package name in APK
                        if not apk_file.endswith(".apk") and re.search(bytes(package,encoding="utf-8"),apk_data):
                            try:
                                apk_relations[apk_file].append(package)
                            except:
                                apk_relations[apk_file] = [package]

                        # search package name in odex/cdex 
                        if apk_file.endswith(".apk") and match_keyword_apk_dex(apk_file,bytes(package,encoding="utf-8")):
                            # print(package,"in",apk_file,"dex")
                            try:
                                apk_relations[apk_file].append(package)
                            except:
                                apk_relations[apk_file] = [package]

            except Exception as e:
                print("Open apk error: ",e)
                continue
            bar()

    # 全量数据
    all_nodes = []
    all_links = []
    # 不含系统数据
    nodes = []
    links = []

    for path in apk_relations:
        source = str(path).split("/")[-1]
        for package in apk_relations[path]:
            system_apk_flag = False

            try:
                info = path_to_package[path.replace(filesystem_dir,"/")]
            except Exception as e:
                continue_flag = True
                if path.endswith("framework-res.apk"):
                    info = "android"
                    continue

                if path.startswith("/apex/"):
                    info = path_to_package[ "/system" + path.replace(filesystem_dir,"/")]
                    continue

                if path.endswith(".odex") or path.endswith(".vdex"):
                    info = ""
                    continue_flag = False 

                if continue_flag:
                    print("source_node error:",e,path)
                    continue

            source_node = {"name":source,"value":info}
            try:
                if package.startswith("com.android.internal.systemui") or package.startswith("com.android.systemui"):
                    target = ""
                else:
                    target = str(package_to_path[package]).split("/")[-1]
                    target_node = {"name":target,"value":package}

                # 数据加载时会异常
                # {
                #     "name": "base.apk",
                #     "value": "com.koushikdutta.vysor"
                # },
                # {
                #     "name": "base.apk",
                #     "value": "com.thundercomm.motormaster"
                # },
                # 暂时忽略
                if source == "base.apk":
                    continue
                if "base" == source.split(".")[0] or "base" == target.split(".")[0]:
                    continue                

                
                if source != target:
                    if source_node not in all_nodes:
                        all_nodes.append(source_node)
                    if  target_node not in all_nodes:
                        all_nodes.append(target_node)
                    all_links.append({"source":source,"target":target})
 

                    # filter system build-in app
                    if source.startswith("com.android") or  info.startswith("com.android")  or target.startswith("com.android") or  package.startswith("com.android"):
                        system_apk_flag = True
                    if source.startswith("android.") or  info.startswith("android.")  or target.startswith("android.") or  package.startswith("android."):
                        system_apk_flag =True
                    if source=="framework-res.apk" or  info == "android" or target=="framework-res.apk":
                        system_apk_flag = True

                    if not system_apk_flag:
                        if source_node not in nodes:
                            nodes.append(source_node)
                        if  target_node not in nodes:
                            nodes.append(target_node)
                        links.append({"source":source,"target":target})

            except Exception as e:
                print("target_node error",e,path)
                pass

    graph_data = {"nodes":nodes,"links":links,"categories": [{"name": "A"}]}

    build_time = str(time.time()).split(".")[0] 
    
    data_dir = os.path.abspath(os.path.dirname(__file__))
    diagram_path = os.path.join(data_dir,"diagram/" + project + "_" + build_time)
    if not os.path.exists(diagram_path):
        os.mkdir(diagram_path)
    realtion_file = build_time +  "_" + project
    project_dir = diagram_path + "/" 

    with open(project_dir + realtion_file + '_apk-relation.json','w',encoding='utf8') as f:
        json.dump(graph_data,f,
        indent=4,
        separators=(',', ': ')
    )
    
    graph_data_all =  {"nodes":all_nodes,"links":all_links,"categories": [{"name": "A"}]}
    with open(project_dir + realtion_file + '_apk-relation-all.json','w',encoding='utf-8') as f:
        json.dump(graph_data_all,f,
        indent=4,
        separators=(',', ': ')
    )
        
    url = f"http://127.0.0.1:13337/apk-relation?date={build_time}&project={project}"
    print("Relation Diagram url: ",url)

if __name__ == '__main__':
    print(banner)
    parser = argparse.ArgumentParser(prog='PROG', usage='%(prog)s [options]', description='Android APK relation generation tool')
    parser.add_argument('-d', '--dir', help='Android root filesystem directory',default="E:/CAR/固件文件系统/VW ICAS3CN_MP_2959/IVI filesystem/")
    parser.add_argument('-p', '--project', help='Project name',default="hacking")
    args = parser.parse_args()
    filesystem_dir = args.dir
    project = args.project
    apk_relation_finder(filesystem_dir,project)


