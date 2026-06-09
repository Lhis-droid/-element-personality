import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(
    page_title="数据处理工作台",
    page_icon="📊",
    layout="wide"
)

if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("📊 数据处理工作台")
st.subheader("上传、清洗、分析和导出数据")

with st.sidebar:
    st.header("📁 数据上传")
    uploaded_file = st.file_uploader(
        "选择数据文件",
        type=['csv', 'xlsx', 'xls'],
        help="支持 CSV 和 Excel 格式"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.data = df
            st.success(f"✅ 已加载 {len(df)} 行数据")
        except Exception as e:
            st.error(f"❌ 加载失败: {str(e)}")

tab1, tab2, tab3, tab4 = st.tabs(["📋 数据预览", "🧹 数据清洗", "📈 数据分析", "💾 数据导出"])

with tab1:
    st.header("数据预览")
    if st.session_state.data is not None:
        df = st.session_state.data
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("行数", df.shape[0])
        with col2:
            st.metric("列数", df.shape[1])
        with col3:
            st.metric("缺失值", df.isnull().sum().sum())
        with col4:
            st.metric("重复行", df.duplicated().sum())
        
        st.subheader("前 100 行数据")
        st.dataframe(df.head(100), use_container_width=True)
        
        st.subheader("数据概览")
        st.dataframe(df.describe(), use_container_width=True)
    else:
        st.info("👈 请先在左侧上传数据文件")

with tab2:
    st.header("数据清洗")
    if st.session_state.data is not None:
        df = st.session_state.data.copy()
        
        st.subheader("缺失值处理")
        col1, col2 = st.columns(2)
        with col1:
            missing_strategy = st.selectbox(
                "缺失值处理方式",
                ["不处理", "删除缺失行", "填充平均值", "填充中位数", "填充众数", "填充指定值"]
            )
        with col2:
            if missing_strategy == "填充指定值":
                fill_value = st.text_input("填充值", "0")
        
        st.subheader("重复值处理")
        remove_duplicates = st.checkbox("删除重复行")
        
        st.subheader("数据类型转换")
        cols_to_convert = st.multiselect(
            "选择要转换的列",
            options=df.columns.tolist()
        )
        if cols_to_convert:
            target_type = st.selectbox("目标类型", ["int", "float", "str", "datetime"])
        
        if st.button("🚀 执行清洗"):
            cleaned_df = df.copy()
            
            if missing_strategy == "删除缺失行":
                cleaned_df = cleaned_df.dropna()
            elif missing_strategy == "填充平均值":
                cleaned_df = cleaned_df.fillna(cleaned_df.mean(numeric_only=True))
            elif missing_strategy == "填充中位数":
                cleaned_df = cleaned_df.fillna(cleaned_df.median(numeric_only=True))
            elif missing_strategy == "填充众数":
                cleaned_df = cleaned_df.fillna(cleaned_df.mode().iloc[0])
            elif missing_strategy == "填充指定值":
                cleaned_df = cleaned_df.fillna(fill_value)
            
            if remove_duplicates:
                cleaned_df = cleaned_df.drop_duplicates()
            
            st.session_state.processed_data = cleaned_df
            st.success(f"✅ 清洗完成！当前 {len(cleaned_df)} 行")
            st.dataframe(cleaned_df.head(50), use_container_width=True)
    else:
        st.info("👈 请先在左侧上传数据文件")

with tab3:
    st.header("数据分析")
    if st.session_state.data is not None:
        df = st.session_state.processed_data if st.session_state.processed_data is not None else st.session_state.data
        
        st.subheader("数值列统计")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        
        st.subheader("分类列统计")
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if cat_cols:
            selected_col = st.selectbox("选择分类列", cat_cols)
            if selected_col:
                value_counts = df[selected_col].value_counts().head(20)
                st.bar_chart(value_counts)
        
        st.subheader("相关性分析")
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            st.dataframe(corr.style.background_gradient(cmap='coolwarm'), use_container_width=True)
    else:
        st.info("👈 请先在左侧上传数据文件")

with tab4:
    st.header("数据导出")
    if st.session_state.processed_data is not None:
        df = st.session_state.processed_data
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("导出数据行数", len(df))
        with col2:
            st.metric("导出数据列数", df.shape[1])
        
        export_format = st.radio("导出格式", ["CSV", "Excel"])
        
        if export_format == "CSV":
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下载 CSV 文件",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            excel_data = output.getvalue()
            st.download_button(
                label="📥 下载 Excel 文件",
                data=excel_data,
                file_name="processed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("👈 请先处理数据后再导出")

st.divider()
st.markdown("""
### 📖 使用说明
1. 在左侧上传 CSV 或 Excel 数据文件
2. 在「数据预览」中查看数据基本信息
3. 在「数据清洗」中选择清洗策略
4. 在「数据分析」中查看统计图表
5. 在「数据导出」中下载处理后的数据
""")