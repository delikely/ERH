from flask import Flask, render_template,send_file,make_response,jsonify
from flask import request
from flask import jsonify
import os
import json

app = Flask(__name__)
data_dir = os.path.abspath(os.path.dirname(__file__)) + "/../"

@app.route("/apk-relation")
def apk_relation_page():
    return render_template("apk-relation.html")

@app.route("/get/relations")
def apk_relation():
    date = request.args.get("date")
    project = request.args.get("project")
    type = request.args.get("type")
    filter = request.args.get("filter")

    project_path = project + "_" + date

    if filter != "None" and filter != "":
        file = date + "_" + project + "_apk-relation-all.json"
    else:
        if type == "part":
            file = date + "_" + project + "_apk-relation.json"
        elif type == "all":
            file = date + "_" + project + "_apk-relation-all.json"
        else:
            file = date + "_" + project + "_apk-relation.json"
    
    error_data = jsonify({"nodes":[{"name":"Null","value":"Use apk_relation_finder.py create diagram fisrt"}],"links":[],"categories":[{"name":"A"}]})
    if "/" not in project_path and "/" and "/" not in file:
        try:
            with open(os.path.join(data_dir,"diagram/" + project_path +"/"+ file),"r") as f:
                data = json.load(f)
                if filter != "None" and filter != "":
                    
                    filter_data = {"nodes": [],"links":[],"categories": [{"name": "A"}]}

                    for link in data["links"]:
                        if link["source"] == filter or link["target"] == filter:
                            filter_data["links"].append(link)

                    if filter.endswith(".apk"):
                        filter = filter[0:-4] +".vdex"
                    if filter.endswith(".apk"):
                        filter = filter[0:-5] +".apk"

                    print("new filter:",filter)
                    for link in data["links"]:
                        if link["source"] == filter or link["target"] == filter:
                            for exist_link in filter_data:
                                if exist_link == link:
                                    continue
                                filter_data["links"].append(link)


                    for node in data["nodes"]:
                        name = node["name"]
                        for link in filter_data["links"]:
                            if link["source"] == name or link["target"] == name:
                                filter_data["nodes"].append(node)
                                break
                    
                    data = filter_data
                return jsonify(data)
        except Exception as e:
            print("Can't access diagram file",e)
            pass
    return error_data


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    app.run(
        host='127.0.0.1',
        # host='0.0.0.0',
        port= 13337,
        # debug=True
    )