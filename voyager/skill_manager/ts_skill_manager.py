import logging
import pdb
import subprocess
import json
import os
from typing import Any, Dict, List

import voyager.utils as U
from voyager.prompts import load_prompt
from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
# from langchain_openrouter
from langchain.schema import SystemMessage, HumanMessage

class TypeScriptSkillManager:
    def __init__(
        self, 
        model_name,
        temperature=0,
        retrieval_top_k=5,
        request_timeout=120,
        ckpt_dir="ckpt",
        resume=False
    ):
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            model=model_name,
            temperature=temperature,
            request_timeout=request_timeout,
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        U.f_mkdir(f"{ckpt_dir}/skill/code")
        U.f_mkdir(f"{ckpt_dir}/skill/description")
        # todo(ngundotra): add programs for env execution
        if resume:
            logging.info(
               f"\033[33mLoading Skill Manager from {ckpt_dir}/skill\033[0m" 
            )
            self.skills = U.load_json(f"{ckpt_dir}/skill/skills.json")
        else:
            self.skills = {}
        self.retrieval_top_k = retrieval_top_k
        self.ckpt_dir = ckpt_dir        

    # ================================
    # Code Loop

    def run_code_loop_code(self, code: str, agent_pubkey: str, latest_blockhash: str, code_file: str = "code_loop_code.ts"):
        with open(code_file, "w") as f:
            f.write(code)
        command = ["bun", "voyager/skill_runner/runSkill.ts", code_file, "4000", agent_pubkey, latest_blockhash]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            # runSkill.ts now outputs a JSON object with serialized_tx
            return json.loads(result.stdout.strip("\n"))
        except subprocess.CalledProcessError as e:
            # When there's an error, runSkill.ts prints JSON to stdout and error details to stderr
            try:
                # Try to parse the JSON output from stdout (this has the structured error info)
                if e.stdout:
                    error_data = json.loads(e.stdout.strip("\n"))
                    # Also capture stderr for full error details
                    if e.stderr:
                        error_data['stderr'] = e.stderr
                    return error_data
                elif e.stderr:
                    # Fallback if only stderr is available
                    return {"success": False, "reason": f"Skill runner error", "stderr": e.stderr}
            except json.JSONDecodeError:
                # Fallback for unexpected output
                return {
                    "success": False, 
                    "reason": "Skill runner error",
                    "stdout": e.stdout if e.stdout else "",
                    "stderr": e.stderr if e.stderr else ""
                }
        except FileNotFoundError:
            return {"success": False, "reason": "Bun command not found. Make sure Bun is installed and in your PATH."}


    # ================================

    @property
    def programs(self):
        programs = []
        for skill_name, entry in self.skills.items():
            # Debug logging
            if isinstance(entry, dict) and 'code' in entry:
                logging.info(f"Adding skill {skill_name} with code length: {len(entry['code'])}")
                programs.append(entry['code'])
            else:
                logging.warning(f"Skill {skill_name} has unexpected format: {type(entry)}")
        # todo(ngundotra): add primitives
        logging.info(f"Total programs length: {len(programs)}, first 200 chars: {programs[:200]}")
        return programs

    def evaluate_code(self, code: str, programs: List[str], agent_pubkey: str, timeout_ms: int):
        import base64
        encoded_code = base64.b64encode(code.encode("utf-8")).decode("utf-8")

        # Need to add a dummy program to the list to make it non-empty
        if not programs:
            programs = ['console.log();']

        encoded_programs = base64.b64encode("\n".join(programs).encode("utf-8")).decode("utf-8")
        command = [
            "bun", "voyager/skill_runner/runCode.ts", 
            encoded_code, 
            encoded_programs, 
            agent_pubkey,
            str(timeout_ms),
        ]
        logging.info(f"Running code with command: {command}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            return {
                'success': True,
                'serialized_tx': json.loads(result.stdout.strip("\n"))["serialized_tx"],
                'stdout': result.stdout.strip("\n"),
                'stderr': result.stderr.strip("\n"),
            }
        except subprocess.CalledProcessError as e:
            # Try to parse JSON error from stdout first (where runCode.ts outputs errors)
            if e.stdout:
                try:
                    error_json = json.loads(e.stdout.strip("\n"))
                    return {
                        "success": False,
                        "reason": error_json.get("error", "Unknown error"),
                        "trace": error_json.get("trace", ""),
                        'stdout': e.stdout.strip("\n") if e.stdout else "",
                        'stderr': e.stderr.strip("\n") if e.stderr else "",
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback to stderr
            return {
                "success": False, 
                "reason": f"Skill runner error: {e.stderr}", 
                'stdout': e.stdout.strip("\n") if e.stdout else "",
                'stderr': e.stderr.strip("\n") if e.stderr else "",
            }
        except FileNotFoundError:
            return {"success": False, "reason": "Bun command not found. Make sure Bun is installed and in your PATH."}


    # ================================
    # OLD CODE

    def get_skills(self) -> Dict[str, str]:
        return self.skills

    def _load_existing_skills(self):
        for filename in sorted(os.listdir(self.skills_dir)):
            if filename.endswith(".ts"):
                skill_id = self.next_skill_id
                self.skills[skill_id] = os.path.join(self.skills_dir, filename)
                self.next_skill_id += 1
    
    def register(self, skill_name: str, code: str) -> int:
        skill_id = self.next_skill_id
        file_path = os.path.join(self.skills_dir, f"skill_{skill_id}.ts")
        with open(file_path, "w") as f:
            f.write(code)
        self.skills[skill_name] = file_path
        self.next_skill_id += 1
        return skill_name

    def __len__(self):
        return len(self.skills)

    def get_skill_docs(self) -> Dict[str, str]:
        # For TypeScript skills, we might not have docstrings in the same way as Python.
        # For now, return the file paths as "docs".
        return {str(k): v for k, v in self.skills.items()}

    def save_skill(self, name: str, code: str) -> str:
        file_path = os.path.join(self.skills_dir, f"{name}.ts")
        with open(file_path, "w") as f:
            f.write(code)
        return file_path

    def execute_skill(self, file_path: str, timeout_ms: int = 10000, agent_pubkey: str = None, latest_blockhash: str = None) -> Dict[str, Any]:
        command = ["bun", "voyager/skill_runner/runSkill.ts", file_path, str(timeout_ms)]
        if agent_pubkey:
            command.append(agent_pubkey)
        if latest_blockhash:
            command.append(latest_blockhash)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            # runSkill.ts now outputs a JSON object with serialized_tx
            return json.loads(result.stdout.strip("\n"))
        except subprocess.CalledProcessError as e:
            # When there's an error, runSkill.ts prints JSON to stdout and error details to stderr
            try:
                # Try to parse the JSON output from stdout (this has the structured error info)
                if e.stdout:
                    error_data = json.loads(e.stdout.strip("\n"))
                    # Also capture stderr for full error details
                    if e.stderr:
                        error_data['stderr'] = e.stderr
                    return error_data
                elif e.stderr:
                    # Fallback if only stderr is available
                    return {"success": False, "reason": f"Skill runner error", "stderr": e.stderr}
            except json.JSONDecodeError:
                # Fallback for unexpected output
                return {
                    "success": False, 
                    "reason": "Skill runner error",
                    "stdout": e.stdout if e.stdout else "",
                    "stderr": e.stderr if e.stderr else ""
                }
        except FileNotFoundError:
            return {"success": False, "reason": "Bun command not found. Make sure Bun is installed and in your PATH."}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    skill_manager = TypeScriptSkillManager(
        model_name="gpt-4o-mini",
        temperature=0.0,
        retrieval_top_k=5,
        request_timeout=120,
        ckpt_dir="test_ckpt",
        resume=False,
    )
    result = skill_manager.evaluate_code(
        "console.log('hello');",
        programs=[],
        agent_pubkey="fake",
        timeout_ms=10000,
    )
    assert not result['success'], f"Skill runner succeeded: {result}"
    result = skill_manager.evaluate_code(
"""
const kp = web3.Keypair.generate(); 
const tx = new web3.Transaction(); 
tx.add(web3.SystemProgram.transfer({
    fromPubkey: kp.publicKey,
    toPubkey: kp.publicKey,
    lamports: 100000,
}));
tx.recentBlockhash = "4vJ9JU1bJJE96FWSJKvHsmmFADCg4gpZQff4P3bkLKi";
tx.feePayer = kp.publicKey; tx.sign(kp); 
return tx.serialize().toString('base64');
""",
        programs=[],
        agent_pubkey="fake",
        timeout_ms=10000,
    )
    assert result['success'], f"Skill runner failed: {result}"

