# 数据分析Agent API
import traceback
import os
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Dataset
from .services import DataAnalysisService

agent_instances = {}

class AnalysisAgentChatView(APIView):
    """数据分析Agent聊天接口"""
    permission_classes = [IsAuthenticated]

    def post(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)

            # 打印调试信息
            print(f"数据集文件路径: {dataset.file.path}")
            print(f"文件是否存在: {os.path.exists(dataset.file.path)}")

            try:
                df = DataAnalysisService.load_dataframe(dataset.file.path)
                print(f"数据加载成功，行数: {len(df)}, 列数: {len(df.columns)}")
            except Exception as load_error:
                print(f"数据加载失败: {load_error}")
                import traceback
                load_trace = traceback.format_exc()
                print(f"加载错误详情: {load_trace}")
                return JsonResponse({
                    'error': f'数据加载失败: {str(load_error)}',
                    'trace': load_trace,
                    'type': 'data_load_failed'
                }, status=500)

            message = request.data.get('message')
            if not message:
                return JsonResponse({'error': '消息不能为空'}, status=400)

            # 获取或创建Agent实例
            agent_key = f"analysis_{dataset_id}_{request.user.id}"
            if agent_key not in agent_instances:
                # 延迟导入，避免模块加载时失败
                try:
                    from agents.analysis_agent import create_analysis_agent
                    agent = create_analysis_agent(df, verbose=False)
                    agent_instances[agent_key] = agent
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"创建Agent失败: {e}\n{error_trace}")
                    # 返回完整的错误信息用于调试
                    return JsonResponse({
                        'error': f'创建Agent失败: {str(e)}',
                        'trace': error_trace,
                        'type': 'agent_creation_failed'
                    }, status=500)
            else:
                agent = agent_instances[agent_key]

            # 尝试使用 invoke 方法，避免 LangChain 弃用警告
            try:
                response = agent.invoke({'input': message})
                if isinstance(response, dict) and 'output' in response:
                    response = response['output']
                elif isinstance(response, dict) and 'result' in response:
                    response = response['result']
            except Exception as e:
                # 回退到 run 方法
                print(f"invoke failed: {e}, falling back to run")
                response = agent.run(message)

            return JsonResponse({
                'response': response,
                'dataset_id': dataset_id
            })

        except Dataset.DoesNotExist:
            return JsonResponse({'error': '数据集不存在'}, status=404)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Agent error: {e}\n{error_trace}")
            # 返回完整的错误信息用于调试
            return JsonResponse({
                'error': f'服务器内部错误: {str(e)}',
                'trace': error_trace,
                'type': 'server_error'
            }, status=500)