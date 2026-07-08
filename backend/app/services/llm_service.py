"""LLM服务 - 支持千问(Qwen)、ChatGLM、DeepSeek等国产开源大模型"""
import os
import json
import logging
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务 - 封装国产大语言模型调用，兼容OpenAI API格式"""

    def __init__(self, api_base=None, api_key=None, model=None, provider=None):
        self.provider = provider or os.environ.get('LLM_PROVIDER', 'ollama')
        if self.provider == 'ollama':
            self.api_base = api_base or os.environ.get('OLLAMA_API_BASE', 'http://192.168.31.245:11434')
            self.api_key = ''
            self.model = model or os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b')
        else:
            self.api_base = api_base or os.environ.get('LLM_API_BASE',
                                                        'https://dashscope.aliyuncs.com/compatible-mode/v1')
            self.api_key = api_key or os.environ.get('LLM_API_KEY', '') or os.environ.get('DASHSCOPE_API_KEY', '')
            self.model = model or os.environ.get('LLM_MODEL', 'qwen-plus')

    def _get_ollama_generate_url(self):
        api_base = self.api_base.rstrip('/')
        if api_base.endswith('/api/generate'):
            return api_base
        return f"{api_base}/api/generate"

    def _get_client(self):
        """获取OpenAI兼容客户端"""
        import openai
        return openai.OpenAI(api_key=self.api_key, base_url=self.api_base)

    def generate(self, system_prompt: str, user_prompt: str,
                 temperature: float = 0.7, max_tokens: int = 4000) -> Dict:
        """调用LLM生成内容（兼容OpenAI API格式，支持千问/ChatGLM/DeepSeek等）"""
        try:
            if self.provider == 'ollama':
                return self._generate_ollama(system_prompt, user_prompt, temperature, max_tokens)

            client = self._get_client()

            # 根据不同提供商调整参数
            kwargs = {
                'model': self.model,
                'messages': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                'temperature': temperature,
            }

            # 不同模型的参数适配
            if self.provider == 'qwen':
                # 千问系列: qwen-plus, qwen-turbo, qwen-max, qwen-long
                kwargs['max_tokens'] = max_tokens
                kwargs['top_p'] = 0.8
            elif self.provider == 'deepseek':
                # DeepSeek系列
                kwargs['max_tokens'] = max_tokens
                kwargs['top_p'] = 0.9
            elif self.provider == 'chatglm':
                # ChatGLM系列
                kwargs['max_tokens'] = max_tokens
            elif self.provider == 'local':
                # 本地部署模型(vLLM/Ollama)
                kwargs['max_tokens'] = max_tokens
            else:
                kwargs['max_tokens'] = max_tokens

            response = client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content
            return {
                'content': content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0)
                },
                'provider': self.provider,
                'status': 'success'
            }
        except ImportError:
            logger.warning("openai库未安装，使用模拟生成")
            return self._mock_generate(system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"LLM调用失败[{self.provider}/{self.model}]: {str(e)}")
            return {'content': '', 'status': 'error', 'error': str(e)}

    def _generate_ollama(self, system_prompt: str, user_prompt: str,
                         temperature: float = 0.7, max_tokens: int = 4000) -> Dict:
        prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}".strip()
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens,
            }
        }

        response = requests.post(self._get_ollama_generate_url(), json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()

        return {
            'content': data.get('response', ''),
            'model': data.get('model', self.model),
            'usage': {
                'prompt_tokens': data.get('prompt_eval_count', 0),
                'completion_tokens': data.get('eval_count', 0),
                'total_tokens': data.get('prompt_eval_count', 0) + data.get('eval_count', 0)
            },
            'provider': self.provider,
            'status': 'success'
        }

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
            'provider': 'mock',
            'status': 'mock'
        }


class QwenService(LLMService):
    """千问(Qwen)服务 - 通过DashScope API或本地vLLM部署"""

    def __init__(self, model='qwen-plus', api_key=None, local=False, **kwargs):
        if local:
            # 本地vLLM部署
            api_base = f"http://{os.environ.get('LOCAL_LLM_HOST', 'localhost')}:{os.environ.get('LOCAL_LLM_PORT', '8000')}/v1"
            model = os.environ.get('LOCAL_LLM_MODEL', 'Qwen2.5-14B-Instruct')
            api_key = 'not-needed'
        else:
            # DashScope API
            api_base = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            api_key = api_key or os.environ.get('DASHSCOPE_API_KEY', '')

        super().__init__(api_base=api_base, api_key=api_key, model=model, provider='qwen')


class DeepSeekService(LLMService):
    """DeepSeek服务"""

    def __init__(self, model='deepseek-chat', api_key=None, **kwargs):
        api_base = 'https://api.deepseek.com/v1'
        api_key = api_key or os.environ.get('DEEPSEEK_API_KEY', '')
        super().__init__(api_base=api_base, api_key=api_key, model=model, provider='deepseek')


class ChatGLMService(LLMService):
    """ChatGLM服务 - 通过本地vLLM部署"""

    def __init__(self, model='THUDM/glm-4-9b-chat', **kwargs):
        api_base = f"http://{os.environ.get('LOCAL_LLM_HOST', 'localhost')}:{os.environ.get('LOCAL_LLM_PORT', '8000')}/v1"
        api_key = 'not-needed'
        super().__init__(api_base=api_base, api_key=api_key, model=model, provider='chatglm')


class LocalLLMService(LLMService):
    """本地部署LLM服务 - 通过vLLM/Ollama等框架部署，兼容OpenAI API格式"""

    def __init__(self, model=None, host=None, port=None, **kwargs):
        host = host or os.environ.get('LOCAL_LLM_HOST', 'localhost')
        port = port or os.environ.get('LOCAL_LLM_PORT', '8000')
        model = model or os.environ.get('LOCAL_LLM_MODEL', 'Qwen2.5-14B-Instruct')
        api_base = f"http://{host}:{port}/v1"
        super().__init__(api_base=api_base, api_key='not-needed', model=model, provider='local')


class OllamaService(LLMService):
    """Ollama local model service."""

    def __init__(self, model=None, host=None, port=None, api_base=None, **kwargs):
        host = host or os.environ.get('LOCAL_LLM_HOST', '192.168.31.245')
        port = port or os.environ.get('LOCAL_LLM_PORT', '11434')
        model = model or os.environ.get('OLLAMA_MODEL', 'qwen2.5:7b')
        api_base = api_base or os.environ.get('OLLAMA_API_BASE', f"http://{host}:{port}")
        super().__init__(api_base=api_base, api_key='', model=model, provider='ollama')


def create_llm_service(provider=None, **kwargs) -> LLMService:
    """工厂方法 - 根据配置创建对应的LLM服务"""
    provider = provider or 'ollama'

    services = {
        'qwen': QwenService,
        'deepseek': DeepSeekService,
        'chatglm': ChatGLMService,
        'local': LocalLLMService,
        'ollama': OllamaService,
    }

    service_class = services.get(provider, LLMService)
    return service_class(**kwargs)
