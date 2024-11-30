import streamlit as st
from package import openai_sdk as sdk
import json
import os
import re

# 区分中外文
def contains_chinese_text(text):
    return bool(re.search('[\u4e00-\u9fff]', text))

st.title("Brainwrite lab🧠")

# 支持的模型
glm_model = ["glm-4-flash"]
spake_model = ["general","4.0Ultra"]
openai_model = ["gpt-3.5-turbo", "gpt-4"]

# 获取当前路径
current_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_path, "data/background.json")

# 读取身份背景词
with open(data_path, "r", encoding="utf-8") as f:
    background_dict = json.load(f)
background_list = []
for key, value in background_dict.items():
    background_list.append(key)

# 侧边栏中的选项
with st.sidebar:
    api_key = st.text_input("API Key", key="chatbot_api_key", type="password",value="516d0fb9b4f436fea223319e15e98f97.dLKy63UjQa6CwyH6")
    model = st.selectbox("Model", ["glm-4-flash", "general", "4.0Ultra"])
    selected = st.multiselect(
    "select who participate",
    background_list,
    max_selections=4,)
    st.divider()
    st.write("Begin new brainstorm")
    if st.button("new"):
        if "messages" in st.session_state:
            del st.session_state["messages"]
            if "selected" in st.session_state:
                for person in st.session_state["selected"]:
                    if person in st.session_state:
                        del st.session_state[person]
                        del st.session_state["paper_" + person]
                    else:
                        pass
                del st.session_state["selected"]
        if "mindmap" in st.session_state:
            del st.session_state["mindmap"]

        st.rerun()
        
    topic = st.text_area("Input the brainstorm topic",key="new_topic")

    st.divider()
    st.write("click refresh to interact with our new mindmap!")

    def refresher():
        st.session_state["new_topic"] = ""
        st.session_state["modified_topic"] = ""

    if st.button("refresh",on_click=refresher):
        temp = 0
        
    if not "summary" in st.session_state:
        st.session_state["summary"] = '''
    - None
'''

    summary_lines = st.session_state["summary"].splitlines()
    # 在侧边栏中显示生成的主题
    st.write("Generated Topics:")
    selected_topic = st.selectbox("Select a topic:", summary_lines)
    # 添加文本输入框供用户修改标题
    modified_topic = st.text_input("Modify the selected topic:",key = "modified_topic")
    # 提取层级前缀
    level_prefix = selected_topic[:len(selected_topic) - len(selected_topic.lstrip())]
    # 如果用户输入的内容不以相同的前缀开头，则添加前缀
    if modified_topic.strip() and not modified_topic.startswith(level_prefix):
        modified_topic = level_prefix + modified_topic.strip()

    # 更新 summary 中的标题
    if selected_topic:
        if modified_topic:
            # 更新选中的主题
            st.session_state["summary"] = st.session_state["summary"].replace(selected_topic, modified_topic)
            topic2 = modified_topic
            print("存在"+modified_topic)
        else:
            topic2 = selected_topic
        st.session_state["selected_topic"] = topic2



# 根据模型选择API地址
if model in glm_model:
    url = "https://open.bigmodel.cn/api/paas/v4/"
elif model in spake_model:
    url = 'https://spark-api-open.xf-yun.com/v1'
elif model in openai_model:
    url = ''



if "messages" not in st.session_state:
    introduction = """
**Brainwriting** is a creative technique used to generate ideas within a group setting. 

**Process:**
1. **Define the Problem:** Start by clearly stating the problem or topic that needs to be addressed.
2. **Individual Writing:** Each participant writes down their ideas individually, often on a sheet of paper or a digital platform.
3. **Passing Ideas:** After a set time, participants pass their ideas to the next person, who then adds to or builds upon them.
4. **Rounds of Writing:** This process is repeated for several rounds to ensure that all ideas are shared and developed.
5. **Review and Discussion:** Once all ideas have been collected, the group reviews them and discusses the most promising ones.

You can get api key in 
- [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
- [https://xinghuo.xfyun.cn/sparkapi](https://xinghuo.xfyun.cn/sparkapi)
"""
    st.session_state["messages"] = [{"role": "assistant", "content": introduction}]
    with st.chat_message("assistant"):
        st.write(introduction)
else:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

if "selected" not in st.session_state:
    pass

else:
    # 输出历史结果
    st.chat_message("assistant").write("Present the results of the discussion from the perspective of each participant.")
    for person in st.session_state["selected"]:
        with st.chat_message("assistant"):
            st.write("**%s**\'s statements"%person)
            st.divider()
            for item in st.session_state[person]:
                st.write('- ' + item)
    
    st.chat_message("assistant").write("Show what's on each note")
    for person in st.session_state["selected"]:
        with st.chat_message("assistant"):
            st.write("The contents on the note of **%s**:"%person)
            st.divider()
            for item in st.session_state["paper_" + person]:
                st.write('- ' + item)
    
    st.chat_message("assistant").write(st.session_state["summary"])

st.sidebar.write("Brainwrite lab🧠")
if st.sidebar.button("continue"):
    if not api_key:
        st.info("Please add your API key to continue.")
        st.stop()
    if len(selected) != 4 and len(selected) != 3:
        st.info("Please select who participate (4 or 3 people).")
        st.stop()
    if not topic:
        if not topic2:
            st.info("Please input the brainstorm topic.")
            st.stop()
        else:
            topic1 = topic2
    else:
        topic1 = topic

    st.session_state["selected"] = []
    for item in selected:
        st.session_state["selected"].append(item)
    
    st.session_state.messages.append({"role": "user", "content": topic1})
    st.chat_message("user").write(topic1)

    # 储存每个专家的发言
    for person in selected:
        st.session_state[person] = []

    # 储存每个纸条的发言
    for person in selected:
        st.session_state["paper_" + person] = []
    
    for i in range(len(selected)):
        num_order = 0
        if i == 0:
            for person in selected:
                sys_back = background_dict[person]
                if contains_chinese_text(person):
                    prompt = '''
### 现在正在对【%s】这个话题进行头脑风暴。

### 请根据你的身份背景，站在你所在领域的视角，参与头脑风暴，并给出你的思考。请用中文回答。

### 生成内容要求简略，用一小段话概括，要有启发性观点，并提出具体的看法或方案.

### 只生成严谨的发言，不要生成其他内容，不需要介绍自己。
'''%topic1
                else:
                    prompt ='''
### Brainstorming on **%s** right now.

### According to your background, stand in the perspective of your field, participate in brainstorming, and give your thoughts. **Please answer in English**.

### The generated content should be brief, Sum your viewpoints up in one paragraph (less than 100 words). Please provide **inspiring viewpoints**. And give your specific opinions or solutions.

### Only generate rigorous statements, do not generate other content. Do not introduce yourself.
'''%topic1
                with st.spinner("Round %d, **%s** is thinking...🧠"%(i+1,person)):
                    msg = sdk.api_call(api_key, url , model, [{"role": "system", "content": sys_back}
                                                            ,{"role": "user", "content": prompt}])
                # st.session_state.messages.append({"role": "assistant", "content": msg})
                # st.chat_message("assistant").write(msg)
                st.session_state[person].append(msg)
                st.session_state["paper_" + person].append("%s:\n\n%s\n\n"%(person,msg))
                history_order = []
                for item in selected:
                    history_order.append(item)
        else:
            # 传纸条
            first_element = history_order.pop(0)
            history_order.append(first_element)
            

            for person in selected:
                # 提取历史信息
                history = ""
                for item in st.session_state["paper_" + history_order[num_order]]:
                    history += item + "\n\n"

                history = "[%s]"%history
                print(history)

                sys_back = background_dict[person]
                if contains_chinese_text(person):
                    prompt = '''
%s

### 现在正在对【%s】这个话题进行头脑风暴。以上内容是其他参与者的发言。

### 请根据你的身份背景，站在你所在领域的视角，参与头脑风暴。

### 请仔细阅读其他参与者的发言，根据你的知识背景，继续发展他们的观点。

### 只生成严谨的发言，不要生成其他内容，不要回答自己是谁，请用中文回答。

### 生成内容要求简略，用一小段话概括，要有启发性观点，并提出具体的看法或方案。
'''%(history,topic1)
                else:
                    prompt ='''
%s

### Brainstorming on **%s** right now. The above are comments by other participants.

### Participate in brainstorming according to your identity background, standing in the perspective of your field.

### Please carefully read the comments by other participants, based on your knowledge background, continue to develop their viewpoints. Put forward specific ideas and methods.

### The generated content should be brief, Sum your viewpoints up in one paragraph (less than 100 words). No need to introduce yourself.

### Only generate rigorous statements, do not generate other content, please answer in English. 
'''%(history,topic1)
                with st.spinner("Round %d, **%s** is thinking...🧠"%(i+1,person)):
                    msg = sdk.api_call(api_key, url , model, [{"role": "system", "content": sys_back},
                                                            {"role": "user", "content": prompt}])
                # st.session_state.messages.append({"role": "assistant", "content": msg})
                # st.chat_message("assistant").write(msg)
                st.session_state[person].append(msg)
                st.session_state["paper_" + history_order[num_order]].append("%s:\n\n%s\n\n"%(person,msg))
                num_order += 1
    
    # 对形成的结果进行解析
    st.chat_message("assistant").write("Present the results of the discussion from the perspective of each participant.")
    for person in selected:
        with st.chat_message("assistant"):
            st.write("**%s**\'s statements"%person)
            st.divider()
            for item in st.session_state[person]:
                st.write('- ' + item)
    
    st.session_state["all_text"] = ""

    st.chat_message("assistant").write("Show what's on each note")
    for person in selected:
        with st.chat_message("assistant"):
            st.write("The contents on the note of **%s**:"%person)
            st.divider()
            for item in st.session_state["paper_" + person]:
                st.write('- ' + item)
                st.session_state["all_text"] += "- " + item

    # 一级主题总结
    with st.spinner("Generating a summary..."):

        def have_content(text):
            return bool(re.search(r'[a-zA-Z\u4e00-\u9fff]', text))

        prompt_summary = """
        %s
        围绕**%s**
        从以上内容中总结几个主题，包含三级标题
        格式如下：
        - （一级）
            - （二级）
                - （三级）
        每个主题以 - 开头，一级主题不少于3个，每个一级主题下的二级主题不小于3个，每个二级主题下的三级主题不小于2个
        """ % (st.session_state["all_text"], topic1)

        msg = sdk.api_call(api_key, url, model, [{"role": "user", "content": prompt_summary}])
        
        # 处理返回的主题
        st.session_state["summary"] = msg.replace("#", "").strip()

    st.info("If you want further discussion on the topic, press refresh and choose a subtitle. You may modify the topic. Otherwise press ‘new’ and input new brainstorm topic. Then press 'continue'. ")
    st.chat_message("assistant").write(st.session_state["summary"])



# # 定义下载 JSON 的方法
# def download_mindmap(data, filename="mindmap.json"):
#     mindmap_json = json.dumps(data, ensure_ascii=False, indent=4)
#     st.download_button(
#         label="Download Mindmap as JSON",
#         data=mindmap_json,
#         file_name=filename,
#         mime="application/json",
#     )

# 初始化思维导图
if "mindmap" not in st.session_state:
    st.session_state["mindmap"] = {
        "root": {
            "title": "Root Topic",
            "children": []
        }
    }

# 如果用户没有按下“new”，将新增的多级标题作为思维导图的一部分

# 更新思维导图
def parse_summary_to_mindmap(summary, parent_node):
    lines = summary.strip().splitlines()
    current_level = [parent_node]

    for line in lines:
        level = len(line) - len(line.lstrip())  # 计算缩进层级
        title = line.strip("- ").strip()

        # 创建新节点
        new_node = {"title": title, "children": []}
        
        # 根据层级插入对应位置
        if level < len(current_level):
            current_level = current_level[:level]
        if current_level != []:
            current_level[-1]["children"].append(new_node)
            current_level.append(new_node)


parse_summary_to_mindmap(st.session_state["summary"], st.session_state["mindmap"]["root"])
