#!/usr/bin/env python3
"""
First Chord Brain - CLI

Usage:
    python3 brain.py onboard "Student Name"
    python3 brain.py lookup "Ryan Ofee"
    python3 brain.py lookup sdt_2grxJL
    python3 brain.py lookup cus_R7DL79Smc0cwBE
"""

import sys
from src.onboarding import OnboardingWorkflow
from rich.console import Console

console = Console()

def main():
    if len(sys.argv) < 2:
        console.print("[bold]First Chord Brain[/bold]")
        console.print("[yellow]Commands:[/yellow]")
        console.print("  onboard \"Student Name\"  — run WGCS onboarding flow")
        console.print("  lookup  <name or ID>    — look up any person, student, or tutor")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "onboard":
        # Name is optional — if omitted, the waiting-list picker will handle it
        student_name = sys.argv[2] if len(sys.argv) >= 3 else ""
        workflow = OnboardingWorkflow()
        workflow.start(student_name)

    elif command == "lookup":
        if len(sys.argv) < 3:
            console.print("[red]Error:[/red] Please provide a name or ID to look up")
            console.print("[yellow]Usage:[/yellow] python3 brain.py lookup \"Ryan Ofee\"")
            sys.exit(1)

        from lookup import lookup, _print_result
        query = " ".join(sys.argv[2:])
        results = lookup(query)
        if not results:
            console.print(f"[yellow]No results found for:[/yellow] {query!r}")
            sys.exit(0)
        print(f"\nFound {len(results)} result(s) for: {query!r}")
        for r in results:
            _print_result(r)

    else:
        console.print(f"[red]Unknown command:[/red] {command}")
        console.print("[yellow]Available commands:[/yellow] onboard, lookup")
        sys.exit(1)

if __name__ == "__main__":
    main()
