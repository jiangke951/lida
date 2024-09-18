from flask import Flask, request, jsonify,url_for
from flask_cors import CORS
from config import get_data, send_cc, send_data
import pandas as pd
from lida import Manager, TextGenerationConfig, llm
import streamlit as st
import http.client
import hashlib
import urllib
import random
import json
import io as ioe # 确保这里你显式地导入了 io 模块



app = Flask(__name__)
CORS(app)



@app.route("/")
def hello_world():
    # 注意：对于静态文件，你不需要在 filename 中包含 'static/' 前缀
    # Flask 会自动将请求重定向到正确的静态文件目录
    image_url = url_for('static', filename='test.png')
    return f"""  
        <!DOCTYPE html>  
        <html>  
        <head>  
            <title>Image Display</title>  
        </head>  
        <body>  
            <h1>The Image</h1>  
            <img src="{image_url}" alt="Test Image">  
        </body>  
        </html>  
        """

@app.route('/arg/hello', methods=['post'])
def hello():
    # 获取客户端发来的表单信息
    info = get_data(request.form)
    print(info)

    return 'Hello'

@app.route('/lida/front/test/sendForm', methods=['post'])
def send_form():
    # response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:4056'
    # 获取客户端发来的表单信息
    '''
    file = request.files['file']
    stream = ioe.StringIO(file.stream.read().decode('utf-8'))
    df = pd.read_csv(stream)
    lida = Manager(text_gen=llm("openai", api_key='sk-proj-KECsGXY1JAYok3NdNx89T3BlbkFJOIKR0h02BG5u8CZf7lvz'))  # !! api key
    textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)
    summary = lida.summarize(data=df,summary_method="default", textgen_config=textgen_config)
    goals = lida.goals(summary, n=2, textgen_config=textgen_config)
    '''
    info = get_data(request.form)
    lida = Manager(
        text_gen=llm("openai", api_key='sk-proj-KECsGXY1JAYok3NdNx89T3BlbkFJOIKR0h02BG5u8CZf7lvz'))
    textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)

    summary = lida.summarize("https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv",
                             summary_method="default", textgen_config=textgen_config)
    goals = lida.goals(summary, n=2, textgen_config=textgen_config)

    goalData = []
    for goal in goals:
        transformed_goal = {
            'id': goal.index,
            'name': goal.question,  # 假设我们用question作为name
            'value': goal.visualization
        }
        goalData.append(transformed_goal)

    chartData = []

    if "fields" in summary:
        fields = summary["fields"]
        nfields = []
        for field in fields:
            flatted_fields = {}
            flatted_fields["column"] = field["column"]

            for row in field["properties"].keys():
                if row != "samples":
                    flatted_fields[row] = field["properties"][row]
                else:
                    flatted_fields[row] = str(field["properties"][row])

            nfields.append(flatted_fields)
        # nfields_df = pd.DataFrame(nfields)
        headers = list(nfields[0].keys()) if nfields else []

        # 初始化一个空列表来存储数据行
        rows = []

        # 遍历每个对象，获取其值作为数据行
        for obj in nfields:
            row = list(obj.values())
            rows.append(row)

            # 将表头和数据行组合成一个新的二维数组
        chartData = [headers] + rows

        print(chartData)


    print(goalData)

    # selected_goal_object = goals[0]
    # selected_library = "matplotlib"
    selected_library = info.get('category', 'matplotlib')
    print(selected_library)
    selected_goal_object = info.get('goal', goals[0])
    print(selected_goal_object)
    # 实现lida.visualize的方法
    visualizations = lida.visualize(
        summary=summary,
        goal=selected_goal_object,
        textgen_config=textgen_config,
        library=selected_library)

    visualizations_data = {}
    for i, visualization in enumerate(visualizations):
        viz_title = f'可视化 {i + 1}'
        viz_data = {
            # 'title': viz_title,
            # 'code': visualization.code  # 假设 visualization 对象有 code 属性
        }
        # selected_viz = visualizations[viz_titles]
        print(visualization)
        if visualization.raster:
            from PIL import Image
            import io
            import base64

            # 将Base64编码的字符串解码为字节流
            imgdata = base64.b64decode(visualization.raster)
            # 使用PIL打开字节流为图像对象
            img = Image.open(io.BytesIO(imgdata))

            # 将PIL图像对象转换为字节流（保存为PNG格式）
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # 将字节流转换为Base64编码的字符串
            img_data = base64.b64encode(img_bytes).decode('utf-8')

            viz_data['img'] = img_data  # 将Base64字符串存储在viz_data中
            viz_data['code'] =visualization.code
        else:
            viz_data['img'] = None  # 或者你可以设置为一个占位符或默认图片
            viz_data['code'] = None

        visualizations_data[viz_title] = viz_data

        # 展示 code（如果需要）
    print("展示")
    print(visualizations_data)
    # 提取 visualizations_data 中的 img 值
    img_url = list(visualizations_data.values())[0]['img']  # 假设 visualizations_data 中只有一个条目
    code = list(visualizations_data.values())[0]['code']
    # 遍历 goalData 并添加 imageUrl 键
    for goal in goalData:
        goal['imageUrl'] = img_url
        goal['code'] = code
    return send_data({'status': 0, 'msg': '成功', 'chartData': chartData, 'goalData': goalData})

