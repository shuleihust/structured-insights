#!/usr/bin/env python3
"""
文案结构化提炼工具
从文案中提取思维模型、方法论和语言风格，生成 Lisp 格式的智能体函数
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class ContentExtractor:
    """文案结构化提取器"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化提取器"""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.client = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(__file__).parent / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        
        handlers = []
        if log_config.get('console', True):
            handlers.append(logging.StreamHandler())
        if log_config.get('file'):
            log_file = Path(__file__).parent / log_config['file']
            handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger(__name__)
    
    def _init_llm_client(self, provider: Optional[str] = None):
        """初始化 LLM 客户端"""
        if provider is None:
            provider = self.config['llm']['provider']
        
        if provider == 'openai':
            return self._init_openai_client()
        elif provider == 'anthropic':
            return self._init_anthropic_client()
        elif provider == 'deepseek':
            return self._init_deepseek_client()
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")
    
    def _init_openai_client(self):
        """初始化 OpenAI 客户端"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai 库: pip install openai")
        
        api_key_env = self.config['llm'].get('api_key_env', 'OPENAI_API_KEY')
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"未设置环境变量: {api_key_env}")
        
        return OpenAI(api_key=api_key)
    
    def _init_anthropic_client(self):
        """初始化 Anthropic 客户端"""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("请安装 anthropic 库: pip install anthropic")
        
        provider_config = self.config['llm']['alternative_providers']['anthropic']
        api_key_env = provider_config.get('api_key_env', 'ANTHROPIC_API_KEY')
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"未设置环境变量: {api_key_env}")
        
        return Anthropic(api_key=api_key)
    
    def _init_deepseek_client(self):
        """初始化 DeepSeek 客户端"""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai 库: pip install openai")
        
        provider_config = self.config['llm']['alternative_providers']['deepseek']
        api_key_env = provider_config.get('api_key_env', 'DEEPSEEK_API_KEY')
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"未设置环境变量: {api_key_env}")
        
        base_url = provider_config.get('base_url')
        return OpenAI(api_key=api_key, base_url=base_url)
    
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        template_path = Path(__file__).parent / self.config['extraction']['prompt_template']
        if not template_path.exists():
            raise FileNotFoundError(f"提示词模板不存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _read_input_content(self, input_source: Optional[str]) -> str:
        """读取输入文案"""
        if input_source is None or input_source == '-':
            # 从标准输入读取
            self.logger.info("从标准输入读取文案...")
            content = sys.stdin.read()
        else:
            # 从文件读取
            input_file = Path(input_source)
            if not input_file.exists():
                raise FileNotFoundError(f"输入文件不存在: {input_file}")
            
            self.logger.info(f"从文件读取文案: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # 验证内容长度
        min_length = self.config['extraction'].get('min_content_length', 100)
        if len(content.strip()) < min_length:
            raise ValueError(f"文案内容过短（少于 {min_length} 字符）")
        
        return content.strip()
    
    def _call_llm(self, prompt: str, provider: Optional[str] = None) -> str:
        """调用 LLM API"""
        if provider is None:
            provider = self.config['llm']['provider']
        
        self.logger.info(f"调用 {provider} API...")
        
        if provider == 'anthropic':
            return self._call_anthropic(prompt)
        else:
            return self._call_openai_compatible(prompt, provider)
    
    def _call_anthropic(self, prompt: str) -> str:
        """调用 Anthropic API"""
        if self.client is None:
            self.client = self._init_llm_client('anthropic')
        
        provider_config = self.config['llm']['alternative_providers']['anthropic']
        
        response = self.client.messages.create(
            model=provider_config['model'],
            max_tokens=provider_config['max_tokens'],
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _call_openai_compatible(self, prompt: str, provider: str) -> str:
        """调用 OpenAI 兼容的 API"""
        if self.client is None:
            self.client = self._init_llm_client(provider)
        
        if provider == 'openai':
            model = self.config['llm']['model']
            max_tokens = self.config['llm']['max_tokens']
            temperature = self.config['llm'].get('temperature', 0.7)
        else:
            provider_config = self.config['llm']['alternative_providers'][provider]
            model = provider_config['model']
            max_tokens = provider_config['max_tokens']
            temperature = provider_config.get('temperature', 0.7)
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def _extract_lisp_code(self, response: str) -> str:
        """从响应中提取 Lisp 代码"""
        # 尝试提取代码块
        if "```lisp" in response:
            start = response.find("```lisp") + 7
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()
        
        # 如果没有代码块标记，返回整个响应
        return response.strip()
    
    def _save_output(self, content: str, output_path: Optional[str] = None) -> str:
        """保存输出结果"""
        output_config = self.config['output']
        
        if output_path is None:
            # 生成默认输出路径
            output_dir = Path(__file__).parent / output_config['directory']
            output_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = output_config['filename_prefix']
            suffix = output_config['filename_suffix']
            filename = f"{prefix}_{timestamp}{suffix}"
            output_path = output_dir / filename
        else:
            output_path = Path(output_path)
        
        # 检查是否覆盖
        if output_path.exists() and not output_config.get('overwrite', False):
            raise FileExistsError(f"输出文件已存在: {output_path}，使用 --overwrite 强制覆盖")
        
        # 保存文件
        with open(output_path, 'w', encoding=output_config['encoding']) as f:
            f.write(content)
        
        self.logger.info(f"结果已保存到: {output_path}")
        return str(output_path)
    
    def extract(self, 
                input_source: Optional[str] = None,
                output_path: Optional[str] = None,
                provider: Optional[str] = None) -> str:
        """
        执行提取流程
        
        Args:
            input_source: 输入文件路径，None 或 '-' 表示从标准输入读取
            output_path: 输出文件路径，None 表示自动生成
            provider: LLM 提供商，None 表示使用配置文件中的默认值
        
        Returns:
            输出文件路径
        """
        try:
            # 1. 读取输入内容
            content = self._read_input_content(input_source)
            self.logger.info(f"成功读取文案，长度: {len(content)} 字符")
            
            # 2. 加载提示词模板
            template = self._load_prompt_template()
            
            # 3. 构造完整提示词
            prompt = template.replace("{{INPUT_CONTENT}}", content)
            
            # 4. 调用 LLM
            response = self._call_llm(prompt, provider)
            self.logger.info("成功获取 LLM 响应")
            
            # 5. 提取 Lisp 代码
            lisp_code = self._extract_lisp_code(response)
            
            # 6. 保存结果
            output_file = self._save_output(lisp_code, output_path)
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"提取失败: {str(e)}")
            raise


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='文案结构化提炼工具 - 将文案转换为 Lisp 格式的智能体函数',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 从文件提取
  python extractor.py -i input.txt -o output.lisp
  
  # 从标准输入提取
  cat input.txt | python extractor.py -o output.lisp
  
  # 使用不同的 LLM 提供商
  python extractor.py -i input.txt --provider anthropic
  
  # 使用自定义配置文件
  python extractor.py -i input.txt --config my_config.json
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        help='输入文件路径（不指定或使用 - 表示从标准输入读取）',
        default=None
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出文件路径（不指定则自动生成）',
        default=None
    )
    
    parser.add_argument(
        '-c', '--config',
        help='配置文件路径（默认: config.json）',
        default='config.json'
    )
    
    parser.add_argument(
        '-p', '--provider',
        help='LLM 提供商（openai/anthropic/deepseek，默认使用配置文件中的设置）',
        choices=['openai', 'anthropic', 'deepseek'],
        default=None
    )
    
    parser.add_argument(
        '--overwrite',
        help='如果输出文件已存在，强制覆盖',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建提取器
        extractor = ContentExtractor(config_path=args.config)
        
        # 如果设置了 overwrite 标志，更新配置
        if args.overwrite:
            extractor.config['output']['overwrite'] = True
        
        # 执行提取
        output_file = extractor.extract(
            input_source=args.input,
            output_path=args.output,
            provider=args.provider
        )
        
        print(f"\n✅ 提取成功！")
        print(f"📄 输出文件: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

