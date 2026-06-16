from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from pydantic import BaseModel, Field

from ecommerce_support_agent.app.services.assistants.assistant_base import Assistant, llm

# 电商相关助手
from ecommerce_support_agent.app.services.assistants.woocommerce_assistant import (
    ToWooCommerceProducts,
    ToWooCommerceOrders,
)
from ecommerce_support_agent.app.services.assistants.form_submission_assistant import ToFormSubmission
from ecommerce_support_agent.app.services.assistants.blog_search_assistant import ToBlogSearch


# ===== 以下 4 个类是原航空项目遗留占位类 =====
# 不要放进 primary_assistant_tools，否则模型可能继续调用航空/酒店/租车/旅游逻辑。
# 保留它们只是为了兼容 graph.py 中的旧 import，避免启动报错。

class ToFlightBookingAssistant(BaseModel):
    """已停用：原航空项目遗留类，仅用于兼容旧图结构。"""
    request: str = Field(description="已停用，请不要使用。")


class ToBookCarRental(BaseModel):
    """已停用：原租车项目遗留类，仅用于兼容旧图结构。"""
    location: str = Field(default="已停用", description="已停用，请不要使用。")
    start_date: str = Field(default="已停用", description="已停用，请不要使用。")
    end_date: str = Field(default="已停用", description="已停用，请不要使用。")
    request: str = Field(default="已停用", description="已停用，请不要使用。")


class ToHotelBookingAssistant(BaseModel):
    """已停用：原酒店项目遗留类，仅用于兼容旧图结构。"""
    location: str = Field(default="已停用", description="已停用，请不要使用。")
    checkin_date: str = Field(default="已停用", description="已停用，请不要使用。")
    checkout_date: str = Field(default="已停用", description="已停用，请不要使用。")
    request: str = Field(default="已停用", description="已停用，请不要使用。")


class ToBookExcursion(BaseModel):
    """已停用：原旅游推荐项目遗留类，仅用于兼容旧图结构。"""
    location: str = Field(default="已停用", description="已停用，请不要使用。")
    request: str = Field(default="已停用", description="已停用，请不要使用。")


# ===== 主助手提示词 =====

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个跨境电商智能客服处理台的主助手，面向中国跨境电商卖家提供业务处理支持。"
            "你的工作不是普通闲聊，而是帮助卖家分析平台问题、整理材料、生成沟通文本和处理建议。"

            "\n\n核心业务范围："
            "\n1. 商品申诉处理：商品被限制、下架、误判、要求补充资料时，帮助整理申诉理由。"
            "\n2. 儿童产品证书误判分析：成人装饰品、手工材料、小摆件等被平台误判为儿童产品时，帮助分析原因并生成说明。"
            "\n3. 商品页面检查：检查商品标题、五点描述、详情页是否存在容易触发平台误判的表达。"
            "\n4. 客服邮件生成：生成平台沟通邮件、客户售后邮件、请求人工复核邮件。"
            "\n5. 售后回复：处理退款、破损、差评、物流延迟、补发等客户沟通场景。"
            "\n6. 资料整理：根据用户提供的商品信息、平台提示、页面内容，整理成可提交的说明材料。"

            "\n\n回答规则："
            "\n1. 默认使用中文回答。只有用户明确要求英文时，才输出英文。"
            "\n2. 不要再说自己是瑞士航空客服助理。"
            "\n3. 不要提航班、机票、酒店、租车、旅游推荐。"
            "\n4. 不要主动引导用户进行任何旅行、订票、住宿相关操作。"
            "\n5. 页面和回答里尽量使用中文业务词："
            "\n   - 用“平台商品编号”代替 ASIN。"
            "\n   - 用“儿童产品证书误判”代替 CPC 误判。"
            "\n   - 用“商品页面”代替 Listing。"
            "\n6. 如果用户需要申诉信，先用中文分析申诉逻辑，再给英文申诉信。"
            "\n7. 生成申诉信时，语气要专业、克制、清晰，不要夸大，不要编造政策。"
            "\n8. 涉及合规判断时，必须优先依据用户提供的商品用途、目标人群、年龄标识、页面描述和平台提示。"
            "\n9. 如果用户提供的信息不足，先给出可执行的初步建议，并说明还需要补充哪些材料。"

            "\n\n常见输出格式："
            "\n- 问题类型判断"
            "\n- 当前风险点"
            "\n- 建议补充材料"
            "\n- 商品页面修改建议"
            "\n- 可复制的中文说明"
            "\n- 可提交给平台的英文邮件或申诉信"

            "\n\n当前用户背景信息："
            "\n<UserInfo>\n{user_info}\n</UserInfo>"

            "\n\n当前时间：{time}。"
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())


# ===== 主助手可用工具 =====
# 这里不要再放 search_flights、航空助手、酒店助手、租车助手、旅游助手。

primary_assistant_tools = [
    DuckDuckGoSearchResults(max_results=5),
    ToWooCommerceProducts,
    ToWooCommerceOrders,
    ToFormSubmission,
    ToBlogSearch,
]


primary_assistant_runnable = primary_assistant_prompt | llm.bind_tools(primary_assistant_tools)

primary_assistant = Assistant(primary_assistant_runnable)
