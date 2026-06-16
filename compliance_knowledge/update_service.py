"""
FAQ鏇存柊鏈嶅姟妯″潡
"""
import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Dict, List
from .document_parser import parse_document
from .data_source import DataSourceManager
# 瀵煎叆鍚戦噺鏁版嵁搴撴ā鍧?from ecommerce_support_agent.app.services.vectordb.vectordb import VectorDB
from ecommerce_support_agent.app.services.vectordb.chunkenizer import recursive_character_splitting


class FAQUpdateService:
    """FAQ鏇存柊鏈嶅姟"""
    
    def __init__(self, config_path: str = "faq_config.yaml"):
        """
        鍒濆鍖朏AQ鏇存柊鏈嶅姟
        
        Args:
            config_path (str): 閰嶇疆鏂囦欢璺緞
        """
        self.scheduler = BackgroundScheduler()
        self.data_source_manager = DataSourceManager(config_path)
        self.last_run_time = {}
        # 鍒濆鍖栧悜閲忔暟鎹簱
        self.faq_vectordb = VectorDB(collection_name="faq_collection")
    
    def start(self):
        """鍚姩瀹氭湡鏇存柊鏈嶅姟"""
        # 娉ㄥ唽瀹氭椂浠诲姟
        sources = self.data_source_manager.get_local_sources()
        for source in sources:
            interval = source.get("update_interval_hours", 24)
            self.scheduler.add_job(
                self._update_source,
                'interval',
                hours=interval,
                args=[source],
                id=f"source_{source['name']}"
            )
            print(f"宸叉敞鍐屾暟鎹簮鏇存柊浠诲姟: {source['name']} (姣弡interval}灏忔椂)")
        
        self.scheduler.start()
        print("FAQ鏇存柊鏈嶅姟宸插惎鍔?)
    
    def stop(self):
        """鍋滄鏇存柊鏈嶅姟"""
        self.scheduler.shutdown()
        print("FAQ鏇存柊鏈嶅姟宸插仠姝?)
    
    def _update_source(self, source_config: Dict):
        """
        鏇存柊鍗曚釜鏁版嵁婧?        
        Args:
            source_config (Dict): 鏁版嵁婧愰厤缃?        """
        try:
            source_name = source_config["name"]
            print(f"寮€濮嬫洿鏂版暟鎹簮: {source_name}")
            
            # 鎵弿鏁版嵁婧愭枃浠?            files = self.data_source_manager.scan_source_files(source_config)
            print(f"鍙戠幇 {len(files)} 涓枃浠?)
            
            # 澶勭悊姣忎釜鏂囦欢
            for file_info in files:
                file_path = file_info["path"]
                modified_time = file_info["modified_time"]
                
                # 妫€鏌ユ枃浠舵槸鍚﹂渶瑕佹洿鏂帮紙閫氳繃淇敼鏃堕棿鍒ゆ柇锛?                if self._should_update_file(source_name, file_path, modified_time):
                    content = parse_document(file_path)
                    if content:
                        self._update_index(source_name, file_path, content)
                        # 鏇存柊鏈€鍚庡鐞嗘椂闂?                        self._update_last_processed_time(source_name, file_path, modified_time)
                        print(f"宸叉洿鏂版枃浠剁储寮? {file_path}")
                    else:
                        print(f"鏃犳硶瑙ｆ瀽鏂囦欢鍐呭: {file_path}")
            
            print(f"鏁版嵁婧愭洿鏂板畬鎴? {source_name}")
        except Exception as e:
            print(f"鏇存柊鏁版嵁婧愬け璐? {source_config['name']}, 閿欒: {str(e)}")
    
    def _should_update_file(self, source_name: str, file_path: str, modified_time: datetime) -> bool:
        """
        鍒ゆ柇鏂囦欢鏄惁闇€瑕佹洿鏂?        
        Args:
            source_name (str): 鏁版嵁婧愬悕绉?            file_path (str): 鏂囦欢璺緞
            modified_time (datetime): 鏂囦欢淇敼鏃堕棿
            
        Returns:
            bool: 鏄惁闇€瑕佹洿鏂?        """
        # 绠€鍗曞疄鐜帮細閫氳繃淇敼鏃堕棿鍒ゆ柇
        last_processed = self._get_last_processed_time(source_name, file_path)
        return not last_processed or modified_time > last_processed
    
    def _get_last_processed_time(self, source_name: str, file_path: str) -> datetime:
        """
        鑾峰彇鏂囦欢鏈€鍚庡鐞嗘椂闂?        
        Args:
            source_name (str): 鏁版嵁婧愬悕绉?            file_path (str): 鏂囦欢璺緞
            
        Returns:
            datetime: 鏈€鍚庡鐞嗘椂闂?        """
        # 绠€鍖栧疄鐜帮細浣跨敤鍐呭瓨瀛樺偍锛堝疄闄呭簲鐢ㄤ腑搴斾娇鐢ㄦ寔涔呭寲瀛樺偍锛?        key = f"{source_name}_{file_path}"
        return self.last_run_time.get(key)
    
    def _update_last_processed_time(self, source_name: str, file_path: str, processed_time: datetime):
        """
        鏇存柊鏂囦欢鏈€鍚庡鐞嗘椂闂?        
        Args:
            source_name (str): 鏁版嵁婧愬悕绉?            file_path (str): 鏂囦欢璺緞
            processed_time (datetime): 澶勭悊鏃堕棿
        """
        # 绠€鍖栧疄鐜帮細浣跨敤鍐呭瓨瀛樺偍锛堝疄闄呭簲鐢ㄤ腑搴斾娇鐢ㄦ寔涔呭寲瀛樺偍锛?        key = f"{source_name}_{file_path}"
        self.last_run_time[key] = processed_time
    
    def _update_index(self, source_name: str, file_path: str, content: str):
        """
        鏇存柊绱㈠紩锛堜笌鍚戦噺鏁版嵁搴撲氦浜掞級
        
        Args:
            source_name (str): 鏁版嵁婧愬悕绉?            file_path (str): 鏂囦欢璺緞
            content (str): 鏂囦欢鍐呭
        """
        try:
            # 1. 灏嗗唴瀹瑰垎鍧?            chunks = recursive_character_splitting(content)
            print(f"灏嗗唴瀹瑰垎鍧椾负 {len(chunks)} 涓墖娈?)
            
            # 2. 涓烘瘡涓潡鐢熸垚宓屽叆鍚戦噺骞跺瓨鍌ㄥ埌鍚戦噺鏁版嵁搴?            for i, chunk in enumerate(chunks):
                try:
                    # 鐢熸垚宓屽叆鍚戦噺
                    embedding = self.faq_vectordb.generate_embedding(chunk)
                    
                    # 瀛樺偍鍒板悜閲忔暟鎹簱
                    # 浣跨敤鏂囦欢璺緞浣滀负鏂囨。ID鍜孶RL
                    self.faq_vectordb.upsert_vector(
                        doc_id=file_path,
                        chunk_text=chunk,
                        embedding=embedding,
                        url=file_path,
                        chunk_index=i
                    )
                except Exception as e:
                    print(f"澶勭悊鍧?{i} 鏃跺嚭閿? {str(e)}")
                    continue
            
            print(f"鎴愬姛鏇存柊绱㈠紩: {file_path}")
        except Exception as e:
            print(f"鏇存柊绱㈠紩澶辫触: {file_path}, 閿欒: {str(e)}")
