"""Boot checklist hook — run BOOT.md on gateway startup.

Drop a BOOT.md file in ~/.hermes/ with instructions for the agent to
execute when the gateway starts.  The agent runs the instructions in a
one-shot session and delivers its response to the configured home
channel.  If nothing needs attention, the agent can reply with [SILENT]
to suppress delivery.

Example BOOT.md:

    # Startup Checklist

    1. Check if the deploy script in /opt/app finished (look at deploy.log)
    2. Send a status update to Discord #general
    3. If there are errors, summarize them

To install:
    cp -r gateway/example-hooks/boot-md ~/.hermes/hooks/boot-md
"""

import asyncio
import logging
import os
import threading
from pathlib import Path

logger = logging.getLogger("hooks.boot-md")

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
BOOT_FILE = HERMES_HOME / "BOOT.md"


def _build_boot_prompt(content: str) -> str:
    """Wrap BOOT.md content in a system-level instruction."""
    return (
        "You are running a startup boot checklist. Follow the BOOT.md "
        "instructions below exactly.\n\n"
        "---\n"
        f"{content}\n"
        "---\n\n"
        "Execute each instruction. If you need to send a message to a "
        "platform, use the send_message tool.\n"
        "If nothing needs attention and there is nothing to report, "
        "reply with ONLY: [SILENT]"
    )


def _run_boot_agent(content: str) -> None:
    """Spawn a one-shot agent session to execute the boot instructions."""
    try:
        from run_agent import AIAgent

        prompt = _build_boot_prompt(content)
        agent = AIAgent(
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            max_iterations=20,
        )
        result = agent.run_conversation(prompt)
        response = result.get("final_response", "")
        if response and "[SILENT]" not in response:
            logger.info("boot-md completed: %s", response[:200])
        else:
            logger.info("boot-md completed (nothing to report)")
    except Exception as e:
        logger.error("boot-md agent failed: %s", e)


async def handle(event_type: str, context: dict) -> None:
    """Gateway startup handler — run BOOT.md if it exists."""
    if not BOOT_FILE.exists():
        logger.debug("No BOOT.md found at %s, skipping", BOOT_FILE)
        return

    content = BOOT_FILE.read_text(encoding="utf-8").strip()
    if not content:
        logger.debug("BOOT.md is empty, skipping")
        return

    logger.info("Running BOOT.md (%d chars)", len(content))

    # Run in a background thread so we don't block gateway startup.
    # The agent may make tool calls, API requests, etc.
    thread = threading.Thread(
        target=_run_boot_agent,
        args=(content,),
        name="boot-md",
        daemon=True,
    )
    thread.start()
