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

def get_model_from_env(env_var: str, default_model: str) -> str:
    """
    Read model name from environment variable with fallback to default.

    Args:
        env_var: Environment variable name (e.g., 'OPENAI_MODEL')
        default_model: Default model if env var not set

    Returns:
        Model name from env or default
    """
    model = os.getenv(env_var)
    if model:
        return model.strip()  # Clean whitespace
    return default_model

# Import existing providers
from llms.openai_llm import OpenAILLMProvider
from llms.claude import ClaudeProvider
from llms.gemini import GeminiProvider
from llms.huggingface import HuggingFaceProvider


class SimpleLLMRunner:
    """Simple LLM executor"""

    def __init__(self):
        self.providers = {
            'openai': OpenAILLMProvider,
            'claude': ClaudeProvider,
            'gemini': GeminiProvider,
            'huggingface': HuggingFaceProvider
        }

    def run(self, llm_name: str, prompt: str, system_prompt: str = None,
            enable_logging: bool = True, enable_evaluation: bool = False,
            context: str = None, ground_truth: str = None):
        """Execute a prompt on the specified LLM"""

        if llm_name not in self.providers:
            print(f"[ERROR] LLM '{llm_name}' not available")
            print(f"Options: {', '.join(self.providers.keys())}")
            return None

        # Basic configuration per LLM
        configs = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model_name': get_model_from_env('OPENAI_MODEL', 'gpt-4-turbo'),
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation,
                'eval_context': context,
                'eval_ground_truth': ground_truth
            },
            'claude': {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'model_name': get_model_from_env('CLAUDE_MODEL', 'claude-sonnet-4-20250514'),
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation,
                'eval_context': context,
                'eval_ground_truth': ground_truth
            },
            'gemini': {
                'api_key': os.getenv('GOOGLE_API_KEY'),
                'model_name': get_model_from_env('GEMINI_MODEL', 'gemini-1.5-pro'),
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation,
                'eval_context': context,
                'eval_ground_truth': ground_truth
            },
            'huggingface': {
                'token': os.getenv('HF_TOKEN'),
                'model_name': get_model_from_env('HUGGINGFACE_MODEL', 'deepseek-ai/DeepSeek-R1:novita'),
                'enable_logging': enable_logging,
                'enable_evaluation': enable_evaluation,
                'eval_context': context,
                'eval_ground_truth': ground_truth
            }
        }

        try:
            # Create provider instance
            provider_class = self.providers[llm_name]
            config = configs[llm_name]
            provider = provider_class(config)

            print(f"\n[OK] Using: {llm_name} ({config.get('model_name', 'default model')})")
            print(f"[*] Executing prompt...\n")

            # Execute with logging
            response = provider.generate_with_logging(prompt, system_prompt=system_prompt)

            return response

        except Exception as e:
            print(f"[ERROR] Error executing {llm_name}: {e}")
            return None

    def list_available(self):
        """List available LLMs"""
        print("\n[INFO] Available LLMs:")
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
    parser.add_argument('--context', type=str,
                       help='Context for evaluation (enables faithfulness metric)')
    parser.add_argument('--context-file', type=str,
                       help='File containing context for evaluation')
    parser.add_argument('--ground-truth', type=str,
                       help='Ground truth answer for evaluation (enables answer_correctness)')
    parser.add_argument('--ground-truth-file', type=str,
                       help='File containing ground truth answer for evaluation')
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
            print(f"[ERROR] File not found: {args.prompt_file}")
            return

    if not prompt:
        print("[ERROR] You must specify --prompt or --prompt-file")
        parser.print_help()
        return

    # Get context (for evaluation)
    context = args.context
    if args.context_file:
        context_path = Path(args.context_file)
        if context_path.exists():
            context = context_path.read_text(encoding='utf-8')
        else:
            print(f"[ERROR] Context file not found: {args.context_file}")
            return

    # Get ground truth (for evaluation)
    ground_truth = args.ground_truth
    if args.ground_truth_file:
        gt_path = Path(args.ground_truth_file)
        if gt_path.exists():
            ground_truth = gt_path.read_text(encoding='utf-8')
        else:
            print(f"[ERROR] Ground truth file not found: {args.ground_truth_file}")
            return

    # Execute with logging configuration
    enable_logging = not args.no_log  # Logging on by default, unless --no-log
    enable_evaluation = args.eval  # Evaluation off by default, unless --eval

    response = runner.run(
        args.llm,
        prompt,
        args.system,
        enable_logging=enable_logging,
        enable_evaluation=enable_evaluation,
        context=context,
        ground_truth=ground_truth
    )

    if response:
        print("\n" + "="*60)
        print("RESPONSE:")
        print("="*60)
        print(response)
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
