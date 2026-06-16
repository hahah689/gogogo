# humanloop_manager.py
import os
from gohumanloop  import DefaultHumanLoopManager , APIProvider
#from gohumanloop import   APIProvider
from gohumanloop.adapters.langgraph_adapter import HumanloopAdapter
from gohumanloop.providers.terminal_provider import TerminalProvider 
from gohumanloop.utils import get_secret_from_env
# 璁剧疆鐜鍙橀噺
os.environ["GOHUMANLOOP_API_KEY"] = "577992f3-3092-4ba1-95e9-5d8a6c540687"

# Initialize HumanLoopManager and HumanloopAdapter for GoHumanLoop
# This is done in a separate file to avoid circular imports
# humanloop_manager = DefaultHumanLoopManager(
#     initial_providers=TerminalProvider(name="TerminalProvider")
# )
# humanloop_adapter = HumanloopAdapter(humanloop_manager, default_timeout=60)

# 鍒涘缓 GoHumanLoopManager 瀹炰緥
humanloop_manager = DefaultHumanLoopManager(
    APIProvider(
        name="ApiProvider",
        api_base_url="http://127.0.0.1:9800/api", # 鎹㈡垚鑷繁椋炰功搴旂敤鐨刄RL
        api_key=get_secret_from_env("GOHUMANLOOP_API_KEY"),  # get_secret_from_env("GOHUMANLOOP_API_KEY"),
        default_platform="feishu"
    )
)
# 鍒涘缓 LangGraphAdapter 瀹炰緥
humanloop_adapter = HumanloopAdapter(
    manager=humanloop_manager,
    default_timeout=300,  # 榛樿瓒呮椂鏃堕棿涓?鍒嗛挓
)
