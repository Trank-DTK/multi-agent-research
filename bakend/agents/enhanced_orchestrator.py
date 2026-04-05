# 增强版编排器
import asyncio
import time
from typing import Dict, List, Any
from .parallel_executor import ParallelExecutor, AsyncParallelExecutor
from .workflow_dag import WorkflowDAG, ResearchWorkflowBuilder
from .cache_service import CacheService, CachedLLM
from .audit_middleware import AuditLogService

class EnhancedOrchestrator:
    """增强版编排器（集成并行执行、DAG工作流、缓存）"""
    
    def __init__(self, user, literature_agent=None, experiment_agent=None, critic_agent=None):
        self.user = user
        self.literature_agent = literature_agent
        self.experiment_agent = experiment_agent
        self.critic_agent = critic_agent
        self.parallel_executor = ParallelExecutor()
        self.async_executor = AsyncParallelExecutor()
        self.cache_service = CacheService()
    
    async def execute_with_cache(self, key_prefix: str, func, *args, **kwargs):
        """带缓存的执行"""
        cache_key = f"{key_prefix}:{self.user.id}"
        
        # 尝试从缓存获取
        cached_result = CacheService.get_llm_response(
            model="qwen2.5:7b",
            prompt=str(args)[:200] + str(kwargs)[:200],
            temperature=0.7
        )
        
        if cached_result:
            return cached_result
        
        # 执行函数
        result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        # 存入缓存
        CacheService.set_llm_response(
            model="qwen2.5:7b",
            prompt=str(args)[:200],
            temperature=0.7,
            response=str(result)[:1000]
        )
        
        return result
    
    async def execute_parallel_research(self, question: str) -> Dict:
        """并行执行研究任务"""
        start_time = time.time()
        
        tasks = []
        
        if self.literature_agent:
            tasks.append({
                "name": "literature_review",
                "func": self.literature_agent.arun if hasattr(self.literature_agent, 'arun') else self.literature_agent.run,
                "args": [f"请调研以下研究问题的相关文献：{question}"],
                "kwargs": {}
            })
        
        if self.experiment_agent:
            tasks.append({
                "name": "experiment_design",
                "func": self.experiment_agent.arun if hasattr(self.experiment_agent, 'arun') else self.experiment_agent.run,
                "args": [f"请为以下研究问题设计实验方案：{question}"],
                "kwargs": {}
            })
        
        results = await self.async_executor.run_parallel(tasks)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 记录审计
        AuditLogService.log(
            user=self.user,
            action_type='workflow_execution',
            action_name='并行研究执行',
            input_data=question[:200],
            output_data=f"完成 {len([r for r in results if r['success']])}/{len(results)} 个任务",
            duration_ms=duration_ms
        )
        
        return {
            "literature_review": next((r["result"] for r in results if r["name"] == "literature_review" and r["success"]), ""),
            "experiment_design": next((r["result"] for r in results if r["name"] == "experiment_design" and r["success"]), ""),
            "errors": [r["error"] for r in results if not r["success"]],
            "duration_ms": duration_ms
        }
    
    async def execute_dag_workflow(self, question: str) -> Dict:
        """执行DAG工作流"""
        start_time = time.time()
        
        # 构建工作流
        builder = ResearchWorkflowBuilder()
        dag = builder.build_research_workflow(
            self.literature_agent or self._create_dummy_agent(),
            self.literature_agent or self._create_dummy_agent(),
            self.experiment_agent or self._create_dummy_agent(),
            self.critic_agent or self._create_dummy_agent()
        )
        
        # 执行工作流
        results = await dag.execute({"question": question})
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        AuditLogService.log(
            user=self.user,
            action_type='workflow_execution',
            action_name='DAG工作流执行',
            input_data=question[:200],
            output_data=f"完成节点: {list(results.keys())}",
            duration_ms=duration_ms
        )
        
        return {
            "results": results,
            "duration_ms": duration_ms
        }
    
    def _create_dummy_agent(self):
        """创建虚拟Agent（用于测试）"""
        class DummyAgent:
            async def arun(self, prompt):
                return f"模拟响应: {prompt[:100]}..."
            def run(self, prompt):
                return f"模拟响应: {prompt[:100]}..."
        return DummyAgent()