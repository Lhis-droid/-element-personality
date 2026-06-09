import streamlit as st
import requests
import json

# 设置页面标题
st.set_page_config(page_title="Fortune Translator", page_icon="🔮")

# 初始化会话状态
if 'current_fortune' not in st.session_state:
    st.session_state.current_fortune = None
if 'cleaned_fortune' not in st.session_state:
    st.session_state.cleaned_fortune = None
if 'translations' not in st.session_state:
    st.session_state.translations = None
if 'element_result' not in st.session_state:
    st.session_state.element_result = None
if 'element_score' not in st.session_state:
    st.session_state.element_score = None

# 元素人格定义
ELEMENTS = {
    "fire": {
        "name": "火元素",
        "icon": "🔥",
        "color": "#FF6B35",
        "traits": ["热情洋溢", "勇敢无畏", "富有创造力", "充满活力", "果断自信"],
        "description": "火元素代表激情与行动力。你是天生的领导者，充满热情和创造力，敢于追求梦想。",
        "fortune_style": "激励鼓舞"
    },
    "water": {
        "name": "水元素",
        "icon": "💧",
        "color": "#4ECDC4",
        "traits": ["情感丰富", "直觉敏锐", "善解人意", "适应性强", "富有同理心"],
        "description": "水元素代表情感与直觉。你内心丰富细腻，善于理解他人，能够适应各种环境。",
        "fortune_style": "温柔抚慰"
    },
    "earth": {
        "name": "土元素",
        "icon": "🌍",
        "color": "#8B7355",
        "traits": ["稳重可靠", "务实踏实", "耐心细致", "勤奋努力", "注重实际"],
        "description": "土元素代表稳定与务实。你脚踏实地，值得信赖，是可靠的朋友和伙伴。",
        "fortune_style": "沉稳建议"
    },
    "air": {
        "name": "风元素",
        "icon": "💨",
        "color": "#A8D8EA",
        "traits": ["思维敏捷", "好奇心强", "善于沟通", "灵活多变", "理性客观"],
        "description": "风元素代表思想与交流。你聪明好奇，善于思考，能够从不同角度看待问题。",
        "fortune_style": "智慧启发"
    }
}

# 元素测试问题
ELEMENT_QUESTIONS = [
    {
        "question": "遇到困难时，你更倾向于？",
        "options": [
            {"text": "直接面对，主动解决", "element": "fire"},
            {"text": "冷静分析，寻找最佳方案", "element": "air"},
            {"text": "寻求他人帮助和支持", "element": "water"},
            {"text": "耐心等待，静观其变", "element": "earth"}
        ]
    },
    {
        "question": "朋友评价你最常说的是？",
        "options": [
            {"text": "热情开朗，充满活力", "element": "fire"},
            {"text": "善解人意，温暖贴心", "element": "water"},
            {"text": "稳重可靠，值得信赖", "element": "earth"},
            {"text": "聪明机智，想法独特", "element": "air"}
        ]
    },
    {
        "question": "你更喜欢哪种休闲方式？",
        "options": [
            {"text": "参加热闹的聚会", "element": "fire"},
            {"text": "安静地看书或冥想", "element": "water"},
            {"text": "动手做手工或园艺", "element": "earth"},
            {"text": "探索新知识或旅行", "element": "air"}
        ]
    },
    {
        "question": "做决策时，你更依赖？",
        "options": [
            {"text": "直觉和感觉", "element": "water"},
            {"text": "逻辑和分析", "element": "air"},
            {"text": "经验和事实", "element": "earth"},
            {"text": "勇气和信念", "element": "fire"}
        ]
    },
    {
        "question": "团队合作中，你通常是？",
        "options": [
            {"text": "提出创意和方向", "element": "fire"},
            {"text": "协调人际关系", "element": "water"},
            {"text": "负责执行和落实", "element": "earth"},
            {"text": "分析问题和方案", "element": "air"}
        ]
    }
]

# 配置区域
with st.sidebar:
    st.header("🔧 API 配置")
    api_key = st.text_input("API Key", value="", type="password", help="大模型 API 的密钥")
    base_url = st.text_input("Base URL", value="https://api.deepseek.com/v1", help="API 的基础地址")
    model = st.text_input("Model", value="deepseek-chat", help="使用的模型名称")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, help="输出随机性")

# 主页面标题
st.title("🔮 Fortune Translator")
st.subheader("获取一句英文箴言，翻译成中文并给出三种解读")

# 在线获取 fortune 的函数
def get_fortune():
    """从在线 API 获取 fortune"""
    try:
        # 使用 http://yerkee.com/api/fortune 这个公开的 fortune API
        response = requests.get("http://yerkee.com/api/fortune", timeout=10)
        response.raise_for_status()
        data = response.json()
        if "fortune" in data:
            return data["fortune"]
        else:
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败: {str(e)}")
        return None

