"""
Supabase integration service for LiveKit backend
Handles database operations, session management, and admin panel integration
"""

import os
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
import httpx

load_dotenv()

logger = logging.getLogger("supabase_service")


class SupabaseService:
    """Service for handling Supabase database operations and admin panel integration"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.websocket_logger_url = os.getenv("WEBSOCKET_LOGGER_URL")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing required Supabase environment variables")
            
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Supabase service initialized with URL: {self.supabase_url}")

    async def get_room_by_livekit_name(self, livekit_room_name: str) -> Optional[Dict[str, Any]]:
        """Get room details by LiveKit room name"""
        try:
            result = self.supabase.table("rooms").select("*").eq("Livekit_room_name", livekit_room_name).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching room by LiveKit name {livekit_room_name}: {e}")
            return None

    async def get_active_session(self, room_id: int) -> Optional[Dict[str, Any]]:
        """Get active session for a room"""
        try:
            result = self.supabase.table("room_sessions").select("*").eq("room_id", room_id).eq("status", "active").execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching active session for room {room_id}: {e}")
            return None

    async def start_session(self, room_id: int, mosque_id: int) -> Optional[str]:
        """Start a new recording session"""
        try:
            # Check if there's already an active session
            active_session = await self.get_active_session(room_id)
            if active_session:
                logger.info(f"Session already active for room {room_id}")
                return active_session["id"]
            
            # Create new session
            session_data = {
                "room_id": room_id,
                "mosque_id": mosque_id,
                "status": "active",
                "logging_enabled": True,
                "transcript_count": 0
            }
            
            result = self.supabase.table("room_sessions").insert(session_data).execute()
            
            if result.data:
                session_id = result.data[0]["id"]
                logger.info(f"Started new session {session_id} for room {room_id}")
                return session_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error starting session for room {room_id}: {e}")
            return None

    async def stop_session(self, room_id: int) -> bool:
        """Stop active session for a room"""
        try:
            # Get active session
            active_session = await self.get_active_session(room_id)
            if not active_session:
                logger.warning(f"No active session found for room {room_id}")
                return False
            
            # Update session status
            result = self.supabase.table("room_sessions").update({
                "status": "completed",
                "ended_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", active_session["id"]).execute()
            
            if result.data:
                logger.info(f"Stopped session {active_session['id']} for room {room_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping session for room {room_id}: {e}")
            return False

    async def save_transcript(self, room_id: int, session_id: str, arabic_text: str, translation: str) -> bool:
        """Save transcript to database"""
        try:
            transcript_data = {
                "room_id": room_id,
                "session_id": session_id,
                "transcription_segment": arabic_text,
                "translation_segment": translation,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("transcripts").insert(transcript_data).execute()
            
            if result.data:
                # Update transcript count in session
                await self.update_session_transcript_count(session_id)
                logger.debug(f"Saved transcript for session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error saving transcript: {e}")
            return False

    async def update_session_transcript_count(self, session_id: str):
        """Update transcript count for a session"""
        try:
            # Get current count
            result = self.supabase.table("room_sessions").select("transcript_count").eq("id", session_id).execute()
            
            if result.data:
                current_count = result.data[0]["transcript_count"]
                new_count = current_count + 1
                
                # Update count
                self.supabase.table("room_sessions").update({
                    "transcript_count": new_count,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", session_id).execute()
                
        except Exception as e:
            logger.error(f"Error updating transcript count: {e}")

    async def send_to_websocket_logger(self, room_id: int, mosque_id: int, arabic_text: str, translation: str):
        """Send translation data to the WebSocket logger"""
        try:
            message = {
                "type": "translation",
                "room_id": room_id,
                "mosque_id": mosque_id,
                "data": {
                    "arabic": arabic_text,
                    "translation": translation
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.websocket_logger_url:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.websocket_logger_url}/functions/v1/websocket-logger",
                        json=message,
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        logger.debug("Successfully sent to WebSocket logger")
                    else:
                        logger.warning(f"WebSocket logger responded with {response.status_code}")
            else:
                logger.debug("WebSocket logger URL not configured")
                
        except Exception as e:
            logger.debug(f"Could not send to WebSocket logger: {e}")

    async def get_room_languages(self, room_id: int) -> tuple[str, str]:
        """Get transcription and translation languages for a room"""
        try:
            result = self.supabase.table("rooms").select("transcription_language, translation__language").eq("id", room_id).execute()
            
            if result.data:
                room_data = result.data[0]
                transcription_lang = room_data.get("transcription_language", "ar")
                translation_lang = room_data.get("translation__language", "en")
                return transcription_lang, translation_lang
            
            return "ar", "en"  # Default values
            
        except Exception as e:
            logger.error(f"Error fetching room languages: {e}")
            return "ar", "en"

    async def is_session_logging_enabled(self, room_id: int) -> bool:
        """Check if logging is enabled for the current session"""
        try:
            active_session = await self.get_active_session(room_id)
            if active_session:
                return active_session.get("logging_enabled", False)
            return False
            
        except Exception as e:
            logger.error(f"Error checking logging status: {e}")
            return False

    async def update_participant_count(self, room_id: int, mosque_id: int, count: int):
        """Send participant count update to admin panel"""
        try:
            message = {
                "type": "participant_update",
                "room_id": room_id,
                "mosque_id": mosque_id,
                "data": {"count": count},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.websocket_logger_url:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{self.websocket_logger_url}/functions/v1/websocket-logger",
                        json=message,
                        timeout=5.0
                    )
                    
        except Exception as e:
            logger.debug(f"Could not send participant update: {e}")

    def get_session_info(self, livekit_room_name: str) -> Optional[Dict[str, Any]]:
        """Get cached session information"""
        return self.active_sessions.get(livekit_room_name)

    def set_session_info(self, livekit_room_name: str, session_info: Dict[str, Any]):
        """Cache session information"""
        self.active_sessions[livekit_room_name] = session_info

    def remove_session_info(self, livekit_room_name: str):
        """Remove cached session information"""
        if livekit_room_name in self.active_sessions:
            del self.active_sessions[livekit_room_name]


# Global instance
supabase_service = SupabaseService() 