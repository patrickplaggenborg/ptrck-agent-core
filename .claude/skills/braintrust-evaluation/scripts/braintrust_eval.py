#!/usr/bin/env python3
"""
Braintrust Evaluation Tool
Run Braintrust evaluations locally using the braintrust CLI
"""

import os
import sys
import argparse
import subprocess
from typing import List, Optional

def run_eval(
    files: List[str],
    watch: bool = False,
    filters: Optional[List[str]] = None,
    list_only: bool = False,
    jsonl: bool = False,
    no_send_logs: bool = False,
    no_progress_bars: bool = False,
    terminate_on_failure: bool = False,
    env_file: Optional[str] = None,
    num_workers: Optional[int] = None,
    verbose: int = 0,
    api_key: Optional[str] = None,
    org_name: Optional[str] = None,
    dev: bool = False,
    dev_host: Optional[str] = None,
    dev_port: Optional[int] = None,
    dev_org_name: Optional[str] = None
) -> None:
    """Run Braintrust evaluations"""

    cmd = ["braintrust", "eval"]

    # Add verbosity
    if verbose > 0:
        cmd.append("-" + "v" * verbose)

    # Add API key if provided
    if api_key:
        cmd.extend(["--api-key", api_key])

    # Add org name if provided
    if org_name:
        cmd.extend(["--org-name", org_name])

    # Add watch flag
    if watch:
        cmd.append("--watch")

    # Add filters
    if filters:
        for filter_str in filters:
            cmd.extend(["--filter", filter_str])

    # Add list flag
    if list_only:
        cmd.append("--list")

    # Add jsonl flag
    if jsonl:
        cmd.append("--jsonl")

    # Add no-send-logs flag
    if no_send_logs:
        cmd.append("--no-send-logs")

    # Add no-progress-bars flag
    if no_progress_bars:
        cmd.append("--no-progress-bars")

    # Add terminate-on-failure flag
    if terminate_on_failure:
        cmd.append("--terminate-on-failure")

    # Add env file
    if env_file:
        cmd.extend(["--env-file", env_file])

    # Add num workers
    if num_workers:
        cmd.extend(["--num-workers", str(num_workers)])

    # Add dev mode flags
    if dev:
        cmd.append("--dev")
        if dev_host:
            cmd.extend(["--dev-host", dev_host])
        if dev_port:
            cmd.extend(["--dev-port", str(dev_port)])
        if dev_org_name:
            cmd.extend(["--dev-org-name", dev_org_name])

    # Add files
    cmd.extend(files)

    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: braintrust CLI not found. Please install it with: pip install braintrust", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running evaluation: {e}", file=sys.stderr)
        sys.exit(1)

def push_code(
    file: str,
    if_exists: str = "error",
    requirements: Optional[str] = None,
    verbose: int = 0,
    api_key: Optional[str] = None,
    org_name: Optional[str] = None
) -> None:
    """Push code to Braintrust"""

    cmd = ["braintrust", "push"]

    # Add verbosity
    if verbose > 0:
        cmd.append("-" + "v" * verbose)

    # Add API key if provided
    if api_key:
        cmd.extend(["--api-key", api_key])

    # Add org name if provided
    if org_name:
        cmd.extend(["--org-name", org_name])

    # Add if-exists behavior
    cmd.extend(["--if-exists", if_exists])

    # Add requirements file
    if requirements:
        cmd.extend(["--requirements", requirements])

    # Add file
    cmd.append(file)

    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: braintrust CLI not found. Please install it with: pip install braintrust", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error pushing code: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run Braintrust evaluations and push code")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Eval command
    eval_parser = subparsers.add_parser("eval", help="Run evaluations")
    eval_parser.add_argument("files", nargs="*", help="Files or directories to evaluate")
    eval_parser.add_argument("--watch", action="store_true", help="Watch files for changes")
    eval_parser.add_argument("--filter", action="append", dest="filters", help="Filter evaluators (can be used multiple times)")
    eval_parser.add_argument("--list", action="store_true", dest="list_only", help="List evaluators without running")
    eval_parser.add_argument("--jsonl", action="store_true", help="Format output as JSONL")
    eval_parser.add_argument("--no-send-logs", action="store_true", help="Don't send logs to Braintrust")
    eval_parser.add_argument("--no-progress-bars", action="store_true", help="Don't show progress bars")
    eval_parser.add_argument("--terminate-on-failure", action="store_true", help="Terminate on failing eval")
    eval_parser.add_argument("--env-file", help="Path to .env file")
    eval_parser.add_argument("--num-workers", type=int, help="Number of worker threads")
    eval_parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity")
    eval_parser.add_argument("--api-key", help="Braintrust API key")
    eval_parser.add_argument("--org-name", help="Organization name")
    eval_parser.add_argument("--dev", action="store_true", help="Run in dev mode")
    eval_parser.add_argument("--dev-host", help="Dev server host")
    eval_parser.add_argument("--dev-port", type=int, help="Dev server port")
    eval_parser.add_argument("--dev-org-name", help="Dev org name")

    # Push command
    push_parser = subparsers.add_parser("push", help="Push code to Braintrust")
    push_parser.add_argument("file", help="File to push")
    push_parser.add_argument("--if-exists", choices=["error", "replace", "ignore"], default="error", help="What to do if function already exists")
    push_parser.add_argument("--requirements", help="Requirements file for dependencies")
    push_parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity")
    push_parser.add_argument("--api-key", help="Braintrust API key")
    push_parser.add_argument("--org-name", help="Organization name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "eval":
            run_eval(
                files=args.files if args.files else ["."],
                watch=args.watch,
                filters=args.filters,
                list_only=args.list_only,
                jsonl=args.jsonl,
                no_send_logs=args.no_send_logs,
                no_progress_bars=args.no_progress_bars,
                terminate_on_failure=args.terminate_on_failure,
                env_file=args.env_file,
                num_workers=args.num_workers,
                verbose=args.verbose,
                api_key=args.api_key,
                org_name=args.org_name,
                dev=args.dev,
                dev_host=args.dev_host,
                dev_port=args.dev_port,
                dev_org_name=args.dev_org_name
            )
        elif args.command == "push":
            push_code(
                file=args.file,
                if_exists=args.if_exists,
                requirements=args.requirements,
                verbose=args.verbose,
                api_key=args.api_key,
                org_name=args.org_name
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
