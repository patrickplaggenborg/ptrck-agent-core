#!/usr/bin/env python3
"""
Braintrust Launch Experiment Tool
Launches experiments on the Braintrust platform using the /v1/eval API endpoint
Waits for completion and returns full results (synchronous execution)
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any

API_BASE_URL = "https://api.braintrust.dev"

def load_env():
    """Load environment variables from .env file if it exists"""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value

def get_api_key() -> str:
    """Get the Braintrust API key from environment"""
    load_env()
    api_key = os.environ.get("BRAINTRUST_API_KEY")
    if not api_key:
        raise ValueError("BRAINTRUST_API_KEY environment variable not set")
    return api_key

def launch_eval(
    project_id: str,
    prompt_id: str,
    dataset_id: str,
    experiment_name: str,
    scorer_type: str = "Factuality",
    field_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Launch an evaluation on the Braintrust platform using the /v1/eval API

    Args:
        project_id: Braintrust project ID
        prompt_id: Braintrust prompt ID to evaluate
        dataset_id: Braintrust dataset ID to use for evaluation
        experiment_name: Name for the experiment
        scorer_type: Type of scorer to use (default: "Factuality" from autoevals)
        field_name: Optional field name for custom field-specific scoring

    Returns:
        Dictionary containing experiment results and URLs
    """
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Build the request payload
    payload = {
        "project_id": project_id,
        "data": {
            "dataset_id": dataset_id
        },
        "task": {
            "function_id": prompt_id
        },
        "scores": [
            {
                # If scorer_type looks like a UUID, treat it as a function_id
                # Otherwise treat it as a global_function name (e.g., "Factuality")
                "function_id" if len(scorer_type) == 36 and scorer_type.count('-') == 4
                else "global_function": scorer_type
            }
        ],
        "experiment_name": experiment_name,
        "stream": False  # Wait for completion
    }

    # If custom field scoring is requested, we'd need a custom scorer function
    # For now, using global autoevals scorers

    try:
        print(f"Launching experiment on Braintrust platform...")
        print(f"  Project ID: {project_id}")
        print(f"  Prompt ID: {prompt_id}")
        print(f"  Dataset ID: {dataset_id}")
        print(f"  Experiment: {experiment_name}")
        print(f"  Scorer ID: {scorer_type}")
        print()
        print("Waiting for experiment to complete (this may take 1-5 minutes)...")
        print()

        response = requests.post(
            f"{API_BASE_URL}/v1/eval",
            headers=headers,
            json=payload
        )

        response.raise_for_status()
        result = response.json()

        return result

    except requests.exceptions.RequestException as e:
        print(f"Error launching evaluation: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)

def format_results(result: Dict[str, Any], project_id: str, experiment_name: str, scorer: str) -> None:
    """Format and print experiment completion results"""
    print()
    print("="*70)
    print("EXPERIMENT COMPLETED SUCCESSFULLY")
    print("="*70)
    print()
    print(f"Experiment Name: {experiment_name}")
    print(f"Project ID: {project_id}")
    print(f"Scorer ID: {scorer}")
    print()

    # Extract experiment ID if available
    experiment_id = result.get('experiment_id')
    if experiment_id:
        print(f"Experiment ID: {experiment_id}")
        print()

    # Extract scores if available
    scores = result.get('scores', {})
    if scores:
        print("Results:")
        for score_name, score_data in scores.items():
            score_value = score_data.get('score', 0)
            print(f"  - {score_name}: {score_value:.4f}")
        print()

    # Show URLs if available
    experiment_url = result.get('experiment_url')
    if experiment_url:
        print(f"View in Braintrust: {experiment_url}")
        print()

    print("="*70)
    print()

def main():
    parser = argparse.ArgumentParser(
        description="Launch a Braintrust experiment on the platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch experiment with Factuality scorer
  python3 launch_experiment.py \\
    --project-id 5956ce58-88ac-42f7-88ce-c2be352de28c \\
    --prompt-id d3599976-c611-48e4-9b57-0763c6e52fb5 \\
    --dataset-id 913d0e08-fdb3-4154-96db-23eb90d3d032 \\
    --experiment-name "Duration Baseline"

  # Launch with different scorer
  python3 launch_experiment.py \\
    --project-id PROJECT_ID \\
    --prompt-id PROMPT_ID \\
    --dataset-id DATASET_ID \\
    --experiment-name "My Test" \\
    --scorer ExactMatch
        """
    )

    parser.add_argument("--project-id", required=True,
                       help="Braintrust project ID")
    parser.add_argument("--prompt-id", required=True,
                       help="Braintrust prompt ID (task function)")
    parser.add_argument("--dataset-id", required=True,
                       help="Braintrust dataset ID")
    parser.add_argument("--experiment-name", required=True,
                       help="Name for the experiment")
    parser.add_argument("--scorer", default="Factuality",
                       help="Scorer to use (default: Factuality). Options: Factuality, ExactMatch, Levenshtein, etc.")
    parser.add_argument("--field-name",
                       help="Field name for custom field-specific scoring (future enhancement)")
    parser.add_argument("--json", action="store_true",
                       help="Output raw JSON response")

    args = parser.parse_args()

    try:
        # Launch the evaluation
        result = launch_eval(
            project_id=args.project_id,
            prompt_id=args.prompt_id,
            dataset_id=args.dataset_id,
            experiment_name=args.experiment_name,
            scorer_type=args.scorer,
            field_name=args.field_name
        )

        # Output results
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            format_results(result, args.project_id, args.experiment_name, args.scorer)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
