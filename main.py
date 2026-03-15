import os
import asyncio
import logging
from dotenv import load_dotenv
from pyrogram import Client
import config
from handlers import setup_handlers
from bridge_manager import BridgeManager
from audio_processor import AudioProcessor

# Pytgcalls imports for dev version
from pytgcalls import PyTgCalls
from pytgcalls.types import StreamAudio
from pytgcalls.types.input_stream import InputStream, InputAudioStream

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class AudioBridgeBot:
    def __init__(self):
        # Initialize Pyrogram Client for Bot
        self.app = Client(
            "audio_bridge_bot",
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            bot_token=os.getenv("BOT_TOKEN"),
            workers=16
        )
        
        # Initialize Pyrogram Client for User
        self.user_app = Client(
            "user_session",
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            session_string=os.getenv("SESSION_STRING")
        )
        
        # Initialize PyTgCalls instances (dev version)
        self.bot_calls = PyTgCalls(self.app)
        self.user_calls = PyTgCalls(self.user_app)
        
        # Initialize managers
        self.bridge_manager = BridgeManager()
        self.audio_processor = AudioProcessor()
        
        # Admin IDs
        self.admin_ids = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
        
        logger.info(f"Admin IDs: {self.admin_ids}")
        logger.info("Kernel Audio Bridge Bot initialized with enhanced processing!")
        
    async def start(self):
        """Start the bot and all services"""
        logger.info("Starting Kernel Audio Bridge Bot...")
        
        try:
            # Start Pyrogram clients
            await self.app.start()
            logger.info("Bot client started successfully")
            
            await self.user_app.start()
            logger.info("User client started successfully")
            
            # Start PyTgCalls
            await self.bot_calls.start()
            logger.info("Bot calls started successfully")
            
            await self.user_calls.start()
            logger.info("User calls started successfully")
            
            # Setup command handlers
            setup_handlers(self)
            
            logger.info("=" * 50)
            logger.info("KERNEL AUDIO BRIDGE BOT IS RUNNING!")
            logger.info("🔥 Enhanced audio processing enabled")
            logger.info("💀 Kernel sound presets available")
            logger.info("=" * 50)
            
            # Keep the bot running
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop all services gracefully"""
        logger.info("Stopping Kernel Audio Bridge Bot...")
        
        try:
            # Stop all active bridges
            for bridge_id in list(self.bridge_manager.active_bridges.keys()):
                logger.info(f"Removing bridge: {bridge_id}")
                await self.bridge_manager.remove_bridge(bridge_id)
            
            # Stop PyTgCalls
            try:
                await self.bot_calls.stop()
                logger.info("Bot calls stopped")
            except:
                pass
                
            try:
                await self.user_calls.stop()
                logger.info("User calls stopped")
            except:
                pass
            
            # Stop Pyrogram clients
            try:
                await self.app.stop()
                logger.info("Bot client stopped")
            except Exception as e:
                logger.error(f"Error stopping bot client: {e}")
                
            try:
                await self.user_app.stop()
                logger.info("User client stopped")
            except Exception as e:
                logger.error(f"Error stopping user client: {e}")
                
            logger.info("Kernel Audio Bridge Bot stopped successfully")
                
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    bot = AudioBridgeBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        asyncio.run(bot.stop())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        asyncio.run(bot.stop())