# 清洗文本的函数
def clean_fortune(text):
    """清洗文本：去掉空行、多余符号"""
    if not text:
        return ""
    
    # 按行分割
    lines = text.split('\n')
    # 过滤空行和纯空白行
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    # 合并成一行
    result = ' '.join(cleaned_lines)
    # 移除多余的空格
    result = ' '.join(result.split())
    return result

# 调用大模型翻译的函数
def call_llm(prompt):
    """调用大模型 API"""
    if not api_key or not base_url:
        st.error("请先在侧边栏配置 API Key 和 Base URL")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
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

# 翻译并生成三种解释
def translate_fortune(cleaned_text):
    """翻译 fortune 并生成三种语气的解释"""
    if not cleaned_text:
        return None
    
    prompt = f"""
    请处理下面这句英文箴言：
    {cleaned_text}
    
    请按以下格式输出：
    【中文翻译】：将这句英文翻译成自然流畅的中文
    【老师式解释】：用老师教导学生的语气解释这句话的含义和道理
    【朋友式解释】：用朋友聊天的轻松语气解释这句话
    【吐槽式解释】：用幽默、调侃的语气吐槽这句话
    
    请直接输出结果，不需要额外说明。
    """
    
    result = call_llm(prompt)
    if result:
        return parse_response(result)
    return None

def parse_response(response):
    """解析大模型的响应"""
    translations = {
        "translation": "",
        "teacher": "",
        "friend": "",
        "吐槽": ""
    }
    
    lines = response.split('\n')
    for line in lines:
        if "【中文翻译】" in line:
            translations["translation"] = line.replace("【中文翻译】", "").replace("：", "").strip()
        elif "【老师式解释】" in line:
            translations["teacher"] = line.replace("【老师式解释】", "").replace("：", "").strip()
        elif "【朋友式解释】" in line:
            translations["friend"] = line.replace("【朋友式解释】", "").replace("：", "").strip()
        elif "【吐槽式解释】" in line:
            translations["吐槽"] = line.replace("【吐槽式解释】", "").replace("：", "").strip()
    
    return translations

# 元素测试函数
def calculate_element(answers):
    """根据回答计算元素得分"""
    scores = {"fire": 0, "water": 0, "earth": 0, "air": 0}
    for answer in answers:
        if answer:
            scores[answer] += 1
    
    max_score = max(scores.values())
    if max_score == 0:
        return None, scores
    
    result = [k for k, v in scores.items() if v == max_score][0]
    return result, scores

def get_element_interpretation(cleaned_text, element_key):
    """根据元素人格生成对应风格的解读"""
    if not cleaned_text or not element_key:
        return None
    
    element = ELEMENTS[element_key]
    style = element["fortune_style"]
    
    prompt = f"""
    请处理下面这句英文箴言：
    {cleaned_text}
    
    我是{element['name']}人格，特点是：{', '.join(element['traits'])}
    
    请用符合{element['name']}特点的方式解释这句话，风格是{style}。
    
    输出格式：
    【元素解读】：用符合{element['name']}人格的语气解释这句箴言的含义
    """
    
    result = call_llm(prompt)
    if result:
        lines = result.split('\n')
        for line in lines:
            if "【元素解读】" in line:
                return line.replace("【元素解读】", "").replace("：", "").strip()
    return None

# 主页面布局
tab1, tab2 = st.tabs(["🌟 Fortune 解读", "🔮 元素人格测试"])

