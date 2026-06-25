"""LLM服务 - 调用大语言模型生成文档内容"""
import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务 - 封装大语言模型调用"""

    def __init__(self, api_base=None, api_key=None, model=None):
        self.api_base = api_base or os.environ.get('LLM_API_BASE', 'https://api.openai.com/v1')
        self.api_key = api_key or os.environ.get('LLM_API_KEY', '')
        self.model = model or os.environ.get('LLM_MODEL', 'gpt-4')

    def generate(self, system_prompt: str, user_prompt: str,
                 temperature: float = 0.7, max_tokens: int = 4000) -> Dict:
        """调用LLM生成内容"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.api_base)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content
            return {
                'content': content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'status': 'success'
            }
        except ImportError:
            logger.warning("openai库未安装，使用模拟生成")
            return self._mock_generate(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            return {'content': '', 'status': 'error', 'error': str(e)}

    def generate_with_context(self, system_prompt: str, user_prompt: str,
                              context: str = '', temperature: float = 0.7) -> Dict:
        """带上下文的生成"""
        if context:
            full_prompt = f"""参考以下上下文信息：
---
{context}
---

基于以上信息，{user_prompt}"""
        else:
            full_prompt = user_prompt

        return self.generate(system_prompt, full_prompt, temperature)

    def generate_chapter(self, doc_type: str, chapter_number: str, chapter_title: str,
                         context: str = '', project_info: Dict = None) -> Dict:
        """生成438C文档章节内容"""
        from app.config.standard_documents import STANDARD_438C_DOCUMENTS
        from app.config.prompt_templates import PROMPT_TEMPLATES, DEFAULT_SYSTEM_PROMPT, DEFAULT_CHAPTER_PROMPT

        # 获取文档类型配置
        doc_config = STANDARD_438C_DOCUMENTS.get(doc_type, {})

        # 获取提示词模板
        template = PROMPT_TEMPLATES.get(doc_type, {})
        system_prompt = template.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
        chapter_prompts = template.get('chapter_prompts', {})

        # 构建用户提示词
        user_prompt = chapter_prompts.get(chapter_number,
                                          DEFAULT_CHAPTER_PROMPT.format(chapter_title=chapter_title))

        # 添加项目信息
        if project_info:
            user_prompt += f"\n\n项目信息：\n- 系统名称：{project_info.get('system_name', '')}\n"
            user_prompt += f"- 系统版本：{project_info.get('system_version', '')}\n"
            user_prompt += f"- 编制单位：{project_info.get('organization', '')}"

        return self.generate_with_context(system_prompt, user_prompt, context)

    def generate_from_code(self, code_content: str, language: str,
                           doc_type: str, project_info: Dict = None) -> Dict:
        """从代码生成文档"""
        system_prompt = f"""你是一位精通{language}语言和GJB 438C规范的资深软件工程师。
你需要根据提供的{language}源代码，按照438C标准生成对应的文档内容。
要求：
1. 准确理解代码的功能和逻辑
2. 按照军标格式组织文档内容
3. 提取代码中的关键信息（类、函数、接口、数据结构等）
4. 使用规范的技术术语"""

        user_prompt = f"""请分析以下{language}源代码，并生成{doc_type}类型文档的相关内容：

```{language}
{code_content}
```

请按照438C标准格式组织内容，包括功能描述、接口说明、数据结构等。"""

        if project_info:
            user_prompt += f"\n\n项目信息：\n- 系统名称：{project_info.get('system_name', '')}\n"
            user_prompt += f"- 系统版本：{project_info.get('system_version', '')}"

        return self.generate(system_prompt, user_prompt, temperature=0.5)

    def answer_question(self, question: str, context: str = '',
                        knowledge_base_id: int = None) -> Dict:
        """智能问答"""
        system_prompt = """你是一位专业的技术文档助手，精通GJB 438C军用软件文档编制规范。
请基于提供的上下文信息回答用户的问题。如果上下文中没有相关信息，请明确说明。
回答应当准确、完整、专业。"""

        return self.generate_with_context(system_prompt, question, context)

    def _mock_generate(self, system_prompt: str, user_prompt: str) -> Dict:
        """模拟生成（开发环境使用）"""
        content = f"""[模拟生成内容]

基于系统提示和用户请求，以下是生成的文档内容：

{user_prompt}

注意：当前为模拟生成模式，请配置LLM API以获取实际生成内容。"""

        return {
            'content': content,
            'model': 'mock',
            'usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
            'status': 'mock'
        }
