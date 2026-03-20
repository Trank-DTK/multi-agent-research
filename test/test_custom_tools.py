# test/test_custom_tools.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bakend.agents.tools import CurrentTimeTool, RandomNumberTool, CalculatorTool

# 测试工具
time_tool = CurrentTimeTool()
print(time_tool.run(""))

rand_tool = RandomNumberTool()
print(rand_tool.run("1 100"))

calc_tool = CalculatorTool()
print(calc_tool.run("123 * 456"))