# 评审Agent
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.memory import ConversationBufferMemory
from langchain_ollama import OllamaLLM
from .critic_tools import (
    QualityEvaluatorTool,
    ConsistencyCheckerTool,
    FeasibilityCheckerTool,
    NoveltyEvaluatorTool
)
from .agent import get_ollama_base_url

def create_critic_agent(verbose=True):
    """创建Critic评审智能体"""
    
    llm = OllamaLLM(
        model="qwen2.5:7b",
        base_url=get_ollama_base_url(),
        temperature=0.3  # 降低温度，让评估更稳定
    )
    
    tools = [
        QualityEvaluatorTool(llm=llm),
        ConsistencyCheckerTool(llm=llm),
        FeasibilityCheckerTool(llm=llm),
        NoveltyEvaluatorTool(llm=llm),
    ]
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,   #ReAct Agent
        memory=memory,
        verbose=verbose,
        handle_parsing_errors=True
    )
    
    return agent


class CriticService:
    """评审服务"""
    
    def __init__(self):
        self.agent = create_critic_agent(verbose=False)
    
    def evaluate_quality(self, content: str) -> dict:
        """评估内容质量"""
        try:
            query = f"使用quality_evaluator工具评估以下内容：\n{content[:500]}"  # 限制长度
            print(f"[CRITIC_DEBUG] 评估内容质量，长度: {len(content)}")
            result = self.agent.run(query)
            print(f"[CRITIC_DEBUG] LLM原始响应: {result[:200]}...")
            parsed = self._parse_critic_result(result, "quality")
            print(f"[CRITIC_DEBUG] 解析结果: score={parsed['score']}, suggestions={len(parsed['suggestions'])}")
            return parsed
        except Exception as e:
            print(f"[CRITIC_DEBUG] 评估失败: {str(e)}")
            return {
                "score": 0,
                "error": str(e),
                "suggestions": ["评审失败，请重试"]
            }
    
    def check_consistency(self, content1: str, content2: str) -> dict:
        """检查一致性"""
        try:
            query = f"使用consistency_checker工具检查：{content1[:250]} | {content2[:250]}"
            print(f"[CRITIC_DEBUG] 检查一致性")
            result = self.agent.run(query)
            print(f"[CRITIC_DEBUG] 一致性检查原始响应: {result[:200]}...")
            parsed = self._parse_critic_result(result, "consistency")
            print(f"[CRITIC_DEBUG] 一致性解析结果: score={parsed['score']}")
            return parsed
        except Exception as e:
            print(f"[CRITIC_DEBUG] 一致性检查失败: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def check_feasibility(self, content: str) -> dict:
        """检查可行性"""
        try:
            query = f"使用feasibility_checker工具评估：\n{content[:500]}"
            print(f"[CRITIC_DEBUG] 检查可行性")
            result = self.agent.run(query)
            print(f"[CRITIC_DEBUG] 可行性检查原始响应: {result[:200]}...")
            parsed = self._parse_critic_result(result, "feasibility")
            print(f"[CRITIC_DEBUG] 可行性解析结果: score={parsed['score']}")
            return parsed
        except Exception as e:
            print(f"[CRITIC_DEBUG] 可行性检查失败: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def evaluate_novelty(self, content: str) -> dict:
        """评估创新性"""
        try:
            query = f"使用novelty_evaluator工具评估：\n{content[:500]}"
            print(f"[CRITIC_DEBUG] 评估创新性")
            result = self.agent.run(query)
            print(f"[CRITIC_DEBUG] 创新性评估原始响应: {result[:200]}...")
            parsed = self._parse_critic_result(result, "novelty")
            print(f"[CRITIC_DEBUG] 创新性解析结果: score={parsed['score']}")
            return parsed
        except Exception as e:
            print(f"[CRITIC_DEBUG] 创新性评估失败: {str(e)}")
            return {"score": 0, "error": str(e)}
    
    def full_evaluation(self, research_question: str, literature_review: str, 
                        experiment_design: str) -> dict:
        """完整评估"""
        evaluation = {
            "research_question": research_question,
            "overall_score": 0,
            "dimensions": {},
            "suggestions": [],
            "passed": False
        }
        
        # 评估文献综述质量
        lit_eval = self.evaluate_quality(literature_review)
        evaluation["dimensions"]["literature_review"] = lit_eval
        
        # 评估实验设计质量
        exp_eval = self.evaluate_quality(experiment_design)
        evaluation["dimensions"]["experiment_design"] = exp_eval
        
        # 检查一致性
        consistency = self.check_consistency(literature_review, experiment_design)
        evaluation["dimensions"]["consistency"] = consistency
        
        # 评估可行性
        feasibility = self.check_feasibility(experiment_design)
        evaluation["dimensions"]["feasibility"] = feasibility
        
        # 计算综合评分（加权平均）
        weights = {
            'literature_review': 0.3,  # 文献质量权重
            'experiment_design': 0.3,  # 实验设计权重
            'consistency': 0.2,        # 一致性权重
            'feasibility': 0.2         # 可行性权重
        }

        weighted_sum = 0
        total_weight = 0
        valid_scores = 0

        # 处理每个维度
        dim_data = [
            ('literature_review', lit_eval),
            ('experiment_design', exp_eval),
            ('consistency', consistency),
            ('feasibility', feasibility)
        ]

        for dim_name, dim_result in dim_data:
            if "score" in dim_result:
                score = dim_result["score"]
                weight = weights.get(dim_name, 0.25)  # 默认权重

                # 如果分数为0但该维度有非空建议，视为最低分1（避免0分过度拉低平均）
                if score == 0 and dim_result.get("suggestions"):
                    # 检查建议是否包含实际内容（不是空列表或占位符）
                    valid_suggestions = [s for s in dim_result.get("suggestions", [])
                                        if s and len(s.strip()) > 3 and s not in ["暂无具体改进建议", "评审失败，请重试"]]
                    if valid_suggestions:
                        score = 1.0  # 给予最低分而不是0分

                weighted_sum += score * weight
                total_weight += weight
                valid_scores += 1

        if total_weight > 0 and valid_scores > 0:
            evaluation["overall_score"] = weighted_sum / total_weight
            # 四舍五入到1位小数
            evaluation["overall_score"] = round(evaluation["overall_score"], 1)
        else:
            evaluation["overall_score"] = 0

        evaluation["passed"] = evaluation["overall_score"] >= 6.0 # 设定6分为及格线
        
        # 收集改进建议并去重
        all_suggestions = []
        seen_suggestions = set()
        for dim in evaluation["dimensions"].values():
            if dim.get("suggestions"):
                for suggestion in dim["suggestions"]:
                    # 标准化建议文本：去除首尾空格，合并连续空格
                    normalized = ' '.join(suggestion.strip().split())
                    if normalized and normalized not in seen_suggestions:
                        seen_suggestions.add(normalized)
                        all_suggestions.append(suggestion)  # 保留原始格式
        evaluation["suggestions"] = all_suggestions

        # 保障：确保dimensions包含所有必要的键
        required_keys = ['literature_review', 'experiment_design', 'consistency', 'feasibility']
        for key in required_keys:
            if key not in evaluation["dimensions"]:
                evaluation["dimensions"][key] = {"score": 0, "suggestions": []}

        return evaluation
    
    def _parse_critic_result(self, result: str, eval_type: str) -> dict:
        """解析评审结果"""
        import re

        # 清理文本：移除开头的工具调用描述和元信息
        cleaned_result = result

        # 只移除开头的工具调用描述（不删除文本中间的）
        tool_call_patterns = [
            r'^根据您的要求，我已经使用了\w+工具[，。:：\s]*',
            r'^我已经使用了\w+工具[，。:：\s]*',
            r'^使用\w+工具评估[，。:：\s]*',
            r'^调用\w+工具[，。:：\s]*',
            r'^工具调用:[，。:：\s]*',
            r'^工具调用结果:[，。:：\s]*',
            r'^正在使用\w+工具[，。:：\s]*',
            r'^开始评估[，。:：\s]*',
            r'^开始检查[，。:：\s]*',
        ]

        for pattern in tool_call_patterns:
            cleaned_result = re.sub(pattern, '', cleaned_result, flags=re.IGNORECASE)

        # 移除常见的错误信息前缀
        error_prefixes = [
            r'质量评估失败：',
            r'一致性检查失败：',
            r'可行性检查失败：',
            r'创新性评估失败：',
            r'评估失败：',
            r'检查失败：',
        ]

        for prefix in error_prefixes:
            if cleaned_result.startswith(prefix):
                cleaned_result = cleaned_result[len(prefix):]

        # 移除多余的空白字符
        cleaned_result = ' '.join(cleaned_result.split())

        # 如果清理后为空，使用原始结果
        if not cleaned_result.strip():
            cleaned_result = result

        parsed = {
            "score": 0,
            "dimension_scores": {},  # 新增：存储各维度评分
            "suggestions": [],
            "raw_result": cleaned_result[:500]  # 使用清理后的文本
        }

        # 1. 提取评分 - 使用多种策略
        score_found = False

        # 策略1：尝试特定格式的评分（基于评估类型）
        type_specific_patterns = {
            "quality": [
                # 各种括号格式
                r'【综合评分】\s*(\d+(?:\.\d+)?)/10',
                r'\[综合评分\]\s*(\d+(?:\.\d+)?)/10',
                # 各种标签格式
                r'综合评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'总分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'总体评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'整体评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'质量评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'文献质量评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'实验设计评分[：:]\s*(\d+(?:\.\d+)?)/10',
                # 带"分"后缀
                r'综合评分[：:]\s*(\d+(?:\.\d+)?)分',
                r'评分[：:]\s*(\d+(?:\.\d+)?)分',
                r'总分[：:]\s*(\d+(?:\.\d+)?)分',
                r'质量评分[：:]\s*(\d+(?:\.\d+)?)分',
                # 简化格式
                r'综合评分\s*[:：]?\s*(\d+(?:\.\d+?))(?:/10|分)?',
                r'评分\s*[:：]?\s*(\d+(?:\.\d+?))(?:/10|分)?',
                r'质量(?:评分)?\s*[:：]?\s*(\d+(?:\.\d+?))(?:/10|分)?',
                # 纯数字格式
                r'(\d+(?:\.\d+)?)/10',
                r'(\d+(?:\.\d+)?)分',
                # 英文格式
                r'Overall Score[:：]\s*(\d+(?:\.\d+)?)/10',
                r'Score[:：]\s*(\d+(?:\.\d+)?)/10',
                r'Quality Score[:：]\s*(\d+(?:\.\d+)?)/10',
            ],
            "consistency": [
                # 各种括号格式
                r'【一致性评分】\s*(\d+(?:\.\d+)?)/10',
                r'\[一致性评分\]\s*(\d+(?:\.\d+)?)/10',
                # 各种标签格式
                r'一致性评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'一致性[：:]\s*(\d+(?:\.\d+)?)/10',
                r'一致度[：:]\s*(\d+(?:\.\d+)?)/10',
                r'一致性分数[：:]\s*(\d+(?:\.\d+?))/10',
                r'一致性评估[：:]\s*(\d+(?:\.\d+?))/10',
                r'一致性检查[：:]\s*(\d+(?:\.\d+?))/10',
                # 带"分"后缀
                r'一致性评分[：:]\s*(\d+(?:\.\d+)?)分',
                r'一致性[：:]\s*(\d+(?:\.\d+)?)分',
                r'一致度[：:]\s*(\d+(?:\.\d+)?)分',
                # 简化格式
                r'一致性(?:评分)?\s*[:：]?\s*(\d+(?:\.\d+?))(?:/10|分)?',
                r'一致(?:性|度)(?:评分)?\s*[:：]?\s*(\d+(?:\.\d+?))(?:/10|分)?',
                # 纯数字格式（在一致性上下文中）
                r'一致性.*?(\d+(?:\.\d+)?)/10',
                r'一致性.*?(\d+(?:\.\d+)?)分',
                r'一致度.*?(\d+(?:\.\d+)?)/10',
                r'一致度.*?(\d+(?:\.\d+)?)分',
                # 英文格式
                r'Consistency Score[:：]\s*(\d+(?:\.\d+)?)/10',
                r'Consistency[:：]\s*(\d+(?:\.\d+)?)/10',
            ],
            "feasibility": [
                r'【可行性评分】\s*(\d+(?:\.\d+)?)/10',
                r'\[可行性评分\]\s*(\d+(?:\.\d+)?)/10',
                r'可行性评分[：:]\s*(\d+(?:\.\d+)?)/10',
                r'可行性[：:]\s*(\d+(?:\.\d+)?)/10',
                r'可行性评估[：:]\s*(\d+(?:\.\d+)?)/10',
                r'可行性检查[：:]\s*(\d+(?:\.\d+)?)/10',
                r'可行性评分[：:]\s*(\d+(?:\.\d+)?)分',
                r'可行性[：:]\s*(\d+(?:\.\d+)?)分',
                # 简化格式
                r'可行性(?:评分)?\s*[:：]?\s*(\d+(?:\.\d+?))(?:/10|分)?',
                r'可行(?:性)?(?:评分)?\s*[:：]?\s*(\d+(?:\.\d+?))(?:/10|分)?',
                # 英文格式
                r'Feasibility Score[:：]\s*(\d+(?:\.\d+)?)/10',
                r'Feasibility[:：]\s*(\d+(?:\.\d+)?)/10',
            ]
        }

        patterns = type_specific_patterns.get(eval_type, [
            r'【综合评分】\s*(\d+(?:\.\d+)?)/10',
            r'\[综合评分\]\s*(\d+(?:\.\d+)?)/10',
            r'综合评分[：:]\s*(\d+(?:\.\d+)?)/10',
            r'评分[：:]\s*(\d+(?:\.\d+)?)/10',
            r'质量评分[：:]\s*(\d+(?:\.\d+)?)/10',
            r'总分[：:]\s*(\d+(?:\.\d+)?)/10',
            r'总体评分[：:]\s*(\d+(?:\.\d+)?)/10',
            r'(\d+(?:\.\d+)?)/10',
            r'(\d+(?:\.\d+)?)分',
        ])

        for pattern in patterns:
            score_match = re.search(pattern, cleaned_result)
            if score_match:
                try:
                    score_text = score_match.group(1)
                    score = float(score_text)
                    if 0 <= score <= 10:
                        parsed["score"] = score
                        score_found = True
                        break
                except (ValueError, IndexError):
                    continue

        # 策略2：如果没有找到/10格式，尝试查找任何0-10之间的数字
        if not score_found:
            # 查找文本中任何看起来像评分的数字
            all_numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', cleaned_result)
            for num_str in all_numbers:
                try:
                    num = float(num_str)
                    # 检查是否是合理的评分（0-10之间）
                    if 0 <= num <= 10:
                        # 确保这个数字在评分上下文中出现
                        context_start = max(0, cleaned_result.find(num_str) - 30)
                        context_end = min(len(cleaned_result), cleaned_result.find(num_str) + len(num_str) + 30)
                        context = cleaned_result[context_start:context_end]

                        # 检查上下文是否包含评分相关词汇
                        score_keywords = ['评分', '分', 'score', 'point', '等级', '级别', 'rating', '星', '颗星']
                        # 放宽要求：如果数字在0-10之间，且附近有评分关键词，则接受
                        if any(keyword in context for keyword in score_keywords):
                            parsed["score"] = num
                            score_found = True
                            break
                except ValueError:
                    continue

        # 策略3：极度宽松模式 - 查找任何0-10之间的数字，优先选择更可能是评分的数字
        if not score_found:
            all_numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', cleaned_result)
            candidate_scores = []

            for num_str in all_numbers:
                try:
                    num = float(num_str)
                    # 检查是否是合理的评分（0-10之间）
                    if 0 <= num <= 10:
                        # 计算这个数字是评分的可能性分数
                        likelihood = 0

                        # 偏好4-8之间的整数（更可能是评分）
                        if 4 <= num <= 8:
                            likelihood += 3
                        elif 2 <= num <= 9:
                            likelihood += 2
                        else:
                            likelihood += 1

                        # 偏好整数或.5结尾的小数
                        if num == int(num):  # 整数
                            likelihood += 2
                        elif num_str.endswith('.5'):  # 半星评分常见
                            likelihood += 1

                        # 偏好出现在文本后半部分的数字（更可能是结论性评分）
                        num_position = cleaned_result.find(num_str) / max(1, len(cleaned_result))
                        if num_position > 0.5:  # 出现在后半部分
                            likelihood += 1

                        candidate_scores.append((num, likelihood, num_str))

                except ValueError:
                    continue

            # 按可能性排序，选择最可能的评分
            if candidate_scores:
                candidate_scores.sort(key=lambda x: x[1], reverse=True)  # 按可能性降序排序
                best_num, best_likelihood, best_str = candidate_scores[0]
                parsed["score"] = best_num
                score_found = True
                print(f"[CRITIC_INFO] 使用极度宽松模式为{eval_type}找到评分: {best_num} (可能性: {best_likelihood})")

        # 如果仍然没有找到评分，记录清理后文本的前100字符用于调试
        if not score_found and len(cleaned_result) > 0:
            # 只在无法解析评分时记录最小调试信息
            debug_snippet = cleaned_result[:100].replace('\n', ' ')
            if debug_snippet.strip():
                print(f"[CRITIC_WARN] 无法解析{eval_type}评分，清理后文本开头: {debug_snippet}...")

        # 2. 提取各维度评分（针对QualityEvaluatorTool）
        if eval_type == "quality":
            # 方法1：查找【各维度评分】或[各维度评分]部分
            dimensions_section = re.search(r'(?:【各维度评分】|\[各维度评分\])\s*(.*?)(?=【改进建议】|【总体评价】|$)', cleaned_result, re.DOTALL)
            if dimensions_section:
                dimensions_text = dimensions_section.group(1)
                # 提取各个维度的评分
                dimension_patterns = {
                    '科学严谨性': r'科学严谨性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '完整性': r'完整性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '创新性': r'创新性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '可操作性': r'可操作性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '表达清晰度': r'表达清晰度[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?'
                }

                for dim_name, pattern in dimension_patterns.items():
                    match = re.search(pattern, dimensions_text)
                    if match:
                        try:
                            dim_score = float(match.group(1))
                            if 0 <= dim_score <= 10:
                                parsed["dimension_scores"][dim_name] = dim_score
                        except (ValueError, IndexError):
                            pass
            else:
                # 方法2：在整个结果中搜索各维度评分（更宽松的匹配）
                dimension_patterns = {
                    '科学严谨性': r'科学严谨性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '完整性': r'完整性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '创新性': r'创新性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '可操作性': r'可操作性[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?',
                    '表达清晰度': r'表达清晰度[：:]\s*(\d+(?:\.\d+)?)(?:/10|分)?'
                }

                for dim_name, pattern in dimension_patterns.items():
                    match = re.search(pattern, cleaned_result)
                    if match:
                        try:
                            dim_score = float(match.group(1))
                            if 0 <= dim_score <= 10:
                                parsed["dimension_scores"][dim_name] = dim_score
                        except (ValueError, IndexError):
                            pass

            # 如果综合评分仍未找到，尝试从各维度评分的平均值计算
            if not score_found and parsed["dimension_scores"]:
                avg_score = sum(parsed["dimension_scores"].values()) / len(parsed["dimension_scores"])
                parsed["score"] = avg_score
                score_found = True

        # 3. 提取改进建议（根据评估类型使用不同的提取策略）
        suggestions_found = []

        # 元描述性文本模式（需要过滤掉）
        meta_descriptive_patterns = [
            # 评估描述性语句
            r'^评估结果显示',
            r'^根据分析',
            r'^总的来说',
            r'^综上所述',
            r'^本评估发现',
            r'^经过评估',
            r'^评估表明',
            r'^分析显示',
            r'^总体来说',
            r'^总体而言',
            r'^由此可见',
            r'^因此，',
            r'^所以，',
            r'^这表明',
            # 工具调用描述
            r'根据您的要求，我已经使用了\w+工具',
            r'我已经使用了\w+工具',
            r'使用\w+工具评估',
            r'调用\w+工具',
            r'工具调用:',
            r'工具调用结果:',
            r'正在使用\w+工具',
            r'开始评估',
            r'开始检查',
            # 通用元描述
            r'以下是我的评估',
            r'评估如下',
            r'检查如下',
            r'我的评估是',
            r'我的检查结果是',
            r'我认为',
            r'在我看来',
        ]

        if eval_type == "quality":
            # 质量评估：从建议部分提取（多种可能标题）
            suggestion_patterns = [
                r'【改进建议】\s*(.*?)(?=【总体评价】|$)',
                r'【优化建议】\s*(.*?)(?=【总体评价】|$)',
                r'【建议】\s*(.*?)(?=【总体评价】|$)',
                r'改进建议[：:]\s*(.*?)(?=【总体评价】|$)',
                r'优化建议[：:]\s*(.*?)(?=【总体评价】|$)',
                r'建议[：:]\s*(.*?)(?=【总体评价】|$)',
            ]

            suggestions_match = None
            for pattern in suggestion_patterns:
                suggestions_match = re.search(pattern, cleaned_result, re.DOTALL)
                if suggestions_match:
                    break

            if suggestions_match:
                suggestions_text = suggestions_match.group(1).strip()
                # 提取编号建议
                for line in suggestions_text.split('\n'):
                    line = line.strip()
                    if line:
                        line_match = re.match(r'^\s*(?:[0-9]+[\.\)、．]|[-•*])\s+(.+)$', line)
                        if line_match:
                            suggestion_text = line_match.group(1).strip()
                            if suggestion_text and len(suggestion_text) > 2:
                                # 过滤元描述性文本
                                is_meta = any(re.search(pattern, suggestion_text) for pattern in meta_descriptive_patterns)
                                if not is_meta:
                                    suggestions_found.append(suggestion_text)

        elif eval_type == "consistency":
            # 一致性检查：从建议部分提取（多种可能标题）
            suggestion_patterns = [
                r'【建议调整】\s*(.*?)(?=【|$)',
                r'【调整建议】\s*(.*?)(?=【|$)',
                r'【修改建议】\s*(.*?)(?=【|$)',
                r'【优化建议】\s*(.*?)(?=【|$)',
                r'建议调整[：:]\s*(.*?)(?=【|$)',
                r'调整建议[：:]\s*(.*?)(?=【|$)',
            ]

            suggestions_match = None
            for pattern in suggestion_patterns:
                suggestions_match = re.search(pattern, cleaned_result, re.DOTALL)
                if suggestions_match:
                    break

            if suggestions_match:
                suggestions_text = suggestions_match.group(1).strip()
                # 提取任何有意义的文本
                for line in suggestions_text.split('\n'):
                    line = line.strip()
                    if line and len(line) > 3:
                        # 过滤元描述性文本
                        is_meta = any(re.search(pattern, line) for pattern in meta_descriptive_patterns)
                        if not is_meta:
                            suggestions_found.append(line)

        elif eval_type == "feasibility":
            # 可行性检查：从建议部分提取（多种可能标题）
            suggestion_patterns = [
                r'【优化建议】\s*(.*?)(?=【|$)',
                r'【改进建议】\s*(.*?)(?=【|$)',
                r'【可行性建议】\s*(.*?)(?=【|$)',
                r'【实施建议】\s*(.*?)(?=【|$)',
                r'优化建议[：:]\s*(.*?)(?=【|$)',
                r'改进建议[：:]\s*(.*?)(?=【|$)',
            ]

            suggestions_match = None
            for pattern in suggestion_patterns:
                suggestions_match = re.search(pattern, cleaned_result, re.DOTALL)
                if suggestions_match:
                    break

            if suggestions_match:
                suggestions_text = suggestions_match.group(1).strip()
                # 提取任何有意义的文本
                for line in suggestions_text.split('\n'):
                    line = line.strip()
                    if line and len(line) > 3:
                        # 过滤元描述性文本
                        is_meta = any(re.search(pattern, line) for pattern in meta_descriptive_patterns)
                        if not is_meta:
                            suggestions_found.append(line)

        # 通用备选方案：如果没有找到特定部分的建议，提取任何建议性文本
        if not suggestions_found:
            suggestion_keywords = ['建议', '改进', '可以', '应该', '需要', '考虑', '加强', '提升', '优化', '调整', '优化']
            # 排除维度评分行
            excluded_patterns = [r'科学严谨性', r'完整性', r'创新性', r'可操作性', r'表达清晰度',
                                r'综合评分', r'各维度评分', r'一致性评分', r'可行性评分',
                                r'技术可行性', r'资源需求', r'潜在风险']

            sentences = re.split(r'[。！？；\n]', cleaned_result)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 5:
                    continue

                # 跳过包含排除模式的句子
                if any(re.search(pattern, sentence) for pattern in excluded_patterns):
                    continue

                # 过滤元描述性文本
                is_meta = any(re.search(pattern, sentence) for pattern in meta_descriptive_patterns)
                if is_meta:
                    continue

                if any(keyword in sentence for keyword in suggestion_keywords):
                    suggestions_found.append(sentence[:100])

        # 去重并限制数量
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions_found:
            if suggestion not in seen and len(suggestion) > 2:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)

        parsed["suggestions"] = unique_suggestions[:5]

        # 最终后备方案：如果仍然没有找到评分，根据建议内容推断
        if not score_found and eval_type in ["quality", "consistency", "feasibility"]:
            # 根据建议的质量和数量推断分数
            if not parsed["suggestions"] or len(parsed["suggestions"]) == 0:
                # 没有建议，可能是完全失败
                parsed["score"] = 0
            else:
                # 分析建议内容
                suggestion_count = len(parsed["suggestions"])

                # 检查建议是否具体（包含具体关键词）
                specific_keywords = ['增加', '完善', '详细', '具体', '明确', '补充', '扩展', '细化', '优化', '改进']
                generic_keywords = ['可以', '应该', '需要', '考虑', '加强', '提升']

                specific_suggestions = 0
                for suggestion in parsed["suggestions"]:
                    if any(keyword in suggestion for keyword in specific_keywords):
                        specific_suggestions += 1
                    elif any(keyword in suggestion for keyword in generic_keywords):
                        # 通用建议
                        pass

                # 计算推断分数
                if specific_suggestions > 0:
                    # 有具体建议，给予中等分数
                    if eval_type == "quality":
                        parsed["score"] = 5.0 + min(3.0, specific_suggestions * 0.5)
                    elif eval_type == "consistency":
                        parsed["score"] = 5.0 + min(3.0, specific_suggestions * 0.5)
                    else:  # feasibility
                        parsed["score"] = 5.0 + min(3.0, specific_suggestions * 0.5)
                elif suggestion_count > 0:
                    # 只有通用建议，给予较低分数
                    parsed["score"] = 3.0 + min(2.0, suggestion_count * 0.3)
                else:
                    # 有建议但无法分类
                    parsed["score"] = 4.0

                # 限制在0-10范围内
                parsed["score"] = max(0, min(10, parsed["score"]))
                print(f"[CRITIC_INFO] 使用后备方案为{eval_type}推断评分: {parsed['score']}")

        return parsed