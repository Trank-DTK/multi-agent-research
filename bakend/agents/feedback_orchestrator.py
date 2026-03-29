# 编排器（带有反馈循环）
import time
from typing import Dict, List
from .critic_agent import CriticService
from .orchestrator import TaskOrchestrator
from .audit_middleware import AuditLogService

class FeedbackOrchestrator(TaskOrchestrator):
    """带反馈循环的编排器"""
    
    def __init__(self, user):
        super().__init__(user)
        self.critic = CriticService()
        self.max_retries = 2  # 最大重试次数
    
    def execute_research_task_with_feedback(self, question: str, conversation=None) -> Dict:
        """带反馈循环的研究任务"""
        
        start_time = time.time()
        
        # 第一步：执行研究任务
        results = super().execute_research_task(question, conversation)
        
        if 'error' in results:
            return results
        
        literature_review = results.get('literature_review', '')
        experiment_design = results.get('experiment_design', '')
        
        # 第二步：Critic评估
        evaluation = self.critic.full_evaluation(
            question,
            literature_review,
            experiment_design
        )
        
        results['evaluation'] = evaluation
        
        # 记录审计日志
        AuditLogService.log(
            user=self.user,
            action_type='critic_evaluation',
            action_name='研究任务评审',
            input_data=question[:500],
            output_data=f"综合评分: {evaluation['overall_score']}, 通过: {evaluation['passed']}",
            duration_ms=int((time.time() - start_time) * 1000)
        )
        
        # 第三步：如果评分低于阈值，尝试优化
        if not evaluation['passed'] and self.max_retries > 0:
            results['optimization_attempted'] = True
            improved_results = self._optimize_research(
                question, 
                literature_review, 
                experiment_design,
                evaluation['suggestions']
            )
            
            if improved_results:
                results.update(improved_results)
                # 再次评估优化后的结果
                new_evaluation = self.critic.full_evaluation(
                    question,
                    improved_results.get('literature_review', ''),
                    improved_results.get('experiment_design', '')
                )
                results['improved_evaluation'] = new_evaluation
                results['improved'] = new_evaluation['passed']
        
        return results
    
    def _optimize_research(self, question: str, literature: str, 
                                  experiment: str, suggestions: List[str]) -> Dict:
        """根据建议优化研究内容"""
        
        improvements = {}
        
        # 优化文献综述
        if literature and suggestions:
            try:
                lit_agent = self.agent_orchestrator.get_agent("literature")
                if lit_agent:
                    improvement_prompt = f"""请根据以下改进建议优化文献综述：

改进建议：{suggestions[:500]}

当前文献综述：
{literature[:1000]}

请输出优化后的文献综述。"""
                    improved_lit = lit_agent.run(improvement_prompt)
                    improvements['literature_review'] = improved_lit
            except Exception as e:
                print(f"文献优化失败: {e}")
        
        # 优化实验设计
        if experiment and suggestions:
            try:
                exp_agent = self.agent_orchestrator.get_agent("experiment")
                if exp_agent:
                    improvement_prompt = f"""请根据以下改进建议优化实验设计：

改进建议：{suggestions[:500]}

当前实验设计：
{experiment[:1000]}

请输出优化后的实验设计方案。"""
                    improved_exp = exp_agent.run(improvement_prompt)
                    improvements['experiment_design'] = improved_exp
            except Exception as e:
                print(f"实验优化失败: {e}")
        
        return improvements