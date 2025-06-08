"""
MCP youtube package initialization
"""

from mcp.server import Server
import logging
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from .constants import *


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize MCP Server instance
youtube_mcp = Server("youtube-mcp")

# Define server configuration
def get_server_config():
    return InitializationOptions(
        server_name="youtube-mcp",
        server_version="1.0.0",
        capabilities=youtube_mcp.get_capabilities(
            notification_options=NotificationOptions(resources_changed=True),
            experimental_capabilities={},
        ),
    )

__all__ = [
    'youtube_mcp',  # Export the MCP instance
    'get_server_config',  # Export the server configuration
    'logger'
] 