from langchain_classic.tools import BaseTool
from datetime import datetime
import random
from typing import Optional, Type
from pydantic import BaseModel, Field

class CurrentTimeTool(BaseTool):
    """获取当前时间的工具"""
    name:str = "current_time"
    description:str = "获取当前时间，输入任意字符串即可"
    
    def _run(self, query: str = "") -> str:
        """同步执行"""
        now = datetime.now()
        return f"当前时间是：{now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    async def _arun(self, query: str = "") -> str:
        """异步调用"""
        return await self._run(query)


class RandomNumberTool(BaseTool):
    """生成随机数的工具"""
    name:str = "random_number"
    description:str = "生成随机整数。输入格式：'最小值 最大值'，如 '1 100'"
    
    def _run(self, query: str) -> str:
        try:
            parts = query.strip().split()
            if len(parts) == 2:
                min_val, max_val = map(int, parts)
                result = random.randint(min_val, max_val)
                return f"生成的随机数是：{result}"
            else:
                return "请提供两个数字，例如 '1 100'"
        except Exception as e:
            return f"错误：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return await self._run(query)


class CalculatorTool(BaseTool):
    """计算器工具"""
    name:str = "calculator"
    description:str = "计算数学表达式。输入数学表达式，如 '123 * 456'"
    
    def _run(self, query: str) -> str:
        try:
            # 只允许安全字符
            allowed = set("0123456789+-*/(). ")
            if not all(c in allowed for c in query):
                return "表达式包含非法字符"
            result = eval(query)
            return f"计算结果：{result}"
        except Exception as e:
            return f"计算错误：{str(e)}"
    
    async def _arun(self, query: str) -> str:
        return await self._run(query)