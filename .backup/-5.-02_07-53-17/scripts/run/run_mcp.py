#!/usr/bin/env python
import argparse
import asyncio
import sys

from app.agent.mcp import MCPAgent
from app.agent.reasoning import ReasoningAgent
from app.config import config
from app.logger import logger


class MCPRunner:
    """Runner class for MCP Agent with proper path handling and configuration."""

    def __init__(self, agent_type="reasoning"):
        """
        Инициализирует runner для MCP агента.

        Args:
            agent_type: Тип агента для использования ("mcp" или "reasoning")
        """
        self.root_path = config.root_path
        self.server_reference = config.mcp_config.server_reference

        # Создаем нужный тип агента
        if agent_type.lower() == "reasoning":
            logger.info("Using ReasoningAgent with Serena and Sequential Thinking capabilities")
            self.agent = ReasoningAgent()
        else:
            logger.info("Using standard MCPAgent")
            self.agent = MCPAgent()

    async def initialize(
        self,
        connection_type: str,
        server_url: str | None = None,
    ) -> None:
        """Initialize the MCP agent with the appropriate connection."""
        logger.info(f"Initializing agent with {connection_type} connection...")

        try:
            if connection_type == "stdio":
                await self.agent.initialize(
                    connection_type="stdio",
                    command=sys.executable,
                    args=["-m", self.server_reference],
                )
            else:  # sse
                await self.agent.initialize(connection_type="sse", server_url=server_url)

            logger.info(f"Connected to MCP server via {connection_type}")

        except ValueError as e:
            # Обрабатываем ошибку отсутствия необходимых модулей
            logger.error(f"Initialization error: {str(e)}")
            print(f"Error: {str(e)}")
            print("Make sure Serena and Sequential Thinking modules are available on the MCP server.")
            sys.exit(1)

    async def run_interactive(self) -> None:
        """Run the agent in interactive mode."""
        print("\nGopiAI Reasoning Agent Interactive Mode (type 'exit' to quit)\n")

        while True:
            user_input = input("\nEnter your request: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                break

            # Для reasoning-агента дополнительно обрабатываем команды plan/approve/reject
            if isinstance(self.agent, ReasoningAgent):
                if user_input.lower() == "approve":
                    self.agent.approve_plan()
                    print("Plan approved. Proceeding with execution.")
                    continue

                if user_input.lower() == "reject":
                    self.agent.reject_plan()
                    print("Plan rejected. Please provide a new request.")
                    continue

                if user_input.lower().startswith("plan "):
                    # Создаем план для указанной задачи
                    task = user_input[5:].strip()
                    print(f"Creating a plan for: {task}")
                    plan = await self.agent.create_plan(task)
                    print("\nProposed Plan:")
                    print(plan)
                    print("\nType 'approve' to accept this plan or 'reject' to start over.")
                    continue

            # Стандартная обработка запроса
            try:
                response = await self.agent.run(user_input)
                print(f"\nAgent: {response}")
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                print(f"\nError: {str(e)}")

    async def run_single_prompt(self, prompt: str) -> None:
        """Run the agent with a single prompt."""
        await self.agent.run(prompt)

    async def run_default(self) -> None:
        """Run the agent in default mode."""
        prompt = input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.info("Processing your request...")
        await self.agent.run(prompt)
        logger.info("Request processing completed.")

    async def cleanup(self) -> None:
        """Clean up agent resources."""
        await self.agent.cleanup()
        logger.info("Session ended")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the GopiAI Agent")
    parser.add_argument(
        "--connection",
        "-c",
        choices=["stdio", "sse"],
        default="stdio",
        help="Connection type: stdio or sse",
    )
    parser.add_argument(
        "--server-url",
        default="http://127.0.0.1:8000/sse",
        help="URL for SSE connection",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument("--prompt", "-p", help="Single prompt to execute and exit")
    parser.add_argument(
        "--agent-type",
        "-a",
        choices=["mcp", "reasoning"],
        default="reasoning",
        help="Type of agent to use (mcp or reasoning)"
    )
    return parser.parse_args()


async def run_mcp() -> None:
    """Main entry point for the MCP runner."""
    args = parse_args()
    runner = MCPRunner(agent_type=args.agent_type)

    try:
        await runner.initialize(args.connection, args.server_url)

        if args.prompt:
            await runner.run_single_prompt(args.prompt)
        elif args.interactive:
            await runner.run_interactive()
        else:
            await runner.run_default()

    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(run_mcp())
