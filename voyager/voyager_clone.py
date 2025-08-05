import copy
import pdb
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents.action import ActionAgent
from agents.curriculum import CurriculumAgent
from agents.critic import CriticAgent
import voyager.utils as U
from skill_manager.ts_skill_manager import TypeScriptSkillManager
from voyager.surfpool_env import SurfpoolEnv
from voyager.utils.progress_tracker import ProgressTracker

load_dotenv()

DEFAULT_MODEL_NAME = "x-ai/grok-3-mini"
# DEFAULT_MODEL_NAME = "gpt-4o-mini"
# DEFAULT_MODEL_NAME = "gpt-4-0613"
# DEFAULT_MODEL_NAME = "claude-3-5-sonnet-20240620"

class VoyagerClone:
    def __init__(
            self,
            action_agent_task_max_retries=3,
            max_iterations=150,
            action_agent_model_name=DEFAULT_MODEL_NAME,
            curriculum_agent_model_name=DEFAULT_MODEL_NAME,
            curriculum_agent_temperature=0,
            curriculum_agent_qa_model_name=DEFAULT_MODEL_NAME,
            curriculum_agent_qa_temperature=0,
            skill_manager_retrieval_top_k=5,
            curriculum_agent_mode="auto",
            curriculum_agent_warm_up=None,
            critic_agent_model_name=DEFAULT_MODEL_NAME,
            critic_agent_temperature=0,
            openai_api_request_timeout=120,
            critic_agent_mode="auto",
            skill_library_dir=None,
            skill_manager_model_name=DEFAULT_MODEL_NAME,
            skill_manager_temperature=0,
            resume: bool = False
        ):
        self.env = SurfpoolEnv()
        if not os.environ['OPENAI_API_KEY']:
            raise ValueError("OPENAI_API_KEY is not set")

        self.run_id = datetime.now().strftime("%y-%m-%d") + "_" + str(int(datetime.now().timestamp()))
        ckpt_dir = f"./ckpt/{self.run_id}"
        os.makedirs(ckpt_dir, exist_ok=True)

        self.max_iterations = max_iterations

        # self.model = "x-ai/grok-3-mini"
        self.action_agent = ActionAgent(
            model_name=action_agent_model_name,
            ckpt_dir=ckpt_dir,
        )
        self.action_agent_task_max_retries = action_agent_task_max_retries
        self.curriculum_agent = CurriculumAgent(
            model_name=curriculum_agent_model_name,
            temperature=curriculum_agent_temperature,
            qa_model_name=curriculum_agent_qa_model_name,
            qa_temperature=curriculum_agent_qa_temperature,
            request_timeout=openai_api_request_timeout,
            ckpt_dir=ckpt_dir,
            resume=resume,
            mode=curriculum_agent_mode,
            warm_up=curriculum_agent_warm_up,
        )
        self.critic_agent = CriticAgent(
            model_name=critic_agent_model_name,
            temperature=critic_agent_temperature,
            request_timeout=openai_api_request_timeout,
            mode=critic_agent_mode,
        )
        self.skill_manager = TypeScriptSkillManager(
            model_name=skill_manager_model_name,
            temperature=skill_manager_temperature,
            retrieval_top_k=skill_manager_retrieval_top_k,
            request_timeout=openai_api_request_timeout,
            ckpt_dir=skill_library_dir if skill_library_dir else ckpt_dir,
            resume=True if resume or skill_library_dir else False,
        )
        self.recorder = U.EventRecorder(ckpt_dir=ckpt_dir, resume=resume)
        self.progress_tracker = ProgressTracker(ckpt_dir=ckpt_dir, resume=resume)
        self.resume = resume

        # init variables for ollout
        self.action_agent_rollout_num_iter = -1
        self.task = None
        self.context = ""
        self.messages = None
        self.conversations = []
        self.last_events = []

    async def reset(self, task, context="", reset_env=True):
        self.action_agent_rollout_num_iter = 0
        self.task = task
        self.context = context
        if reset_env:
            await self.env.reset()
        obs = await self.env._get_observation()
        events = [("observe", obs)]
        skills = self.skill_manager.retrieve_skills(query=self.context)
        logging.info(
            f"\033[33mRender Action Agent system message with {len(skills)} skills\033[0m"
        )
        system_message = self.action_agent.render_system_message(skills=skills)
        human_message = self.action_agent.render_human_message(
            events=events, code="", task=self.task, context=context, critique=""
        )
        self.messages =[system_message, human_message]
        logging.info(
            f"\033[32m****Action Agent human message****\n{human_message.content}\033[0m"
        )
        assert len(self.messages) == 2
        self.conversations = []
        return self.messages

    async def step(self):
        if self.action_agent_rollout_num_iter < 0:
            raise ValueError("Agent must be reset before stepping")
        ai_message = self.action_agent.llm.invoke(self.messages)
        logging.info(f"\033[34m****Action Agent ai message****\n{ai_message.content}\033[0m")
        
        # Track action agent message
        self.progress_tracker.record_agent_message(
            "action_agent", 
            "response", 
            ai_message.content,
            self.task
        )
        
        self.conversations.append(
            (self.messages[0].content, self.messages[1].content, ai_message.content)
        )
        parsed_result = self.action_agent.process_ai_message(message=ai_message)
        success = False
        reward = 0
        critique = ""
        error_msg = None
        
        if isinstance(parsed_result, dict):
            code = parsed_result["program_code"] + '\n' + parsed_result["exec_code"]
            events, reward, terminated, truncated, info = await self.env.step2(
                code,
                programs=self.skill_manager.programs,
                skill_manager=self.skill_manager,
            )
            self.recorder.record(events, self.task)
            
            # Get observation for tracking
            obs_event = next((e for e in reversed(events) if e[0] == "observe"), None)
            current_obs = obs_event[1] if obs_event else {}
            
            # Check for errors in info
            if "error" in info:
                error_msg = info["error"]
            
            success, critique = self.critic_agent.check_task_success(
                events=events,
                task=self.task,
                context=self.context,
                max_retries=5,
            )
            
            # Track critic agent message
            self.progress_tracker.record_agent_message(
                "critic_agent",
                "critique",
                critique,
                self.task
            )
            
            new_skills = self.skill_manager.retrieve_skills(
                query=self.context
                + "\n\n"
                + self.action_agent.summarize_chatlog(events)
            )
            system_message = self.action_agent.render_system_message(skills=new_skills)
            human_message = self.action_agent.render_human_message(
                events=events,
                code=parsed_result["program_code"],
                task=self.task,
                context=self.context,
                critique=critique,
            )
            self.last_events = copy.deepcopy(events)
            self.messages = [system_message, human_message]
        else:
            assert isinstance(parsed_result, str)
            self.recorder.record([], self.task)
            critique = f"Failed to parse code: {parsed_result}"
            logging.info(f"\033[34m{parsed_result} Trying again!\033[0m")
            # Update last_events even on parsing failures to maintain observation state
            self.last_events = [("observe", parsed_result)]
            
        assert len(self.messages) == 2
        self.action_agent_rollout_num_iter += 1
        done = (
            self.action_agent_rollout_num_iter >= self.action_agent_task_max_retries
            or success
        )
        info = {
            "task": self.task,
            "success": success,
            "conversations": self.conversations,
        }
        if success:
            assert(
                "program_code" in parsed_result and "program_name" in parsed_result
            ), "program andprogram_name must be returned when success"
            info["program_code"] = parsed_result["program_code"]
            info["program_name"] = parsed_result["program_name"]
        else:
            logging.info(
                f"\033[32m****Action Agent human message****\n{self.messages[-1].content}\033[0m"
            )
        return self.messages, reward, done, info

    async def rollout(self, *, task, context, reset_env=True):
        # pdb.set_trace()
        await self.reset(task=task, context=context, reset_env=reset_env)
        while True:
            messages, reward, done, info = await self.step()
            if done:
                break
        return messages, reward, done, info

    async def learn(self, reset_env=True):
        # todo(ngundotra): add resume logic (maybe keep keypair in ckpt)
        self.last_events, _ = await self.env.reset()
        while True:
            if self.recorder.iteration > self.max_iterations:
                logging.info("Iteration limit reached")
                break
            task, context = self.curriculum_agent.propose_next_task(
                events=self.last_events,
                max_retries=5
            )
            
            # Track curriculum agent decision
            self.progress_tracker.record_agent_message(
                "curriculum_agent",
                "proposed_task",
                f"Task: {task}\nContext: {context}",
                task
            )
            
            logging.info(
                f"\033[35mStarting task {task} for at most {self.action_agent_task_max_retries} times\033[0m"
            )
            # try: 
            messages, reward, done, info = await self.rollout(
                task=task,
                context=context,
                reset_env=reset_env
            )
            # except Exception as e:
            #     # pdb.set_trace()
            #     # time.sleep(3)
            #     info = {
            #         "task": task,
            #         "success": False
            #     }
            #     self.last_events, _ = await self.env.reset()
            #     logging.info("Your last round rollout terminated due to an error:")
            #     logging.info(
            #         f"\033[41m{e}\033[0m"
            #     )

            if info['success']:
                self.skill_manager.add_new_skill(info)
            
            self.curriculum_agent.update_exploration_progress(info)
            
            # Get current observation for tracking from the most recent events
            # This contains the updated discovered_programs count after the transaction
            obs_event = next((e for e in reversed(self.last_events) if e[0] == "observe"), None)
            current_obs = obs_event[1] if obs_event else {}
            
            # Handle double-wrapped observation
            if isinstance(current_obs, list) and len(current_obs) > 0 and current_obs[0][0] == "observe":
                current_obs = current_obs[0][1]
            
            # Track iteration progress
            self.progress_tracker.record_iteration(
                task=task,
                success=info['success'],
                reward=reward,
                observation=current_obs,
                error=info.get('error'),
                critique=info.get('critique'),
                completed_tasks=self.curriculum_agent.completed_tasks
            )
            
            logging.info(
                f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m"
            )
            logging.info(
                f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m"
            )
        
        # Export summary report at the end
        self.progress_tracker.export_summary_report()
        
        return {
            "completed_tasks": self.curriculum_agent.completed_tasks,
            "failed_tasks": self.curriculum_agent.failed_tasks,
            "skills": self.skill_manager.skills,
        }

    async def decompose_task(self, task: str):
        if not self.last_events:
            self.last_events, _ = await self.env.reset()
        return self.curriculum_agent.decompose_task(task, self.last_events)

    async def inference(self, task=None, sub_goals=[], reset_env=True):
        if not task and not sub_goals:
            raise ValueError("Either task or sub_goals must be provided")
        if not sub_goals:
            sub_goals = await self.decompose_task(task)
        self.curriculum_agent.completed_tasks = []
        self.curriculum_agent.failed_tasks = []
        self.last_events, _ = await self.env.reset()
        while self.curriculum_agent.progress < len(sub_goals):
            next_task = sub_goals[self.curriculum_agent.progress]
            context = self.curriculum_agent.get_task_context(next_task)
            logging.info(
                f"\033[35mStarting task {next_task} for at most {self.action_agent_task_max_retries} times\033[0m"
            )
            messags, reward, done, info = await self.rollout(
                task=next_task,
                context=context,
                reset_env=reset_env,
            )
            self.curriculum_agent.update_exploration_progress(info)
            logging.info(
                f"\033[35mCompleted {self.curriculum_agent.progress} out of {len(sub_goals)} tasks\033[0m"
            )
            logging.info(
                f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m"
            )


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    voyager = VoyagerClone()
    # voyager.reset()
    # voyager.decompose_task("Create a new token")
    # voyager.inference()
    # voyager.step()
    # voyager.rollout()
    asyncio.run(voyager.learn())