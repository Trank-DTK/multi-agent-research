# 数据分析服务
import pandas as pd
import numpy as np
import json
from django.core.files.storage import default_storage
from .models import Dataset, AnalysisResult, DataVisualization

class DataAnalysisService:
    """数据分析服务"""
    
    @staticmethod
    def load_dataframe(file_path):
        """加载数据文件为DataFrame"""
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("不支持的文件格式，请上传CSV或Excel文件")
        return df
    
    @staticmethod
    def save_dataset(user, file, name=None, description=''):
        """保存数据集"""
        # 保存文件到磁盘
        file_path = default_storage.save(f'datasets/{user.id}/{file.name}', file)
        full_path = default_storage.path(file_path)
        
        # 读取数据
        df = DataAnalysisService.load_dataframe(full_path)
        
        # 创建数据集记录
        dataset = Dataset.objects.create(
            user=user,
            name=name or file.name,
            description=description,
            file=file_path,
            file_name=file.name,
            file_size=file.size,
            row_count=len(df),
            column_count=len(df.columns)
        )
        
        # 保存列信息到缓存或额外表
        dataset._columns = list(df.columns)
        dataset._dtypes = df.dtypes.astype(str).to_dict()
        
        return dataset, df
    
    @staticmethod
    def descriptive_statistics(df, columns=None):
        """描述性统计"""
        if columns:
            df = df[columns]   #只分析指定的列
        
        stats = df.describe().to_dict()   #统计值
        
        # 添加缺失值信息
        missing = df.isnull().sum().to_dict()
        
        # 添加数据类型
        dtypes = df.dtypes.astype(str).to_dict()
        
        return {
            'statistics': stats,
            'missing_values': missing,
            'data_types': dtypes,
            'row_count': len(df),
            'column_count': len(df.columns)
        }
    
    @staticmethod
    def correlation_analysis(df, columns=None):
        """相关性分析"""
        if columns:
            df = df[columns]
        
        # 只选择数值列
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {'error': '没有数值列可用于相关性分析'}
        
        correlation = numeric_df.corr().to_dict()
        
        # 找出强相关对（r的绝对值>0.7）
        strong_correlations = []
        for i, col1 in enumerate(numeric_df.columns):
            for j, col2 in enumerate(numeric_df.columns):
                if i < j:
                    corr_val = numeric_df[col1].corr(numeric_df[col2])
                    if abs(corr_val) > 0.7:
                        strong_correlations.append({
                            'col1': col1,
                            'col2': col2,
                            'correlation': corr_val,
                            'strength': '强正相关' if corr_val > 0 else '强负相关'
                        })
        
        return {
            'correlation_matrix': correlation,
            'strong_correlations': strong_correlations,
            'numeric_columns': list(numeric_df.columns)
        }
    
    @staticmethod
    def generate_insight(df, stats, correlation, llm=None):
        """生成AI洞察"""
        insight_prompt = f"""
请根据以下数据分析结果，生成简洁的数据洞察报告：

数据集信息：
- 行数：{stats['row_count']}
- 列数：{stats['column_count']}

描述性统计摘要：
{json.dumps(stats['statistics'], ensure_ascii=False)[:1000]}

相关性分析：
{json.dumps(correlation.get('strong_correlations', []), ensure_ascii=False)[:500]}

请输出：
1. 数据概览（1-2句话）
2. 关键发现（3-5点）
3. 建议（2-3点）
"""
        
        if llm:
            try:
                insight = llm.invoke(insight_prompt)
                return insight
            except:
                return DataAnalysisService._default_insight(stats, correlation)
        else:
            return DataAnalysisService._default_insight(stats, correlation)
    
    @staticmethod
    def _default_insight(stats, correlation):
        """默认洞察"""
        insight = f"数据集包含{stats['row_count']}行{stats['column_count']}列数据。"
        
        if correlation.get('strong_correlations'):
            insight += f"发现{len(correlation['strong_correlations'])}对强相关关系。"
        
        return insight
    
    @staticmethod
    def prepare_chart_data(df, chart_type, x_column, y_column=None):
        """准备图表数据"""
        if chart_type == 'line' or chart_type == 'bar':
            if y_column:
                data = {
                    'x': df[x_column].tolist(),
                    'y': df[y_column].tolist()
                }
            else:
                # 单变量统计
                value_counts = df[x_column].value_counts()
                data = {
                    'x': value_counts.index.tolist(),
                    'y': value_counts.values.tolist()
                }
        
        elif chart_type == 'scatter':
            data = {
                'x': df[x_column].tolist(),
                'y': df[y_column].tolist() if y_column else []
            }
        
        elif chart_type == 'histogram':
            data = {
                'values': df[x_column].dropna().tolist(),
                'bins': 20
            }
        
        else:
            data = {}
        
        return data