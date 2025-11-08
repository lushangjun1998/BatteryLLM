import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, AsyncGenerator  # 新增：异步生成器类型
from build_rag import get_embedding_model, load_documents_from_folder, build_qa_chain, build_or_load_vectordb
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import markdown
from concurrent.futures import ThreadPoolExecutor
from starlette.responses import StreamingResponse, JSONResponse
import re, logging, json
from datetime import datetime

app = FastAPI(
    title="RAG",
    description="电池策略LLM(内测版)",
    version="1.0.0"
)

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Markdown渲染函数
def render_markdown(text: str) -> str:
    extensions = ['extra', 'codehilite']
    return markdown.markdown(text, extensions=extensions)

# 添加 CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应限制为具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET/POST等）
    allow_headers=["*"],  # 允许所有请求头
)

# 定义请求和响应模型
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3


class AnswerResponse(BaseModel):
    question: str
    answer: str
    status: str


class FeedbackRequest(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    feedback: str
    email: str


def init_rag_system():
    docs_path = "txt_file"
    embed_model_path = "model_dir/BAAI/bge-large-zh-v1___5"
    chromadb_dir = "chroma_db"

    embedding_model = get_embedding_model(embed_model_path)
    if not os.path.exists(chromadb_dir):
        documents = load_documents_from_folder(docs_path)
    else:
        documents = None
    vectordb = build_or_load_vectordb(documents, chromadb_dir, embedding_model)

    qa_chain = build_qa_chain(vectordb, stream=False)
    return qa_chain


# 全局QA链
qa_chain = init_rag_system()
# 全局线程池
executor = ThreadPoolExecutor(max_workers=36)

# 保存反馈到日志文件
def save_feedback_to_log(feedback_data):
    log_file = "feedback.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_data["timestamp"] = timestamp

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_data, ensure_ascii=False) + "\n")

# 前端页面路由
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: qa_chain.invoke(request.question)['result']
        )
        # 清理think标签并转换为HTML
        cleaned_result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
        html_content = markdown.markdown(cleaned_result)
        return {
            "question": request.question,
            "answer": html_content,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理问题时出错: {str(e)}"
        )


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        feedback_data = {
            "question": request.question,
            "answer": request.answer,
            "feedback": request.feedback,
            "email": request.email
        }
        save_feedback_to_log(feedback_data)
        return {"status": "success", "message": "反馈提交成功"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"提交反馈时出错: {str(e)}"
        )

@app.post("/ask_stream")
async def ask_question(request: QuestionRequest) -> StreamingResponse:
    try:
        question = request.question

        # 1. 检索相关文档（使用线程池避免阻塞）
        docs = await asyncio.get_event_loop().run_in_executor(
            executor,
            lambda: qa_chain["retriever"].get_relevant_documents(question)
        )
        # 2. 构建上下文
        context = "\n\n".join([doc.page_content for doc in docs])

        # 3. 渲染提示词
        prompt = qa_chain["prompt"].format(context=context, question=question)

        # 4. 流式生成回答（定义异步生成器）
        async def generate_answer() -> AsyncGenerator[str, None]:
            # 调用LLM的流式接口（同步方法用线程池包装）
            stream_contxt = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: qa_chain["llm"].stream([{"role": "user", "content": prompt}])
            )

            # 逐段返回回答内容（SSE格式）
            for chunk in stream_contxt:
                content = chunk.content  # 获取当前片段内容
                if content:
                    # 转换为Markdown并以SSE格式返回
                    print(f"data: {content}")  # 检查是否有**等特殊字符
                    yield f"data: {json.dumps(content)}\n\n"
            # for chunk in stream_contxt:
            #     content = chunk.content
            #     if content:
            #         print(f"data: {content}")
            # 发送结束信号
            yield "data: [DONE]\n\n"
        # 返回流式响应
        return StreamingResponse(generate_answer(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理问题时出错: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


