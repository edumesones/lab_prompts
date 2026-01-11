"""
Simple script to run different LLMs dynamically
Usage: python run_llm.py --llm openai --prompt "your question"
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing providers
from llms.openai_llm import OpenAILLMProvider
from llms.claude import ClaudeLLMProvider
from llms.gemini import GeminiLLMProvider
from llms.huggingface import HuggingFaceLLMProvider


class SimpleLLMRunner:
    """Simple LLM executor"""

    def __init__(self):
        self.providers = {
            'openai': OpenAILLMProvider,
            'claude': ClaudeLLMProvider,
            'gemini': GeminiLLMProvider,
            'huggingface': HuggingFaceLLMProvider
        }

    def run(self, llm_name: str, prompt: str, system_prompt: str = None,
            enable_logging: bool = True, enable_evaluation: bool = False):
        """Execute a prompt on the specified LLM"""

        if llm_name not in self.providers:
            print(f"❌ LLM '{llm_name}' not available")
            print(f"Options: {', '.join(self.providers.keys())}")
            return None

        # Basic configuration per LLM
        configs = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model_name': 'gpt-4-turbo',
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation
            },
            'claude': {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'model_name': 'claude-sonnet-4-20250514',
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation
            },
            'gemini': {
                'api_key': os.getenv('GOOGLE_API_KEY'),
                'model_name': 'gemini-1.5-pro',
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation
            },
            'huggingface': {
                'token': os.getenv('HF_TOKEN'),
                'model_name': 'deepseek-ai/DeepSeek-R1:novita',
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation
            }
        }

        try:
            # Create provider instance
            provider_class = self.providers[llm_name]
            config = configs[llm_name]
            provider = provider_class(config)

            print(f"\n✅ Using: {llm_name} ({config.get('model_name', 'default model')})")
            print(f"📝 Executing prompt...\n")

            # Execute with logging
            response = provider.generate_with_logging(prompt, system_prompt=system_prompt)

            return response

        except Exception as e:
            print(f"❌ Error executing {llm_name}: {e}")
            return None

    def list_available(self):
        """List available LLMs"""
        print("\n📋 Available LLMs:")
        for name in self.providers.keys():
            print(f"  - {name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simple LLM executor")
    parser.add_argument('--llm', type=str, default='openai',
                       help='LLM to use (openai, claude, gemini, huggingface)')
    parser.add_argument('--prompt', type=str,
                       help='Prompt to execute')
    parser.add_argument('--prompt-file', type=str,
                       help='File with the prompt')
    parser.add_argument('--system', type=str,
                       help='System prompt (optional)')
    parser.add_argument('--list', action='store_true',
                       help='List available LLMs')
    parser.add_argument('--eval', action='store_true',
                       help='Enable RAGAS evaluation (coherence, relevance)')
    parser.add_argument('--no-log', action='store_true',
                       help='Disable automatic JSON logging')

    args = parser.parse_args()

    runner = SimpleLLMRunner()

    if args.list:
        runner.list_available()
        return

    # Get prompt
    prompt = args.prompt
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if prompt_path.exists():
            prompt = prompt_path.read_text(encoding='utf-8')
        else:
            print(f"❌ File not found: {args.prompt_file}")
            return

    if not prompt:
        print("❌ You must specify --prompt or --prompt-file")
        parser.print_help()
        return

    # Execute with logging configuration
    enable_logging = not args.no_log  # Logging on by default, unless --no-log
    enable_evaluation = args.eval  # Evaluation off by default, unless --eval

    response = runner.run(
        args.llm,
        prompt,
        args.system,
        enable_logging=enable_logging,
        enable_evaluation=enable_evaluation
    )

    if response:
        print("\n" + "="*60)
        print("RESPONSE:")
        print("="*60)
        print(response)
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
