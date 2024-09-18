from lida import Manager, TextGenerationConfig, llm
import streamlit as st
import http.client
import hashlib
import urllib
import random
import json
# 通过编写 Python 脚本（使用 Streamlit 的 API）来构建用户界面，直接利用你的数据科学代码来创建应用，而无需成为前端开发者或学习复杂的 Web 开发框架
# 支持多种数据可视化库，如 Matplotlib、Pandas、Plotly、Altair 等。你可以轻松地将这些库生成的图表嵌入到你的 Streamlit 应用中，创建丰富的数据可视化效果
import pandas as pd
lida = Manager(text_gen = llm("openai", api_key='sk-proj-KECsGXY1JAYok3NdNx89T3BlbkFJOIKR0h02BG5u8CZf7lvz')) # !! api key
textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)

selected_dataset = None

upload_own_data = st.sidebar.checkbox("上传你自己的数据")
if upload_own_data:
    uploaded_file = st.sidebar.file_uploader("选择一个CSV或JSON文件", type=["csv", "json"])

    if uploaded_file is not None:
        # Get the original file name and extension
        file_name, file_extension = os.path.splitext(uploaded_file.name)

        # Load the data depending on the file type
        if file_extension.lower() == ".csv":
            data = pd.read_csv(uploaded_file)
        elif file_extension.lower() == ".json":
            data = pd.read_json(uploaded_file)

        # Save the data using the original file name in the data dir
        uploaded_file_path = os.path.join("data", uploaded_file.name)
        data.to_csv(uploaded_file_path, index=False)

        selected_dataset = uploaded_file_path

        datasets.append({"label": file_name, "url": uploaded_file_path})

        # st.sidebar.write("Uploaded file path: ", uploaded_file_path)
else:
    selected_dataset = datasets[[dataset["label"]
                                 for dataset in datasets].index(selected_dataset_label)]["url"]

st.sidebar.write("### 选择可视化方法")

summarization_methods = [
            {"label": "llm",
            "description":
            "使用LLM为数据生成默认摘要，添加列的数据类型和数据集描述等详细信息"},
            {"label": "default",
            "description": "使用数据集列统计信息和列名作为摘要"},

            {"label": "columns", "description": "使用数据集列名作为摘要"}]
selected_method_label = st.sidebar.selectbox(
            '选择摘要方法',
            options=[method["label"] for method in summarization_methods],
            index=0
        )

selected_method = summarization_methods[[
            method["label"] for method in summarization_methods].index(selected_method_label)]["label"]

        # add description of selected method in very small font to sidebar
selected_summary_method_description = summarization_methods[[
            method["label"] for method in summarization_methods].index(selected_method_label)]["description"]

if selected_method:
            st.sidebar.markdown(
                f"<span> {selected_summary_method_description} </span>",
                unsafe_allow_html=True)


# summary = lida.summarize("https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv", summary_method="default", textgen_config=textgen_config)
summary = lida.summarize(
            selected_dataset,
            summary_method=selected_method,
            textgen_config=textgen_config)

goals = lida.goals(summary, n=2, textgen_config=textgen_config)

if "dataset_description" in summary:
    st.write(summary["dataset_description"])
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
    nfields_df = pd.DataFrame(nfields)
    st.write(nfields_df)
else:
    st.write(str(summary))


