"""doc-structure-router 测试界面"""
import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from doc_router import DocumentRouter
from doc_router.config import ConfigManager, Config

# 页面配置
st.set_page_config(
    page_title="Doc Structure Router",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化配置管理器
@st.cache_resource
def get_config_manager():
    return ConfigManager()

config_manager = get_config_manager()

# 侧边栏导航
st.sidebar.title("📄 Doc Structure Router")
st.sidebar.markdown("---")

# 页面选择
page = st.sidebar.radio(
    "导航",
    ["🏠 首页", "📤 文档上传", "🔍 结构分析", "🗄️ 向量库测试", "⚙️ 配置管理"],
    index=0,
)

# 显示配置信息
st.sidebar.markdown("---")
st.sidebar.subheader("当前配置")
config = config_manager.load()
st.sidebar.info(f"""
- **LLM**: {config.llm.provider} / {config.llm.model}
- **OCR**: {config.ocr.engine}
- **向量库**: {config.vector_db.type}
""")


def render_home():
    """渲染首页"""
    st.title("📄 Doc Structure Router")
    st.markdown("---")
    
    st.markdown("""
    ## 文档结构智能路由
    
    自动检测文档结构，选择最佳切分策略，为向量数据库提供高质量的文本分块。
    
    ### 功能特点
    
    | 功能 | 说明 |
    |------|------|
    | 📤 文档上传 | 支持PDF、TXT、Markdown等格式 |
    | 🔍 结构分析 | 自动识别文档结构类型 |
    | ✂️ 智能分块 | 根据结构选择最佳分块策略 |
    | 🗄️ 向量库存储 | 支持ChromaDB等向量数据库 |
    | ⚙️ 配置管理 | 灵活配置LLM、OCR等参数 |
    
    ### 支持的文档结构
    
    - 📚 **目录型 (toc)** - 有目录/书签的文档
    - 📖 **章节型 (chapter)** - 有章节编号的文档
    - 📝 **词汇表型 (glossary)** - 术语+解释格式
    - ❓ **问答型 (qa)** - 问题+答案格式
    - 📋 **参考文档 (reference)** - API文档、规范
    - 📄 **平面文档 (plain)** - 无明显结构
    """)
    
    # 快速开始
    st.markdown("---")
    st.markdown("### 快速开始")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 上传文档", use_container_width=True):
            st.session_state.page = "📤 文档上传"
            st.rerun()
    
    with col2:
        if st.button("🔍 结构分析", use_container_width=True):
            st.session_state.page = "🔍 结构分析"
            st.rerun()
    
    with col3:
        if st.button("⚙️ 配置管理", use_container_width=True):
            st.session_state.page = "⚙️ 配置管理"
            st.rerun()


def render_upload():
    """渲染文档上传页"""
    st.title("📤 文档上传")
    st.markdown("---")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文档文件",
        type=["pdf", "txt", "md", "docx"],
        help="支持PDF、TXT、Markdown、Word格式",
    )
    
    if uploaded_file:
        st.success(f"已上传: {uploaded_file.name}")
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        try:
            # OCR设置
            st.subheader("OCR设置")
            col1, col2 = st.columns(2)
            
            with col1:
                ocr_engine = st.selectbox(
                    "OCR引擎",
                    ["paddle", "tesseract"],
                    index=0,
                    help="选择OCR引擎",
                )
            
            with col2:
                ocr_lang = st.text_input(
                    "OCR语言",
                    value="ch",
                    help="OCR识别语言",
                )
            
            # 处理文档
            if st.button("🚀 开始处理", use_container_width=True):
                with st.spinner("正在处理文档..."):
                    try:
                        router = DocumentRouter(
                            ocr_engine=ocr_engine,
                            ocr_lang=ocr_lang,
                        )
                        chunks = router.process_file(tmp_path)
                        
                        st.success(f"处理完成! 共 {len(chunks)} 个分块")
                        
                        # 显示结果
                        st.subheader("处理结果")
                        
                        # 统计信息
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("分块数量", len(chunks))
                        with col2:
                            template_types = set(c.template_type for c in chunks)
                            st.metric("结构类型", len(template_types))
                        with col3:
                            avg_len = sum(len(c.text) for c in chunks) / len(chunks) if chunks else 0
                            st.metric("平均长度", f"{avg_len:.0f}字")
                        
                        # 显示分块详情
                        st.subheader("分块详情")
                        for i, chunk in enumerate(chunks[:10]):  # 只显示前10个
                            with st.expander(f"Chunk {i+1}: {chunk.template_type}"):
                                st.text_area(
                                    "文本内容",
                                    chunk.text,
                                    height=150,
                                    key=f"chunk_{i}",
                                    disabled=True,
                                )
                                st.json(chunk.metadata)
                        
                        if len(chunks) > 10:
                            st.info(f"还有 {len(chunks) - 10} 个分块未显示...")
                    
                    except Exception as e:
                        st.error(f"处理失败: {e}")
        
        finally:
            # 清理临时文件
            os.unlink(tmp_path)


