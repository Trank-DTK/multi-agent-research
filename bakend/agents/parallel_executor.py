# 并行执行器
import asyncio
import concurrent.futures
import threading
from typing import List, Dict, Any, Callable
from datetime import datetime
from django.db import transaction
from .audit_middleware import AuditLogService

class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    def run_parallel(self, tasks: List[Dict]) -> List[Dict]:
        """
        并行执行多个任务
        
        tasks格式:
        [
            {"name": "任务1", "func": callable, "args": [], "kwargs": {}},
            {"name": "任务2", "func": callable, "args": [], "kwargs": {}},
        ]
        """
        results = []
        futures = []
        
        for task in tasks:
            future = self.executor.submit(
                self._run_with_error_handling,
                task["func"],
                task.get("args", []),
                task.get("kwargs", {}),
                task.get("name", "unknown")
            )
            futures.append((task.get("name", f"task_{len(futures)}"), future))
        
        for name, future in futures:
            try:
                result = future.result(timeout=60)
                results.append({
                    "name": name,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "name": name,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def _run_with_error_handling(self, func, args, kwargs, name):
        """带错误处理的执行"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise Exception(f"{name} 执行失败: {str(e)}")
    
    def shutdown(self):
        self.executor.shutdown(wait=True)


class AsyncParallelExecutor:
    """异步并行执行器"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)  #控制同时执行的信号量
    
    async def run_parallel(self, tasks: List[Dict]) -> List[Dict]:
        """异步并行执行多个协程任务"""
        results = []
        
        async def run_one(task):
            async with self.semaphore:
                try:
                    if asyncio.iscoroutinefunction(task["func"]):
                        result = await task["func"](*task.get("args", []), **task.get("kwargs", {}))
                    else:
                        # 在线程池中运行同步函数
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(
                            None,
                            task["func"],
                            *task.get("args", []),
                            **task.get("kwargs", {})
                        )
                    return {
                        "name": task.get("name", "unknown"),
                        "success": True,
                        "result": result
                    }
                except Exception as e:
                    return {
                        "name": task.get("name", "unknown"),
                        "success": False,
                        "error": str(e)
                    }
        
        # 并发执行所有任务
        tasks_coro = [run_one(task) for task in tasks]
        results = await asyncio.gather(*tasks_coro, return_exceptions=False)
        
        return results


class ParallelOrchestrator:
    """并行编排器"""
    
    def __init__(self, user):
        self.user = user
        self.parallel_executor = ParallelExecutor()
        self.async_executor = AsyncParallelExecutor()
    
    def execute_parallel_research_tasks(self, research_question: str, 
                                         literature_agent, experiment_agent) -> Dict:
        """并行执行研究任务"""
        
        tasks = [
            {
                "name": "literature_review",
                "func": literature_agent.run,
                "args": [f"请调研以下研究问题的相关文献：{research_question}"],
                "kwargs": {}
            },
            {
                "name": "methodology_suggestion",
                "func": experiment_agent.run,
                "args": [f"请为以下研究问题推荐研究方法论：{research_question}"],
                "kwargs": {}
            },
            {
                "name": "related_concepts",
                "func": self._get_related_concepts,
                "args": [research_question],
                "kwargs": {}
            }
        ]
        
        results = self.parallel_executor.run_parallel(tasks)
        
        # 记录审计
        AuditLogService.log(
            user=self.user,
            action_type='workflow_execution',
            action_name='并行研究任务',
            input_data=research_question[:200],
            output_data=f"完成 {len([r for r in results if r['success']])}/{len(results)} 个任务",
            duration_ms=0  # 实际应该计算耗时
        )
        
        return {
            "literature_review": next((r["result"] for r in results if r["name"] == "literature_review" and r["success"]), ""),
            "methodology": next((r["result"] for r in results if r["name"] == "methodology_suggestion" and r["success"]), ""),
            "related_concepts": next((r["result"] for r in results if r["name"] == "related_concepts" and r["success"]), []),
            "errors": [r["error"] for r in results if not r["success"]]
        }
    
    def _get_related_concepts(self, question: str) -> List[str]:
        """获取相关概念（模拟）"""
        # 实际应该调用知识库或LLM
        return ["深度学习", "神经网络", "机器学习"]