import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(__file__))

from app.services.llm_service import LLMService, create_llm_service


class LLMServiceOllamaTest(unittest.TestCase):
    def test_default_service_uses_ollama_qwen_endpoint(self):
        service = LLMService()

        self.assertEqual(service.provider, 'ollama')
        self.assertEqual(service.model, 'qwen2.5:7b')
        self.assertEqual(service._get_ollama_generate_url(), 'http://192.168.31.245:11434/api/generate')

    @patch.dict(os.environ, {'LLM_API_BASE': 'https://dashscope.aliyuncs.com/compatible-mode/v1'})
    def test_ollama_ignores_openai_compatible_base(self):
        service = LLMService(provider='ollama')

        self.assertEqual(service._get_ollama_generate_url(), 'http://192.168.31.245:11434/api/generate')

    @patch('app.services.llm_service.requests.post')
    def test_ollama_generate_payload_and_response(self, post):
        response = Mock()
        response.json.return_value = {
            'model': 'qwen2.5:7b',
            'response': '生成成功',
            'prompt_eval_count': 3,
            'eval_count': 5,
        }
        response.raise_for_status.return_value = None
        post.return_value = response

        service = LLMService()
        result = service.generate('系统提示', '用户问题', temperature=0.2, max_tokens=128)

        post.assert_called_once()
        url = post.call_args.args[0]
        payload = post.call_args.kwargs['json']
        self.assertEqual(url, 'http://192.168.31.245:11434/api/generate')
        self.assertEqual(payload['model'], 'qwen2.5:7b')
        self.assertEqual(payload['stream'], False)
        self.assertIn('系统提示', payload['prompt'])
        self.assertIn('用户问题', payload['prompt'])
        self.assertEqual(payload['options']['temperature'], 0.2)
        self.assertEqual(payload['options']['num_predict'], 128)
        self.assertEqual(result['content'], '生成成功')
        self.assertEqual(result['usage']['total_tokens'], 8)
        self.assertEqual(result['status'], 'success')

    def test_factory_defaults_to_ollama(self):
        service = create_llm_service()

        self.assertEqual(service.provider, 'ollama')
        self.assertEqual(service.model, 'qwen2.5:7b')


if __name__ == '__main__':
    unittest.main()
