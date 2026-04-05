#工作流DAG
from typing import Dict, List, Any, Set
from collections import deque
import asyncio
import hashlib
import json

class DAGNode:
    """DAG节点 数据结构"""
    
    def __init__(self, node_id: str, name: str, func, depends_on: List[str] = None):
        self.node_id = node_id
        self.name = name
        self.func = func  #节点执行的函数，可以是同步或异步
        self.depends_on = depends_on or []  #依赖哪些节点
        self.depended_by = []    #被哪些节点依赖（自动计算）
        self.result = None
        self.error = None
        self.status = "pending"  # pending, running, completed, failed
    
    def add_dependency(self, node_id: str):
        if node_id not in self.depends_on:
            self.depends_on.append(node_id)


class WorkflowDAG:
    """工作流有向无环图"""
    
    def __init__(self, name: str = "workflow"):
        self.name = name
        self.nodes: Dict[str, DAGNode] = {}
        self.execution_context = {}
    
    def add_node(self, node_id: str, name: str, func, depends_on: List[str] = None):
        """添加节点"""
        self.nodes[node_id] = DAGNode(node_id, name, func, depends_on)
        self._update_dependencies()  
    
    def _update_dependencies(self):
        """更新依赖关系"""
        # 清空depended_by
        for node in self.nodes.values():
            node.depended_by = []
        
        # 重建依赖关系
        for node_id, node in self.nodes.items():
            for dep_id in node.depends_on:
                if dep_id in self.nodes:
                    self.nodes[dep_id].depended_by.append(node_id)
    
    def validate(self) -> bool:
        """验证DAG是否有环(DFS)"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = self.nodes[node_id]
            for next_id in node.depended_by:
                if next_id not in visited:
                    if has_cycle(next_id):
                        return True
                elif next_id in rec_stack:
                    return True #有环
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    return False  #有环
        
        return True
    
    def get_execution_order(self) -> List[str]:
        """获取拓扑排序的执行顺序 Kahn算法"""
        if not self.validate():
            raise ValueError("DAG存在环，无法执行")
        
        in_degree = {node_id: len(node.depends_on) for node_id, node in self.nodes.items()}
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        order = []
        
        while queue:
            node_id = queue.popleft()
            order.append(node_id)
            
            node = self.nodes[node_id]
            for next_id in node.depended_by:
                in_degree[next_id] -= 1
                if in_degree[next_id] == 0:
                    queue.append(next_id)
        
        if len(order) != len(self.nodes):
            raise ValueError("DAG存在环（部分节点未执行）")
        
        return order
    
    async def execute(self, context: Dict = None) -> Dict:
        """执行工作流"""
        self.execution_context = context or {}
        execution_order = self.get_execution_order()
        results = {}
        
        for node_id in execution_order:
            node = self.nodes[node_id]
            
            # 检查依赖是否完成
            deps_ready = all(
                self.nodes[dep_id].status == "completed"
                for dep_id in node.depends_on
            )
            
            if not deps_ready:
                raise ValueError(f"节点 {node_id} 的依赖未就绪")
            
            node.status = "running"
            
            try:
                # 准备参数（依赖节点的结果）
                args = []
                for dep_id in node.depends_on:
                    if self.nodes[dep_id].result:
                        args.append(self.nodes[dep_id].result)
                
                # 执行节点函数
                if asyncio.iscoroutinefunction(node.func):
                    result = await node.func(*args, **self.execution_context)
                else:
                    result = node.func(*args, **self.execution_context)
                
                node.result = result
                node.status = "completed"
                results[node_id] = result
                
            except Exception as e:
                node.status = "failed"
                node.error = str(e)
                results[node_id] = {"error": str(e)}
                raise
        
        return results


class ResearchWorkflowBuilder:
    """研究工作流构建器"""
    
    def __init__(self):
        self.dag = WorkflowDAG("research_workflow")
    
    def build_research_workflow(self, research_agent, literature_agent, experiment_agent, critic_agent):
        """构建研究工作流"""
        
        # 定义节点函数（需要适配实际Agent）
        async def research_question_analysis(question: str):
            return await research_agent.arun(f"请分析以下研究问题的核心要素：{question}")
        
        async def literature_search(question_analysis: str, question: str):
            return await literature_agent.arun(f"请调研以下研究问题的文献：{question}")
        
        async def experiment_design(question_analysis: str, question: str):
            return await experiment_agent.arun(f"请设计以下研究问题的实验方案：{question}")
        
        async def consistency_check(literature: str, experiment: str):
            return await critic_agent.arun(
                f"请检查文献调研和实验设计的一致性：\n文献：{literature[:500]}\n实验：{experiment[:500]}"
            )
        
        async def generate_report(literature: str, experiment: str, consistency: str):
            report = f"""
# 研究报告

## 文献调研
{literature}

## 实验设计
{experiment}

## 一致性检查
{consistency}
"""
            return report
        
        # 添加节点
        self.dag.add_node("analysis", "问题分析", research_question_analysis)
        self.dag.add_node("literature", "文献调研", literature_search, depends_on=["analysis"])
        self.dag.add_node("experiment", "实验设计", experiment_design, depends_on=["analysis"])
        self.dag.add_node("consistency", "一致性检查", consistency_check, depends_on=["literature", "experiment"])
        self.dag.add_node("report", "生成报告", generate_report, depends_on=["literature", "experiment", "consistency"])
        
        return self.dag