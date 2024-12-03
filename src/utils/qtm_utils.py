import asyncio
from enum import Enum

class OperatingSystem(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "Darwin"
    UNKNOWN = "Unknown"

# Event loop policy determines how events are selected for exectution.
# Selecting an OS-specific policy makes this selection more efficient.
# Currently, only Windows is set to use the non-default option.
event_loop_policies = {
    OperatingSystem.WINDOWS: asyncio.WindowsSelectorEventLoopPolicy(),
    OperatingSystem.LINUX: asyncio.DefaultEventLoopPolicy(),
    OperatingSystem.MACOS: asyncio.DefaultEventLoopPolicy(),
    OperatingSystem.UNKNOWN: asyncio.DefaultEventLoopPolicy()
}