def render_analysis():
    """渲染结构分析页"""
    st.title("🔍 结构分析")
    st.markdown("---")
    
    # 分析模式
    analysis_mode = st.radio(
        "分析模式",
        ["📋 样本分析 (前50页)", "📊 完整分析"],
        horizontal=True,
    )
    
    sample_pages = 50 if "样本" in analysis_mode else None
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文档文件",
        type=["pdf", "txt", "md"],
        key="analysis_upload",
    )
    
    if uploaded_file:
        st.success(f"已上传: {uploaded_file.name}")
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        try:
            if st.button("🔍 开始分析", use_container_width=True):
                with st.spinner("正在分析文档结构..."):
                    try:
                        router = DocumentRouter()
                        
                        # 获取结构信息
                        info = router.get_info(tmp_path)
                        
                        st.success("分析完成!")
                        
                        # 显示分析结果
                        st.subheader("分析结果")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 基本信息")
                            st.json({
                                "文件名": uploaded_file.name,
                                "文件大小": f"{uploaded_file.size / 1024:.1f} KB",
                                "分析模式": analysis_mode,
                            })
                        
                        with col2:
                            st.markdown("#### 结构识别")
                            st.json(info)
                        
                        # 完整分析结果
                        if "完整" in analysis_mode:
                            st.subheader("完整分析结果")
                            
                            # 获取分块
                            chunks = router.process_file(tmp_path)
                            
                            st.json({
                                "总分块数": len(chunks),
                                "结构类型": list(set(c.template_type for c in chunks)),
                                "元数据": chunks[0].metadata if chunks else {},
                            })
                    
                    except Exception as e:
                        st.error(f"分析失败: {e}")
        
        finally:
            # 清理临时文件
            os.unlink(tmp_path)


