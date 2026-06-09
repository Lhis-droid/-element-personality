import streamlit as st
import requests
import json

# 设置页面配置
st.set_page_config(
    page_title="AI ChatBot",
    page_icon="🤖",
    layout="wide"
)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'base_url' not in st.session_state:
    st.session_state.base_url = "https://api.deepseek.com/v1"
if 'model' not in st.session_state:
    st.session_state.model = "deepseek-chat"

# 侧边栏配置
with st.sidebar:
    st.header("🔧 API 配置")
    
    api_key = st.text_input(
        "API Key", 
        value=st.session_state.api_key, 
        type="password", 
        help="大模型 API 的密钥"
    )
    
    base_url = st.text_input(
        "Base URL", 
        value=st.session_state.base_url, 
        help="API 的基础地址"
    )
    
    model = st.text_input(
        "Model", 
        value=st.session_state.model, 
        help="使用的模型名称"
    )
    
    temperature = st.slider(
        "Temperature", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.1, 
        help="输出随机性"
    )
    
    # 保存配置按钮
    if st.button("💾 保存配置"):
        st.session_state.api_key = api_key
        st.session_state.base_url = base_url
        st.session_state.model = model
        st.success("✅ 配置已保存")
    
    # 清空对话按钮
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.success("✅ 对话已清空")
        st.rerun()

# 主页面标题
st.title("🤖 AI ChatBot")
st.subheader("与 AI 助手进行智能对话")

def call_llm(messages):
    """调用大模型 API"""
    if not api_key or not base_url:
        st.error("请先配置 API Key 和 Base URL")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            st.error("API 返回格式异常")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"API 调用失败: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("API 返回不是有效的 JSON")
        return None

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入框
if prompt := st.chat_input("输入你的问题..."):
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 获取 AI 回复
    with st.chat_message("assistant"):
        with st.spinner("AI 正在思考..."):
            response = call_llm(st.session_state.messages)
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# 使用说明
st.divider()
with st.expander("📖 使用说明", expanded=False):
    st.write("""
    **使用步骤：**
    1. 在左侧边栏配置你的大模型 API 参数
    2. 点击「保存配置」按钮
    3. 在下方输入框中输入问题
    4. 等待 AI 回复
    
    **支持的 API 格式：**
    - DeepSeek API: https://api.deepseek.com/v1
    - OpenAI 兼容 API: 设置对应的 Base URL 即可
    
    **注意事项：**
    - 请确保你的 API Key 有足够的余额
    - 对话历史会保存在当前会话中
    - 点击「清空对话」可以重置聊天记录
    """)