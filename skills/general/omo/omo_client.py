#!/usr/bin/env python3
"""
Omo CLI Client

Wrapper para Omo CLI - Agente de desarrollo.
"""

import os
import sys
import subprocess
from typing import Dict, Optional
from dataclasses import dataclass

SKILLS_DIR = os.path.dirname(__file__)
CLAWD_DIR = os.path.dirname(SKILLS_DIR)
if CLAWD_DIR not in sys.path:
    sys.path.insert(0, CLAWD_DIR)


@dataclass
class OmoResult:
    success: bool
    output: str
    error: Optional[str] = None


class OmoCLI:
    """Cliente para Omo CLI."""
    
    def __init__(self, sandbox: bool = True, cwd: str = None):
        self.sandbox = sandbox
        self.cwd = cwd or os.getcwd()
    
    def _run(self, args, input_text=None):
        cmd = ["omo"] + args
        return subprocess.run(
            cmd, input=input_text, capture_output=True, text=True, cwd=self.cwd
        )
    
    def run(self, task: str, sandbox: bool = None) -> OmoResult:
        """Ejecutar tarea."""
        sandbox = sandbox if sandbox is not None else self.sandbox
        args = ["run", "--task", task]
        if sandbox:
            args.append("--sandbox")
        
        result = self._run(args)
        return OmoResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr if result.returncode != 0 else None
        )
    
    def run_file(self, filepath: str) -> OmoResult:
        """Ejecutar desde archivo."""
        with open(filepath, 'r') as f:
            task = f.read()
        return self.run(task)
    
    def interactive(self):
        """Modo interactivo."""
        subprocess.run(["omo", "interactive"])
    
    def status(self) -> Dict:
        result = subprocess.run(["omo", "status"], capture_output=True, text=True)
        return {"output": result.stdout.strip(), "error": result.stderr}


def omo_run(task: str, sandbox: bool = True):
    cli = OmoCLI(sandbox=sandbox)
    result = cli.run(task)
    print(result.output)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Omo CLI")
    parser.add_argument("task", help="Task")
    parser.add_argument("--sandbox", action="store_true", default=True)
    args = parser.parse_args()
    omo_run(args.task, args.sandbox)
