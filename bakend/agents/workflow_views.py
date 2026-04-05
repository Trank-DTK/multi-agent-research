# 工作流API
import asyncio
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .workflow_dag import ResearchWorkflowBuilder
from .literature_agent import create_literature_agent
from .experiment_agent import create_experiment_agent
from .critic_agent import create_critic_agent
from .agent import get_ollama_base_url
from langchain_community.llms import Ollama

class WorkflowExecuteView(APIView):
    """工作流执行接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        question = request.data.get('question')
        
        if not question:
            return JsonResponse({'error': '研究问题不能为空'}, status=400)
        
        # 创建临时Agent（简化版）
        llm = Ollama(
            model="qwen2.5:7b",
            base_url=get_ollama_base_url(),
            temperature=0.7
        )
        
        class SimpleAgent:
            def __init__(self, llm):
                self.llm = llm
            async def arun(self, prompt):
                return self.llm.invoke(prompt)
        
        simple_agent = SimpleAgent(llm)
        
        # 构建工作流
        builder = ResearchWorkflowBuilder()
        dag = builder.build_research_workflow(simple_agent, simple_agent, simple_agent, simple_agent)
        
        # 执行工作流
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(dag.execute({"question": question}))
            loop.close()
            
            return JsonResponse({
                'success': True,
                'results': {
                    'analysis': results.get('analysis', ''),
                    'literature': results.get('literature', ''),
                    'experiment': results.get('experiment', ''),
                    'consistency': results.get('consistency', ''),
                    'report': results.get('report', '')
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class WorkflowStatusView(APIView):
    """工作流状态查询"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, workflow_id):
        # 实际应该从缓存或数据库获取工作流状态
        return JsonResponse({
            'workflow_id': workflow_id,
            'status': 'running',
            'progress': 50,
            'current_node': '文献调研'
        })