def render_vectorstore():
    """渲染向量库测试页"""
    st.title("🗄️ 向量库测试")
    st.markdown("---")
    
    # 向量库配置
    st.subheader("向量库配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        db_type = st.selectbox(
            "向量库类型",
            ["chromadb"],
            index=0,
        )
    
    with col2:
        collection_name = st.text_input(
            "集合名称",
            value="documents",
        )
    
    # 初始化向量库
    try:
        from doc_router.vectorstore import create_vectorstore
        
        vectorstore = create_vectorstore(
            vector_db_type=db_type,
            collection=collection_name,
        )
        
        st.success(f"向量库连接成功: {db_type}")
        
        # 集合信息
        st.subheader("集合信息")
        info = vectorstore.get_collection_info()
        st.json(info)
        
        # 测试添加文档
        st.subheader("添加测试文档")
        
        test_text = st.text_area(
            "输入测试文本",
            value="这是一个测试文档，用于验证向量库功能。",
            height=100,
        )
        
        if st.button("➕ 添加文档"):
            with st.spinner("正在添加文档..."):
                try:
                    ids = vectorstore.add_documents(
                        texts=[test_text],
                        metadatas=[{"source": "test", "type": "manual"}],
                    )
                    st.success(f"添加成功! ID: {ids[0]}")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加失败: {e}")
        
        # 测试搜索
        st.subheader("搜索测试")
        
        search_query = st.text_input(
            "搜索查询",
            value="测试",
        )
        
        if st.button("🔍 搜索"):
            with st.spinner("正在搜索..."):
                try:
                    results = vectorstore.search(query=search_query, k=5)
                    
                    if results:
                        st.success(f"找到 {len(results)} 个结果")
                        
                        for i, result in enumerate(results):
                            with st.expander(f"结果 {i+1} (相关度: {result.score:.3f})"):
                                st.text(result.text)
                                st.json(result.metadata)
                    else:
                        st.warning("未找到结果")
                
                except Exception as e:
                    st.error(f"搜索失败: {e}")
        
        # 文档列表
        st.subheader("文档列表")
        
        documents = vectorstore.get()
        
        if documents:
            st.info(f"共 {len(documents)} 个文档")
            
            for doc in documents[:10]:
                with st.expander(f"文档: {doc['id']}"):
                    st.text(doc["text"][:200])
                    st.json(doc["metadata"])
        else:
            st.warning("暂无文档")
        
        # 操作按钮
        st.subheader("操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 刷新", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🗑️ 清空集合", use_container_width=True):
                if st.button("确认清空", type="primary"):
                    vectorstore.reset()
                    st.success("已清空")
                    st.rerun()
    
    except Exception as e:
        st.error(f"向量库连接失败: {e}")


def render_config():
    """渲染配置管理页"""
    st.title("⚙️ 配置管理")
    st.markdown("---")
    
    config = config_manager.load()
    
    # LLM配置
    st.subheader("🤖 LLM配置")
    
    with st.expander("LLM设置", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            llm_provider = st.selectbox(
                "提供商",
                ["ollama", "openai", "dashscope", "zhipu", "moonshot", "deepseek"],
                index=["ollama", "openai", "dashscope", "zhipu", "moonshot", "deepseek"].index(config.llm.provider),
            )
        
        with col2:
            llm_model = st.text_input(
                "模型名称",
                value=config.llm.model,
            )
        
        llm_api_key = st.text_input(
            "API密钥",
            value=config.llm.api_key,
            type="password",
            help="Ollama本地部署不需要API密钥",
        )
        
        llm_base_url = st.text_input(
            "API地址",
            value=config.llm.base_url,
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            llm_temperature = st.slider(
                "温度",
                min_value=0.0,
                max_value=2.0,
                value=config.llm.temperature,
                step=0.1,
            )
        
        with col2:
            llm_max_tokens = st.number_input(
                "最大Token数",
                min_value=256,
                max_value=32768,
                value=config.llm.max_tokens,
                step=256,
            )
    
    # OCR配置
    st.subheader("👁️ OCR配置")
    
    with st.expander("OCR设置", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            ocr_engine = st.selectbox(
                "OCR引擎",
                ["paddle", "tesseract"],
                index=["paddle", "tesseract"].index(config.ocr.engine),
            )
        
        with col2:
            ocr_lang = st.text_input(
                "OCR语言",
                value=config.ocr.lang,
            )
        
        ocr_dpi = st.number_input(
            "DPI",
            min_value=72,
            max_value=300,
            value=config.ocr.dpi,
            step=1,
        )
    
    # 向量库配置
    st.subheader("🗄️ 向量库配置")
    
    with st.expander("向量库设置", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            vdb_type = st.selectbox(
                "向量库类型",
                ["chromadb"],
                index=0,
            )
        
        with col2:
            vdb_collection = st.text_input(
                "集合名称",
                value=config.vector_db.collection,
            )
        
        vdb_path = st.text_input(
            "存储路径",
            value=config.vector_db.path,
        )
    
    # 分析配置
    st.subheader("📊 分析配置")
    
    with st.expander("分析设置", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sample_pages = st.number_input(
                "样本分析页数",
                min_value=1,
                max_value=100,
                value=config.analysis.sample_pages,
            )
        
        with col2:
            chunk_size = st.number_input(
                "分块大小",
                min_value=100,
                max_value=5000,
                value=config.analysis.chunk_size,
            )
        
        with col3:
            chunk_overlap = st.number_input(
                "分块重叠",
                min_value=0,
                max_value=500,
                value=config.analysis.chunk_overlap,
            )
    
    # 保存配置
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 保存到用户配置", use_container_width=True):
            # 创建新配置
            new_config = Config()
            new_config.llm.provider = llm_provider
            new_config.llm.model = llm_model
            new_config.llm.api_key = llm_api_key
            new_config.llm.base_url = llm_base_url
            new_config.llm.temperature = llm_temperature
            new_config.llm.max_tokens = llm_max_tokens
            new_config.ocr.engine = ocr_engine
            new_config.ocr.lang = ocr_lang
            new_config.ocr.dpi = ocr_dpi
            new_config.vector_db.type = vdb_type
            new_config.vector_db.collection = vdb_collection
            new_config.vector_db.path = vdb_path
            new_config.analysis.sample_pages = sample_pages
            new_config.analysis.chunk_size = chunk_size
            new_config.analysis.chunk_overlap = chunk_overlap
            
            if config_manager.save(new_config, target="user"):
                st.success("配置已保存!")
                st.rerun()
            else:
                st.error("保存失败!")
    
    with col2:
        if st.button("💾 保存到项目配置", use_container_width=True):
            new_config = Config()
            new_config.llm.provider = llm_provider
            new_config.llm.model = llm_model
            new_config.llm.api_key = llm_api_key
            new_config.llm.base_url = llm_base_url
            new_config.llm.temperature = llm_temperature
            new_config.llm.max_tokens = llm_max_tokens
            new_config.ocr.engine = ocr_engine
            new_config.ocr.lang = ocr_lang
            new_config.ocr.dpi = ocr_dpi
            new_config.vector_db.type = vdb_type
            new_config.vector_db.collection = vdb_collection
            new_config.vector_db.path = vdb_path
            new_config.analysis.sample_pages = sample_pages
            new_config.analysis.chunk_size = chunk_size
            new_config.analysis.chunk_overlap = chunk_overlap
            
            if config_manager.save(new_config, target="local"):
                st.success("配置已保存!")
                st.rerun()
            else:
                st.error("保存失败!")
    
    with col3:
        if st.button("🔄 重置为默认", use_container_width=True):
            if config_manager.reset(target="user"):
                st.success("配置已重置!")
                st.rerun()
            else:
                st.error("重置失败!")
    
    # 配置信息
    st.subheader("ℹ️ 配置信息")
    
    info = config_manager.get_config_info()
    st.json(info)


# 路由
if page == "🏠 首页":
    render_home()
elif page == "📤 文档上传":
    render_upload()
elif page == "🔍 结构分析":
    render_analysis()
elif page == "🗄️ 向量库测试":
    render_vectorstore()
elif page == "⚙️ 配置管理":
    render_config()
