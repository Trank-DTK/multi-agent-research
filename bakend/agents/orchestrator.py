# 任务编排器
from datetime import datetime
from typing import Dict
from .models import Task,TaskStep




class AgentOrchestrator:
    """多智能体编排器"""
    
    def __init__(self, user):
        self.user = user
        self.agents = {}  # 注册的智能体
        self.tasks = {}
    
    def register_agent(self, name, agent_instance):
        """注册智能体"""
        self.agents[name] = agent_instance
        print(f"已注册智能体: {name}")
    
    def get_agent(self, name):
        """获取智能体实例"""
        return self.agents.get(name)
    
    def run_workflow(self, workflow_type: str, input_data: Dict) -> Dict:
        """运行工作流"""

        if workflow_type == "research_pipeline":
            return self._research_pipeline(input_data)
        elif workflow_type == "experiment_design":
            return self._experiment_design_workflow(input_data)
        elif workflow_type == "literature_review":
            return self._literature_review_workflow(input_data)
        else:
            return {"error": f"未知工作流类型: {workflow_type}"}
    
    def _research_pipeline(self, input_data: Dict) -> Dict:
        """完整研究流程：文献调研 -> 实验设计 -> 方案整合"""
        
        research_question = input_data.get("question", "")
        if not research_question:
            return {"error": "请提供研究问题"}
        
        results = {}
        
        # 步骤1：文献调研
        print("步骤1: 文献调研...")
        literature_agent = self.get_agent("literature")
        if literature_agent:
            try:
                lit_result = literature_agent.run(
                    f"请帮我调研以下研究问题的相关文献：{research_question}\n"
                    "请提供：1. 核心研究成果 2. 主要方法 3. 研究空白"
                )
                results["literature_review"] = lit_result
            except Exception as e:
                results["literature_review"] = f"文献调研失败：{str(e)}"
        else:
            results["literature_review"] = "文献助手未注册"
        
        # 步骤2：基于文献设计实验
        print("步骤2: 实验设计...")
        experiment_agent = self.get_agent("experiment")
        if experiment_agent:
            try:
                exp_prompt = f"""请根据以下文献调研结果，设计实验方案：

研究问题：{research_question}

文献调研结果：
{results.get('literature_review', '无')}

请设计详细的实验方案。"""
                
                exp_result = experiment_agent.run(exp_prompt)
                results["experiment_design"] = exp_result
            except Exception as e:
                results["experiment_design"] = f"实验设计失败：{str(e)}"
        else:
            results["experiment_design"] = "实验助手未注册"
        
        # 步骤3：整合方案
        print("步骤3: 整合方案...")
        
        summary_prompt = f"""请将以下研究内容整合成一个完整的研究方案：

研究问题：{research_question}

文献调研：
{results.get('literature_review', '无')}

实验设计：
{results.get('experiment_design', '无')}

请输出一份结构化的研究方案报告。"""
        
        # 使用通用Agent或LLM整合
        summary_agent = self.get_agent("general")
        if summary_agent:
            try:
                results["final_report"] = summary_agent.run(summary_prompt)
            except Exception as e:
                results["final_report"] = f"方案整合失败：{str(e)}"
        else:
            # 如果没有通用Agent，简单拼接
            results["final_report"] = f"""
# 研究方案报告

## 研究问题
{research_question}

## 文献调研结果
{results.get('literature_review', '无')}

## 实验设计方案
{results.get('experiment_design', '无')}
"""
        
        return results
    
    def _experiment_design_workflow(self, input_data: Dict) -> Dict:
        """实验设计工作流"""
        research_topic = input_data.get("topic", "")
        
        results = {}
        
        # 使用实验助手
        experiment_agent = self.get_agent("experiment")
        if experiment_agent:
            try:
                results["design"] = experiment_agent.run(
                    f"请为以下研究主题设计实验方案：{research_topic}"
                )
            except Exception as e:
                results["error"] = str(e)
        
        return results
    
    def _literature_review_workflow(self, input_data: Dict) -> Dict:
        """文献综述工作流"""
        query = input_data.get("query", "")
        
        results = {}
        
        # 使用文献助手
        literature_agent = self.get_agent("literature")
        if literature_agent:
            try:
                results["review"] = literature_agent.run(
                    f"请帮我调研以下主题的文献：{query}"
                )
            except Exception as e:
                results["error"] = str(e)
        
        return results


class TaskOrchestrator:
    """任务编排器（带数据库存储）"""
    
    def __init__(self, user):
        self.user = user
        self.agent_orchestrator = AgentOrchestrator(user)
    
    def register_agents(self, literature_agent=None, experiment_agent=None):
        """注册智能体"""
        if literature_agent:
            self.agent_orchestrator.register_agent("literature", literature_agent)
        if experiment_agent:
            self.agent_orchestrator.register_agent("experiment", experiment_agent)
    
    def execute_research_task(self, question: str, conversation=None) -> Dict:
        """执行研究任务"""

        # 创建任务记录
        task = Task.objects.create(
            user=self.user,
            conversation=conversation,
            title=question[:50],
            description=question,
            status='running'
        )

        try:
            # 记录步骤
            step1 = TaskStep.objects.create(
                task=task,
                agent_name="literature",
                action="文献调研",
                input_data=question,
                order=1,
                status='running'
            )

            # 执行工作流
            results = self.agent_orchestrator.run_workflow(
                "research_pipeline",
                {"question": question}
            )
            
            # 更新步骤状态
            step1.status = 'completed'
            step1.output_data = results.get('literature_review', '')[:500]
            step1.completed_at = datetime.now()
            step1.save()
            
            step2 = TaskStep.objects.create(
                task=task,
                agent_name="experiment",
                action="实验设计",
                input_data=question,
                order=2,
                status='completed'
            )
            step2.output_data = results.get('experiment_design', '')[:500]
            step2.completed_at = datetime.now()
            step2.save()
            
            # 更新任务状态
            task.status = 'completed'
            task.result = results.get('final_report', '')
            task.save()
            
            return results
            
        except Exception as e:
            task.status = 'failed'
            task.result = str(e)
            task.save()
            return {"error": str(e)}