@app.route('/lida/front/test/sendForm1', methods=['post'])
def send_form1():
    info = get_data(request.form)
    file = request.files['file']
    print(file)
    exit()

    lida = Manager(
        text_gen=llm("openai", api_key='sk-proj-KECsGXY1JAYok3NdNx89T3BlbkFJOIKR0h02BG5u8CZf7lvz'))
    textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)

    summary = lida.summarize("https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv",
                             summary_method="default", textgen_config=textgen_config)
    goals = lida.goals(summary, n=2, textgen_config=textgen_config)

    goalData = []
    for goal in goals:
        transformed_goal = {
            'id': goal.index,
            'name': goal.question,  # 假设我们用question作为name
            'value': goal.visualization
        }
        goalData.append(transformed_goal)

    chartData = []

    if "fields" in summary:
        fields = summary["fields"]
        nfields = []
        for field in fields:
            flatted_fields = {}
            flatted_fields["column"] = field["column"]

            for row in field["properties"].keys():
                if row != "samples":
                    flatted_fields[row] = field["properties"][row]
                else:
                    flatted_fields[row] = str(field["properties"][row])

            nfields.append(flatted_fields)
        # nfields_df = pd.DataFrame(nfields)
        headers = list(nfields[0].keys()) if nfields else []

        # 初始化一个空列表来存储数据行
        rows = []

        # 遍历每个对象，获取其值作为数据行
        for obj in nfields:
            row = list(obj.values())
            rows.append(row)

            # 将表头和数据行组合成一个新的二维数组
        chartData = [headers] + rows

        print(chartData)


    print(goalData)
    selected_goal_object = goals[0]
    selected_library = "matplotlib"
    # 实现lida.visualize的方法
    visualizations = lida.visualize(
        summary=summary,
        goal=selected_goal_object,
        textgen_config=textgen_config,
        library=selected_library)

    visualizations_data = {}
    for i, visualization in enumerate(visualizations):
        viz_title = f'可视化 {i + 1}'
        viz_data = {
            # 'title': viz_title,
            # 'code': visualization.code  # 假设 visualization 对象有 code 属性
        }
        # selected_viz = visualizations[viz_titles]
        print(visualization)
        if visualization.raster:
            from PIL import Image
            import io
            import base64

            # 将Base64编码的字符串解码为字节流
            imgdata = base64.b64decode(visualization.raster)
            # 使用PIL打开字节流为图像对象
            img = Image.open(io.BytesIO(imgdata))

            # 将PIL图像对象转换为字节流（保存为PNG格式）
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # 将字节流转换为Base64编码的字符串
            img_data = base64.b64encode(img_bytes).decode('utf-8')

            viz_data['img'] = img_data  # 将Base64字符串存储在viz_data中
            viz_data['code'] =visualization.code
        else:
            viz_data['img'] = None  # 或者你可以设置为一个占位符或默认图片
            viz_data['code'] = None

        visualizations_data[viz_title] = viz_data

        # 展示 code（如果需要）
    print("展示")
    print(visualizations_data)
    # 提取 visualizations_data 中的 img 值
    img_url = list(visualizations_data.values())[0]['img']  # 假设 visualizations_data 中只有一个条目
    code = list(visualizations_data.values())[0]['code']
    # 遍历 goalData 并添加 imageUrl 键
    for goal in goalData:
        goal['imageUrl'] = img_url
        goal['code'] = code
    return send_data({'status': 0, 'msg': '成功', 'chartData': chartData, 'goalData': goalData})


@app.route('/lida/front/test/visualization', methods=['post'])
def visualization():
    # response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:4056'
    # 获取客户端发来的表单信息

    # file = request.files['file']
    # df = pd.read_csv(file)
    # lida = Manager(text_gen=llm("openai", api_key='sk-proj-KECsGXY1JAYok3NdNx89T3BlbkFJOIKR0h02BG5u8CZf7lvz'))  # !! api key
    # textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)
    # summary = lida.summarize(data=df,summary_method="default", textgen_config=textgen_config)
    # goals = lida.goals(summary, n=2, textgen_config=textgen_config)
    info = get_data(request.form)
    selected_goal_index = info[goal_index]
    selected_library = info[library]
    lida = Manager(
        text_gen=llm("openai", api_key='sk-proj-KECsGXY1JAYok3NdNx89T3BlbkFJOIKR0h02BG5u8CZf7lvz'))  # !! api key
    textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)

    summary = lida.summarize("https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv",
                             summary_method="default", textgen_config=textgen_config)
    goals = lida.goals(summary, n=2, textgen_config=textgen_config)

    selected_goal_object = goals[selected_goal_index]
    # 实现lida.visualize的方法
    visualizations = lida.visualize(
        summary=summary,
        goal=selected_goal_object,
        textgen_config=textgen_config,
        library=selected_library)

    visualizations_data = []

    for i, visualization in enumerate(visualizations):

        viz_data = {
            'title': viz_title,
        }

        if visualization.raster:
            from PIL import Image
            import io
            import base64

            # 将Base64编码的字符串解码为字节流
            imgdata = base64.b64decode(visualization.raster)
            # 使用PIL打开字节流为图像对象
            img = Image.open(io.BytesIO(imgdata))

            # 将PIL图像对象转换为字节流（保存为PNG格式）
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # 将字节流转换为Base64编码的字符串
            img_data = base64.b64encode(img_bytes).decode('utf-8')

            viz_data['img'] = img_data  # 将Base64字符串存储在viz_data中

        else:
            viz_data['img'] = None  # 或者你可以设置为一个占位符或默认图片

        # visualizations_data[viz_title] = viz_data

        # 展示 code（如果需要）
    print("展示")
    print(visualizations_data)

    # 结束实验
    return send_data({'status': 0, 'msg': '成功', 'visualizations_data': visualizations_data})


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=9540)
