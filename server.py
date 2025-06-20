from mcp_vendor import mcp, logger, get_server_config
import asyncio
from mcp.server.stdio import stdio_server
from .tools import register_tools
from .resources import register_resources
from .prompts import register_prompts


async def main():
    """Main function to run the server."""
    logger.info("Starting MCP server...")

    # Register tools before starting the server
    register_tools()

    register_prompts()

    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            get_server_config()
        )
    logger.info("MCP server started successfully")

# This is required for the entry point to work
if __name__ == '__main__':
    asyncio.run(main())
