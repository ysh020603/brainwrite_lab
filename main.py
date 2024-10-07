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
    api_key = st.text_input("API Key", key="chatbot_api_key", type="password")
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
        st.rerun()
    topic = st.text_area("Input the brainstorm topic")

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
if st.sidebar.button("begin"):
    if not api_key:
        st.info("Please add your API key to continue.")
        st.stop()
    if len(selected) != 4 and len(selected) != 3:
        st.info("Please select who participate (4 or 3 people).")
        st.stop()
    if not topic:
        st.info("Please input the brainstorm topic.")
        st.stop()
    st.session_state["selected"] = []
    for item in selected:
        st.session_state["selected"].append(item)

    
    
    st.session_state.messages.append({"role": "user", "content": topic})
    st.chat_message("user").write(topic)

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
'''%topic
                else:
                    prompt ='''
### Brainstorming on **%s** right now.

### According to your background, stand in the perspective of your field, participate in brainstorming, and give your thoughts. **Please answer in English**.

### The generated content should be brief, Sum your viewpoints up in one paragraph (less than 100 words). Please provide **inspiring viewpoints**. And give your specific opinions or solutions.

### Only generate rigorous statements, do not generate other content. Do not introduce yourself.
'''%topic
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
'''%(history,topic)
                else:
                    prompt ='''
%s

### Brainstorming on **%s** right now. The above are comments by other participants.

### Participate in brainstorming according to your identity background, standing in the perspective of your field.

### Please carefully read the comments by other participants, based on your knowledge background, continue to develop their viewpoints. Put forward specific ideas and methods.

### The generated content should be brief, Sum your viewpoints up in one paragraph (less than 100 words). No need to introduce yourself.

### Only generate rigorous statements, do not generate other content, please answer in English. 
'''%(history,topic)
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

    with st.spinner("Generating a summary..."):
        prompt_summary = """
%s

围绕**%s**
从以上内容中总结几个主题
每个主题以 - 开头，只生成总结的主题，不要生成其他内容，总结的主题数量不超过6个
"""%(st.session_state["all_text"], topic)
        msg = sdk.api_call(api_key, url , model, [{"role": "user", "content": prompt_summary}])
        summary_list = msg.replace("#","").split("- ")[1:]
        print(summary_list)

        st.session_state["summary"] = ""
        for item in summary_list:
            st.session_state["summary"] += "- " + item + "\n\n"
            prompt_sub = """
%s
s
以**%s**为中心
围绕**%s**这个主题
总结上文中相关的观点 
总结出4点即可，以 - 约束格式，不要生成其他内容。
"""%(st.session_state["all_text"], topic, item)
            msg = sdk.api_call(api_key, url , model, [{"role": "user", "content": prompt_sub}])
            st.session_state["summary"] += msg.replace("- ", "    - ").replace("#", "") + "\n\n"
            print(msg)
        st.chat_message("assistant").write(st.session_state["summary"])
        


