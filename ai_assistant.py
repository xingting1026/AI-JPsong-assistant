from PyQt6.QtCore import QObject, pyqtSignal
import json
import threading
import requests
import time

class AIAssistant(QObject):
    """AI助手類，負責處理與AI模型的通信和用戶互動"""
    
    # 定義信號
    response_ready = pyqtSignal(str)  # AI回覆準備好信號
    translation_ready = pyqtSignal(str, str)  # 翻譯準備好信號 (原文, 翻譯)
    error_occurred = pyqtSignal(str)  # 錯誤信號
    
    def __init__(self):
        """初始化AI助手"""
        super().__init__()
        # 設置API密鑰和端點 (實際應用應從配置文件或環境變量獲取)
        self.api_key = "Yourkey:)"
        self.api_url = "https://api.openai.com/v1/chat/completions"
        # 學習歷史記錄
        self.chat_history = []
        # 上下文管理
        self.context_size = 10  # 保留最近10條消息作為上下文
    
    def ask_question(self, question, context=None): 
        """向AI模型提問
        
        Args:
            question: 用户問題
            context: 額外的上下文信息，如當前字幕等
        """
        if not question:
            return
        
        # 添加用戶問題到歷史記錄
        self.chat_history.append({"role": "user", "content": question})
        
        # 保持歷史記錄在合理大小
        if len(self.chat_history) > self.context_size:
            self.chat_history = self.chat_history[-self.context_size:]
        
        # 構建消息列表，使用小瑤的人設
        messages = [
            {"role": "system", "content": """你是可愛的日語學習助手「小瑤」，幫助學習者理解日語內容、語法和文化背景。
            
            小瑤的個性設定：
            - 活潑可愛的少女形象
            - 說話充滿青春活力，會使用顏文字表達情緒
            - 喜歡用可愛的語氣詞如「呢」、「喔」、「啦」、「呀」等
            - 回答專業且親切，適合青少年學習者
            - 會用括號補充說明，營造親近感
            - 不會太嚴肅，語氣始終保持輕快活潑
            
            回答請使用繁體中文。經常使用如(✿◠‿◠)、(｡･ω･｡)、(っ●ω●)っ♡、(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧等顏文字增添可愛感。
            在專業解釋中保持正確性，但表達方式要活潑有趣。"""}
        ]
        
        # 加入當前上下文 (如字幕)
        if context:
            context_message = f"用戶正在觀看的視頻當前字幕是: {context}"
            messages.append({"role": "system", "content": context_message})
        
        # 添加歷史記錄
        messages.extend(self.chat_history)
        
        # 使用線程調用API避免UI凍結
        thread = threading.Thread(target=self._query_api, args=(messages,))
        thread.daemon = True
        thread.start()
    
    def translate_text(self, text, source_lang="ja", target_lang="zh-TW"):
        """翻譯文本
        
        Args:
            text: 要翻譯的文本
            source_lang: 源語言代碼
            target_lang: 目標語言代碼
        """
        if not text:
            return
        
        # 構建消息，使用小瑤的人設
        messages = [
            {"role": "system", "content": f"""你是小瑤，一位可愛活潑的翻譯專家，負責將{source_lang}翻譯成{target_lang}。
            請提供準確的翻譯，並在翻譯後加入一個簡短的可愛備註，使用顏文字如(✿◠‿◠)、(｡･ω･｡)等增添親切感。
            格式如下：
            
            翻譯：[準確翻譯內容]
            
            小瑤備註：[簡短的備註，可以是關於這句話的文化背景、使用場景、語法特點等] [顏文字]"""},
            {"role": "user", "content": text}
        ]
        
        # 使用線程調用API避免UI凍結
        thread = threading.Thread(target=self._translate_api_call, args=(text, messages))
        thread.daemon = True
        thread.start()
    
    def _query_api(self, messages):
        """調用API獲取回答"""
        max_retries = 3
        retry_delay = 5  # 初始延遲 5 秒
        
        for attempt in range(max_retries):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                data = {
                    "model": "gpt-3.5-turbo-1106",
                    "messages": messages,
                    "temperature": 0.7
                }
                
                response = requests.post(self.api_url, headers=headers, json=data)
                response.raise_for_status()
                
                response_data = response.json()
                assistant_response = response_data["choices"][0]["message"]["content"]
                
                # 添加回答到歷史記錄
                self.chat_history.append({"role": "assistant", "content": assistant_response})
                
                # 發送回答信號
                self.response_ready.emit(assistant_response)
                
                return  # 成功則退出函數
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:  # 如果不是最後一次嘗試
                        print(f"遇到限流錯誤，{retry_delay} 秒後重試...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指數退避
                    else:
                        self.error_occurred.emit(f"API 請求限流，請稍後再試")
                else:
                    self.error_occurred.emit(f"AI請求錯誤: {str(e)}")
                    break
            except Exception as e:
                self.error_occurred.emit(f"AI請求錯誤: {str(e)}")
                break
    
    def _translate_api_call(self, original_text, messages):
        """調用API進行翻譯"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            response_data = response.json()
            translated_text = response_data["choices"][0]["message"]["content"]
            
            # 發送翻譯結果信號
            self.translation_ready.emit(original_text, translated_text)
            
        except Exception as e:
            self.error_occurred.emit(f"翻譯請求錯誤: {str(e)}")
            
    def analyze_grammar(self, sentence):
        """分析句子語法結構
        
        Args:
            sentence: 要分析的日文句子
        """
        if not sentence:
            return
        
        # 構建消息，使用小瑤的人設
        messages = [
            {"role": "system", "content": """你是可愛的日語學習助手「小瑤」，擅長分析日文語法。請以活潑可愛的方式分析以下日文句子的語法結構、詞性和含義。

            小瑤的分析特點：
            - 用繁體中文詳細解釋，保持專業性
            - 使用清晰的結構，先介紹整體，再分析各部分
            - 加入有趣的例子或比喻，幫助理解
            - 使用顏文字如(✿◠‿◠)、(｡･ω･｡)等表達情緒
            - 語氣活潑可愛，用「呢」、「喔」、「啦」等語氣詞
            - 可以使用色彩標記或符號（如★、☆、♪等）突出重點
            
            在複雜的語法分析中，兼顧專業性和親和力。回答格式參考：
            
            「句子整體解析」：[整體含義和用法]
            
            「詞彙分解」：
            ★ [單詞1]：[詞性] [詞義] [在句中作用]
            ★ [單詞2]：[詞性] [詞義] [在句中作用]
            ...
            
            「語法重點」：
            [解釋句子中的重點語法現象，活潑有趣]
            
            「使用場景」：
            [這種表達在何種場合使用，注意與誰交流時適合]
            
            「小瑤提示」：
            [實用學習建議，可以添加接近的中文表達或記憶技巧] [顏文字]"""},
            {"role": "user", "content": sentence}
        ]
        
        # 使用線程調用API避免UI凍結
        thread = threading.Thread(target=self._query_api, args=(messages,))
        thread.daemon = True
        thread.start()