if summary:
    st.sidebar.write("### 目标选择")
    num_goals = st.sidebar.slider(
        "生成的目标数量",
        min_value=1,
        max_value=10,
        value=4)
    own_goal = st.sidebar.checkbox("添加你的目标")

    # **** lida.goals *****
    goals = lida.goals(summary, n=num_goals, textgen_config=textgen_config)
    st.write(f"## 目标 ({len(goals)})")

    default_goal = goals[0].question
    goal_questions = [goal.question for goal in goals]

    if own_goal:
        user_goal = st.sidebar.text_input("描述你的目标")

        if user_goal:
            new_goal = Goal(question=user_goal, visualization=user_goal, rationale="")
            goals.append(new_goal)
            goal_questions.append(new_goal.question)

    selected_goal = st.selectbox('选择一个可视化目标', options=goal_questions, index=0)

    # st.markdown("### Selected Goal")
    selected_goal_index = goal_questions.index(selected_goal)
    st.write(goals[selected_goal_index])

    selected_goal_object = goals[selected_goal_index]

    # Step 5 - Generate visualizations
    if selected_goal_object:
        st.sidebar.write("## 可视化库")
        visualization_libraries = ["seaborn", "matplotlib", "plotly"]

        selected_library = st.sidebar.selectbox(
            '选择一个可视化库',
            options=visualization_libraries,
            index=0
        )

        # Update the visualization generation call to use the selected library.
        st.write("## 可视化")

        # slider for number of visualizations
        num_visualizations = st.sidebar.slider(
            "生成的可视化数量",
            min_value=1,
            max_value=10,
            value=1)

        # textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=True)
        # **** lida.visualize *****
        # 实现lida.visualize的方法
        visualizations = lida.visualize(
            summary=summary,
            goal=selected_goal_object,
            textgen_config=textgen_config,
            library=selected_library)

        viz_titles = [f'可视化 {i + 1}' for i in range(len(visualizations))]

        selected_viz_title = st.selectbox('选择一个可视化', options=viz_titles, index=0)

        selected_viz = visualizations[viz_titles.index(selected_viz_title)]

        if selected_viz.raster:
            from PIL import Image
            import io
            import base64

            imgdata = base64.b64decode(selected_viz.raster)
            img = Image.open(io.BytesIO(imgdata))
            st.image(img, caption=selected_viz_title, use_column_width=True)

        if st.button('保存图片'):
            image_data_list = [selected_viz.raster]
            savedata(image_data_list)
            st.write('保存成功！')

        st.write("### 可视化代码")
        st.code(selected_viz.code)

    reviz = st.sidebar.checkbox("重新生成")
    evacode = st.sidebar.checkbox("可视化评估")
    expcode = st.sidebar.checkbox("可视化解释")
    recommendviz = st.sidebar.checkbox("推荐相关可视化")
    if reviz:
        st.write("## 重新生成")
        userfeedback = st.text_input('请输入修改条件')
        if userfeedback:
            repair = lida.repair(
                code=selected_viz.code,
                goal=selected_goal_object,
                summary=summary,
                feedback=userfeedback,
                textgen_config=textgen_config,
                library=selected_library)
            if repair[0].raster:
                from PIL import Image
                import io
                import base64

                imgdata = base64.b64decode(repair[0].raster)
                img = Image.open(io.BytesIO(imgdata))
                st.image(img, caption=selected_viz_title, use_column_width=True)

            st.write("### 可视化代码")
            st.code(repair[0].code)
            st.write("## 重新生成结束")
    if evacode:
        st.write("## 可视化评估")
        evaluation = lida.evaluate(
            code=selected_viz.code,
            goal=selected_goal_object,
            textgen_config=textgen_config,
            library=selected_library)
        st.subheader('漏洞')
        st.subheader(evaluation[0][0]['score'])
        st.write(baidu_translate(evaluation[0][0]['rationale']))
        st.subheader('数据转换')
        st.subheader(evaluation[0][1]['score'])
        st.write(baidu_translate(evaluation[0][1]['rationale']))
        st.subheader('功能')
        st.subheader(evaluation[0][2]['score'])
        st.write(baidu_translate(evaluation[0][2]['rationale']))
        st.subheader('图表类型选择')
        st.subheader(evaluation[0][3]['score'])
        st.write(baidu_translate(evaluation[0][3]['rationale']))
        st.subheader('代码')
        st.subheader(evaluation[0][4]['score'])
        st.write(baidu_translate(evaluation[0][4]['rationale']))
        st.subheader('美观')
        st.subheader(evaluation[0][5]['score'])
        st.write(baidu_translate(evaluation[0][5]['rationale']))
        st.write("## 可视化评估结束")
    if expcode:
        st.write("## 可视化解释")
        explanation = lida.explain(
            code=selected_viz.code,
            textgen_config=textgen_config,
            library=selected_library)
        # st.write(explanation)
        st.subheader('基本解释')
        st.write(baidu_translate(explanation[0][0]['explanation']))
        st.subheader('数据转换')
        st.write(baidu_translate(explanation[0][1]['explanation']))
        st.subheader('可视化处理')
        st.write(baidu_translate(explanation[0][2]['explanation']))
        st.write("## 可视化解释结束")
    if recommendviz:
        st.write("## 推荐相关可视化")
        recommender = lida.recommend(
            code=selected_viz.code,
            summary=summary,
            n=1,
            textgen_config=textgen_config,
            library=selected_library)
        if recommender[0].raster:
            from PIL import Image
            import io
            import base64

            imgdata = base64.b64decode(recommender[0].raster)
            img = Image.open(io.BytesIO(imgdata))
            st.image(img, caption=selected_viz_title, use_column_width=True)
            st.write("### 可视化代码")
            st.code(recommender[0].code)
        st.write("## 推荐相关可视化结束")