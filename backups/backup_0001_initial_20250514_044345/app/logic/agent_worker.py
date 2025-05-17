# logic/agent_worker.py
from PySide6.QtCore import QObject, Signal
import asyncio

class AgentWorker(QObject):
    finished = Signal(object)
    start_task = Signal(str)
    status_update = Signal(str)
    intermediate_result = Signal(str)

    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.start_task.connect(self.run_agent_task)
        self._loop = None

        if hasattr(agent, "on_thinking_start"):
            agent.on_thinking_start = lambda: self.status_update.emit("Thinking... 🤔")
        if hasattr(agent, "on_thinking_end"):
            agent.on_thinking_end = lambda: self.status_update.emit("Planning next step... 📋")
        if hasattr(agent, "on_tool_start"):
            agent.on_tool_start = lambda tool_name: self.status_update.emit(f"Using tool: {tool_name} 🛠️")
        if hasattr(agent, "on_tool_end"):
            agent.on_tool_end = lambda tool_name: self.status_update.emit(f"Finished using {tool_name} ✅")

    def run_agent_task(self, prompt: str):
        try:
            self.status_update.emit("Starting task... 🚀")
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            result = self._loop.run_until_complete(self.agent.run(prompt))
            self.status_update.emit("Task completed! ✨")
            self.finished.emit(result)
        except Exception as e:
            print(f"Error in agent task: {e}")
            self.status_update.emit(f"Error: {e} ❌")
            self.finished.emit(f"Agent Error: {e}")

    def stop_loop(self):
        if self._loop and self._loop.is_running():
            self.status_update.emit("Stopping agent... 🛑")
            self._loop.call_soon_threadsafe(self._loop.stop)
