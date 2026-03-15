import asyncio
from typing import Dict, Optional
from datetime import datetime
import logging
import numpy as np
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudio
from pytgcalls.exceptions import AlreadyJoinedError, NotInCallError
import io

class BridgeManager:
    def __init__(self):
        self.active_bridges: Dict[str, Dict] = {}
        self.group_settings: Dict[int, Dict] = {}
        self.logger = logging.getLogger(__name__)
        self.audio_queues: Dict[str, asyncio.Queue] = {}
        
    async def create_bridge(self, source_group: int, target_group: int, 
                           source_calls, target_calls, audio_processor):
        """Create audio bridge between two groups"""
        bridge_id = f"{source_group}:{target_group}"
        
        if bridge_id in self.active_bridges:
            return False, "Bridge already exists!"
        
        # Create audio queue for this bridge
        self.audio_queues[bridge_id] = asyncio.Queue(maxsize=100)
        
        self.active_bridges[bridge_id] = {
            'source': source_group,
            'target': target_group,
            'source_calls': source_calls,
            'target_calls': target_calls,
            'audio_processor': audio_processor,
            'created_at': datetime.now(),
            'active': True,
            'stream_task': None,
            'receive_task': None
        }
        
        try:
            # Start audio receiving from source
            receive_task = asyncio.create_task(
                self.receive_audio(bridge_id)
            )
            
            # Start audio forwarding to target
            stream_task = asyncio.create_task(
                self.stream_audio(bridge_id)
            )
            
            self.active_bridges[bridge_id]['receive_task'] = receive_task
            self.active_bridges[bridge_id]['stream_task'] = stream_task
            
            self.logger.info(f"Bridge created: {source_group} -> {target_group}")
            return True, "Bridge created successfully!"
            
        except Exception as e:
            self.logger.error(f"Error creating bridge: {e}")
            await self.remove_bridge(bridge_id)
            return False, f"Error: {str(e)}"
    
    async def receive_audio(self, bridge_id: str):
        """Receive audio from source group"""
        bridge = self.active_bridges.get(bridge_id)
        if not bridge:
            return
            
        source_group = bridge['source']
        audio_queue = self.audio_queues.get(bridge_id)
        
        try:
            self.logger.info(f"Starting audio reception from {source_group}")
            
            @bridge['source_calls'].on_stream_end()
            async def on_stream_end(chat_id: int):
                if chat_id == source_group:
                    self.logger.info(f"Stream ended in source group {source_group}")
                    await self.remove_bridge(bridge_id)
            
            @bridge['source_calls'].on_kicked()
            async def on_kicked(chat_id: int):
                if chat_id == source_group:
                    self.logger.info(f"Bot kicked from source group {source_group}")
                    await self.remove_bridge(bridge_id)
            
            # In dev version, audio reception might be handled differently
            # This is a simplified version
            while bridge.get('active', False):
                try:
                    # Simulate receiving audio (replace with actual audio capture)
                    await asyncio.sleep(0.02)  # 20ms chunks
                    
                    if bridge.get('active', False) and audio_queue:
                        # Generate test audio (replace with actual captured audio)
                        test_audio = np.zeros(1920, dtype=np.int16).tobytes()
                        
                        try:
                            await asyncio.wait_for(
                                audio_queue.put(test_audio),
                                timeout=1.0
                            )
                        except asyncio.TimeoutError:
                            pass
                        
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in receive_audio: {e}")
                    await asyncio.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"Fatal error in receive_audio: {e}")
        finally:
            self.logger.info(f"Audio reception stopped for {bridge_id}")
    
    async def stream_audio(self, bridge_id: str):
        """Stream processed audio to target group"""
        bridge = self.active_bridges.get(bridge_id)
        if not bridge:
            return
            
        target_group = bridge['target']
        audio_queue = self.audio_queues.get(bridge_id)
        audio_processor = bridge['audio_processor']
        
        try:
            self.logger.info(f"Starting audio streaming to {target_group}")
            
            while bridge.get('active', False):
                try:
                    if audio_queue:
                        # Get audio chunk from queue
                        audio_chunk = await asyncio.wait_for(
                            audio_queue.get(), 
                            timeout=5.0
                        )
                        
                        # Process audio with filters
                        processed_audio = await audio_processor.process_audio(
                            audio_chunk,
                            str(target_group),
                            str(bridge['source'])
                        )
                        
                        # In dev version, you would send audio to target
                        # This depends on your implementation
                        self.logger.debug(f"Processed {len(processed_audio)} bytes for {target_group}")
                    
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in stream_audio: {e}")
                    await asyncio.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"Fatal error in stream_audio: {e}")
        finally:
            self.logger.info(f"Audio streaming stopped for {bridge_id}")
    
    async def remove_bridge(self, bridge_id: str):
        """Remove an active bridge"""
        if bridge_id in self.active_bridges:
            bridge = self.active_bridges[bridge_id]
            bridge['active'] = False
            
            self.logger.info(f"Removing bridge {bridge_id}")
            
            # Cancel tasks
            if bridge.get('receive_task'):
                bridge['receive_task'].cancel()
                try:
                    await bridge['receive_task']
                except:
                    pass
                    
            if bridge.get('stream_task'):
                bridge['stream_task'].cancel()
                try:
                    await bridge['stream_task']
                except:
                    pass
            
            # Leave voice chats
            try:
                if bridge.get('source_calls'):
                    await bridge['source_calls'].leave_group_call(bridge['source'])
            except:
                pass
                
            try:
                if bridge.get('target_calls'):
                    await bridge['target_calls'].leave_group_call(bridge['target'])
            except:
                pass
            
            # Clean up queue
            if bridge_id in self.audio_queues:
                while not self.audio_queues[bridge_id].empty():
                    try:
                        self.audio_queues[bridge_id].get_nowait()
                    except:
                        pass
                del self.audio_queues[bridge_id]
            
            del self.active_bridges[bridge_id]
            self.logger.info(f"Bridge {bridge_id} removed successfully")
            return True
            
        return False
    
    def set_group_setting(self, group_id: int, setting: str, value):
        """Set group-specific settings"""
        if group_id not in self.group_settings:
            self.group_settings[group_id] = {}
        
        self.group_settings[group_id][setting] = value
        self.logger.info(f"Group {group_id} setting {setting} = {value}")
    
    def get_group_setting(self, group_id: int, setting: str, default=None):
        """Get group-specific setting"""
        if group_id in self.group_settings:
            return self.group_settings[group_id].get(setting, default)
        return default
    
    async def check_voice_chat_active(self, group_id: int, client):
        """Check if voice chat is active in a group"""
        try:
            chat = await client.get_chat(group_id)
            return hasattr(chat, 'voice_chat') and chat.voice_chat is not None
        except Exception as e:
            self.logger.error(f"Error checking voice chat: {e}")
            return False
    
    def get_bridge_status(self, bridge_id: str = None):
        """Get status of bridges"""
        if bridge_id:
            if bridge_id in self.active_bridges:
                bridge = self.active_bridges[bridge_id]
                return {
                    'exists': True,
                    'source': bridge['source'],
                    'target': bridge['target'],
                    'active': bridge['active'],
                    'created_at': bridge['created_at'].isoformat()
                }
            return {'exists': False}
        
        # Return all bridges
        status = {}
        for bid, bridge in self.active_bridges.items():
            status[bid] = {
                'source': bridge['source'],
                'target': bridge['target'],
                'active': bridge['active'],
                'created_at': bridge['created_at'].isoformat()
            }
        return status