with tab1:
    # 获取 fortune 按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 获取 Fortune", disabled=st.session_state.current_fortune is not None):
            with st.spinner("正在获取 fortune..."):
                raw_fortune = get_fortune()
                if raw_fortune:
                    st.session_state.current_fortune = raw_fortune
                    st.session_state.cleaned_fortune = clean_fortune(raw_fortune)
                    
                    # 翻译
                    with st.spinner("正在翻译..."):
                        st.session_state.translations = translate_fortune(st.session_state.cleaned_fortune)
                       
                        # 如果有元素人格结果，生成元素解读
                        if st.session_state.element_result:
                            with st.spinner("正在生成元素解读..."):
                                st.session_state.element_interpretation = get_element_interpretation(
                                    st.session_state.cleaned_fortune, 
                                    st.session_state.element_result
                                )

    with col2:
        if st.button("🔄 换一句", disabled=st.session_state.current_fortune is None):
            # 清除状态，触发重新获取
            st.session_state.current_fortune = None
            st.session_state.cleaned_fortune = None
            st.session_state.translations = None
            st.session_state.element_interpretation = None
            # 自动刷新页面
            st.rerun()

    # 显示结果
    if st.session_state.current_fortune:
        st.divider()
        
        # 原始英文
        with st.expander("📝 原始英文", expanded=True):
            st.text(st.session_state.current_fortune)
        
        # 清洗后的英文
        with st.expander("✨ 清洗后的英文", expanded=True):
            st.write(f"**{st.session_state.cleaned_fortune}**")
        
        # 翻译结果
        if st.session_state.translations:
            translations = st.session_state.translations
            
            with st.expander("🌍 中文翻译", expanded=True):
                st.success(translations["translation"])
            
            with st.expander("👨‍🏫 老师式解释", expanded=True):
                st.info(f"老师说：{translations['teacher']}")
            
            with st.expander("👯 朋友式解释", expanded=True):
                st.warning(f"朋友说：{translations['friend']}")
            
            with st.expander("😂 吐槽式解释", expanded=True):
                st.error(f"吐槽说：{translations['吐槽']}")
        
        # 元素解读
        if st.session_state.element_result and st.session_state.element_interpretation:
            element = ELEMENTS[st.session_state.element_result]
            with st.expander(f"{element['icon']} {element['name']}解读", expanded=True):
                st.markdown(f"<p style='color:{element['color']};font-size:16px;'>{element['icon']} {element['name']}说：{st.session_state.element_interpretation}</p>", unsafe_allow_html=True)

with tab2:
    st.title("🔮 四元素人格测试")
    st.subheader("发现你的元素属性")
    
    # 显示元素卡片
    st.markdown("### 四元素介绍")
    cols = st.columns(4)
    for i, (key, element) in enumerate(ELEMENTS.items()):
        with cols[i]:
            st.markdown(f"""
            <div style='background-color:{element['color']}20;border-radius:12px;padding:16px;text-align:center;'>
                <span style='font-size:32px;'>{element['icon']}</span>
                <h3 style='color:{element['color']};'>{element['name']}</h3>
                <p style='font-size:12px;color:#666;'>{element['description'][:30]}...</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # 测试问题
    st.markdown("### 开始测试")
    answers = []
    
    for i, q in enumerate(ELEMENT_QUESTIONS):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        options = [opt["text"] for opt in q["options"]]
        selected = st.radio(f"问题 {i+1}", options, key=f"q_{i}", index=None, horizontal=True)
        
        if selected:
            for opt in q["options"]:
                if opt["text"] == selected:
                    answers.append(opt["element"])
                    break
        else:
            answers.append(None)
    
    # 提交按钮
    if st.button("🧪 查看结果"):
        if None in answers:
            st.warning("请回答所有问题！")
        else:
            result, scores = calculate_element(answers)
            st.session_state.element_result = result
            st.session_state.element_score = scores
            
            # 显示结果
            st.divider()
            element = ELEMENTS[result]
            st.markdown(f"""
            <div style='background-color:{element['color']}20;border-radius:16px;padding:24px;text-align:center;'>
                <span style='font-size:64px;'>{element['icon']}</span>
                <h2 style='color:{element['color']};margin-top:16px;'>你是{element['name']}人格！</h2>
                <p style='font-size:16px;color:#333;margin-top:16px;'>{element['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 你的特质")
            cols = st.columns(5)
            for j, trait in enumerate(element["traits"]):
                with cols[j]:
                    st.markdown(f"<div style='background-color:{element['color']}20;border-radius:8px;padding:8px;text-align:center;color:{element['color']};'>{trait}</div>", unsafe_allow_html=True)
            
            st.markdown("### 得分详情")
            for key, score in scores.items():
                elem = ELEMENTS[key]
                progress = (score / len(ELEMENT_QUESTIONS)) * 100
                st.markdown(f"{elem['icon']} {elem['name']}:")
                st.progress(progress/100)
                st.markdown(f"<span style='color:{elem['color']};'>{score}/{len(ELEMENT_QUESTIONS)}</span>", unsafe_allow_html=True)
    
    # 使用说明
st.divider()
with st.expander("📖 使用说明", expanded=False):
    st.write("""
    **Fortune 解读：**
    1. 在左侧边栏配置你的大模型 API 参数
    2. 点击「获取 Fortune」按钮获取一句英文箴言
    3. 系统会自动翻译并生成四种语气的解释（老师式、朋友式、吐槽式、元素人格）
    
    **元素人格测试：**
    1. 切换到「元素人格测试」标签页
    2. 回答5个问题,了解你的元素属性
    3. 测试完成后,Fortune 解读会根据你的元素人格生成专属解读
    
    **支持的 API 格式**:
    - DeepSeek API: https://api.deepseek.com/v1
    - OpenAI 兼容 API: 设置对应的 Base URL 即可
    """)
