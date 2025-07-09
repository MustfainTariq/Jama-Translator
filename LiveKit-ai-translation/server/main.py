"""
LiveKit Translation Agent with Supabase Integration
Handles real-time audio transcription, translation, and logging to Supabase database
"""

import asyncio
import logging
import json
import time
import re
from typing import Set, Any, Dict, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    JobRequest,
    WorkerOptions,
    cli,
    stt,
    llm,
    utils,
)
from livekit.plugins import openai, silero, speechmatics
from livekit.plugins.speechmatics.types import TranscriptionConfig
from dotenv import load_dotenv
import os

# Import our Supabase service
from supabase_service import supabase_service

load_dotenv()

logger = logging.getLogger("transcriber")

@dataclass
class Language:
    code: str
    name: str
    flag: str

languages = {
    "ar": Language(code="ar", name="Arabic", flag="🇸🇦"),
    "en": Language(code="en", name="English", flag="🇺🇸"),
    "es": Language(code="es", name="Spanish", flag="🇪🇸"),
    "fr": Language(code="fr", name="French", flag="🇫🇷"),
    "de": Language(code="de", name="German", flag="🇩🇪"),
    "ja": Language(code="ja", name="Japanese", flag="🇯🇵"),
    "nl": Language(code="nl", name="Dutch", flag="🇳🇱"),
    "ur": Language(code="ur", name="Urdu", flag="🇵🇰"),
    "tr": Language(code="tr", name="Turkish", flag="🇹🇷"),
    "id": Language(code="id", name="Indonesian", flag="🇮🇩"),
    "ms": Language(code="ms", name="Malay", flag="🇲🇾"),
}

LanguageCode = Enum(
    "LanguageCode",
    {lang.name: code for code, lang in languages.items()},
)


class TranslationService:
    """Enhanced translation service with Supabase integration"""
    
    def __init__(self, room: rtc.Room, target_language: str, source_language: str = "ar"):
        self.room = room
        self.target_language = target_language
        self.source_language = source_language
        self.use_context = True  # Enable context for better translations
        self.context = llm.ChatContext()
        self.message_count = 0
        self.max_context_messages = 9
        
        # Configure system prompt
        self.system_prompt = (
            f"You are a professional simultaneous interpreter for Islamic religious content. "
            f"Translate the provided {source_language} text to {target_language}. "
            f"Rules: 1) Translate ONLY the most recent sentence. "
            f"2) Be accurate and respectful with religious terminology. "
            f"3) Use natural, spoken language appropriate for live translation. "
            f"4) Return ONLY the translation, no explanations. "
            f"5) Maintain the tone and meaning of the original."
        )
        
        self.context.add_message(role="system", content=self.system_prompt)
        self.llm = openai.LLM()
        
        logger.info(f"Translation service initialized: {source_language} -> {target_language}")

    async def translate_text(self, text: str, track: rtc.Track) -> str:
        """Translate text and publish to room"""
        try:
            if self.use_context:
                self.context.add_message(content=text, role="user")
                self.message_count += 1
                
                # Reset context periodically to prevent drift
                if self.message_count > self.max_context_messages:
                    self.context = llm.ChatContext()
                    self.context.add_message(role="system", content=self.system_prompt)
                    self.message_count = 0
                    logger.debug("Context reset after 9 messages")
                
                stream = self.llm.chat(chat_ctx=self.context)
            else:
                # Fresh context mode
                fresh_context = llm.ChatContext()
                fresh_context.add_message(role="system", content=self.system_prompt)
                fresh_context.add_message(content=text, role="user")
                stream = self.llm.chat(chat_ctx=fresh_context)
            
            # Collect translation
            translated_text = ""
            async for chunk in stream:
                if chunk.delta and chunk.delta.content:
                    translated_text += chunk.delta.content
            
            # Clean up translation
            translated_text = translated_text.strip()
            
            # Publish to room
            await self._publish_transcription(translated_text, track)
            
            logger.info(f"Translated: {text[:50]}... -> {translated_text[:50]}...")
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original text if translation fails

    async def _publish_transcription(self, text: str, track: rtc.Track):
        """Publish transcription to LiveKit room"""
        try:
            segment = rtc.TranscriptionSegment(
                id=utils.misc.shortuuid("SG_"),
                text=text,
                start_time=0,
                end_time=0,
                language=self.target_language,
                final=True,
            )
            
            transcription = rtc.Transcription(
                self.room.local_participant.identity,
                track.sid if track else "",
                [segment]
            )
            
            await self.room.local_participant.publish_transcription(transcription)
            
        except Exception as e:
            logger.error(f"Error publishing transcription: {e}")


class RoomSessionManager:
    """Manages room sessions and database integration"""
    
    def __init__(self, room: rtc.Room):
        self.room = room
        self.room_data: Optional[Dict[str, Any]] = None
        self.active_session: Optional[Dict[str, Any]] = None
        self.translation_service: Optional[TranslationService] = None
        self.participant_count = 0
        
    async def initialize(self):
        """Initialize room session by loading room data from database"""
        try:
            # Get room data from database using LiveKit room name
            self.room_data = await supabase_service.get_room_by_livekit_name(self.room.name)
            
            if not self.room_data:
                logger.error(f"Room {self.room.name} not found in database")
                return False
            
            logger.info(f"Loaded room data: {self.room_data['Title']} (ID: {self.room_data['id']})")
            
            # Get room languages
            source_lang, target_lang = await supabase_service.get_room_languages(self.room_data['id'])
            
            # Initialize translation service
            self.translation_service = TranslationService(
                room=self.room,
                target_language=target_lang,
                source_language=source_lang
            )
            
            # Start session automatically when room is initialized
            await self.start_session()
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing room session: {e}")
            return False

    async def start_session(self):
        """Start a new recording session"""
        try:
            if not self.room_data:
                logger.error("Cannot start session: room data not loaded")
                return
            
            session_id = await supabase_service.start_session(
                room_id=self.room_data['id'],
                mosque_id=self.room_data['mosque_id']
            )
            
            if session_id:
                self.active_session = {
                    'id': session_id,
                    'room_id': self.room_data['id'],
                    'mosque_id': self.room_data['mosque_id']
                }
                
                # Cache session info
                supabase_service.set_session_info(self.room.name, self.active_session)
                
                logger.info(f"Started session {session_id} for room {self.room_data['Title']}")
                 
        except Exception as e:
             logger.error(f"Error starting session: {e}")

    async def stop_session(self):
        """Stop the current recording session"""
        try:
            if self.room_data and self.active_session:
                await supabase_service.stop_session(self.room_data['id'])
                logger.info(f"Stopped session {self.active_session['id']}")
                
                # Clear cached session info
                supabase_service.remove_session_info(self.room.name)
                
        except Exception as e:
            logger.error(f"Error stopping session: {e}")

    async def handle_transcription(self, text: str, track: rtc.Track):
        """Handle incoming transcription and translation"""
        try:
            if not self.translation_service or not self.active_session or not self.room_data:
                logger.warning("Translation service, session, or room data not initialized")
                return
            
            # Check if logging is enabled
            if not await supabase_service.is_session_logging_enabled(self.room_data['id']):
                logger.debug("Logging disabled for this session")
                return
            
            # Translate text
            translated_text = await self.translation_service.translate_text(text, track)
            
            # Save to database
            await supabase_service.save_transcript(
                room_id=self.room_data['id'],
                session_id=self.active_session['id'],
                arabic_text=text,
                translation=translated_text
            )
            
            # Send to admin panel via WebSocket
            await supabase_service.send_to_websocket_logger(
                room_id=self.room_data['id'],
                mosque_id=self.room_data['mosque_id'],
                arabic_text=text,
                translation=translated_text
            )
            
        except Exception as e:
            logger.error(f"Error handling transcription: {e}")

    async def update_participant_count(self, count: int):
        """Update participant count"""
        try:
            if self.room_data:
                self.participant_count = count
                await supabase_service.update_participant_count(
                    room_id=self.room_data['id'],
                    mosque_id=self.room_data['mosque_id'],
                    count=count
                )
                
        except Exception as e:
            logger.error(f"Error updating participant count: {e}")


def prewarm(proc: JobProcess):
    """Prewarm function to initialize VAD"""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(job: JobContext):
    """Main entrypoint for LiveKit agent"""
    logger.info(f"Starting LiveKit agent for room: {job.room.name}")
    
    # Initialize room session manager
    session_manager = RoomSessionManager(job.room)
    
    # Initialize room data
    if not await session_manager.initialize():
        logger.error("Failed to initialize room session - exiting")
        return
    
    # Get room languages for STT configuration
    if not session_manager.room_data:
        logger.error("Room data not available")
        return
        
    source_lang, target_lang = await supabase_service.get_room_languages(session_manager.room_data['id'])
    
    # Configure STT for the source language
    stt_provider = speechmatics.STT(
        transcription_config=TranscriptionConfig(
            language=source_lang,
            operating_point="enhanced",
            enable_partials=True,
            max_delay=2.0,
            punctuation_overrides={
                "enable_punctuation": True,
                "punctuation_sensitivity": 0.5
            }
        )
    )
    
    # Configure sentence processing
    def extract_complete_sentences(text: str) -> list[str]:
        """Extract complete sentences from text"""
        if not text or len(text.strip()) < 3:
            return []
        
        # Arabic sentence endings
        arabic_endings = ['۔', '؟', '!', '.', '?']
        
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in arabic_endings:
                sentence = current_sentence.strip()
                if len(sentence) > 5:  # Minimum sentence length
                    sentences.append(sentence)
                current_sentence = ""
        
        # Add remaining text if substantial
        if len(current_sentence.strip()) > 10:
            sentences.append(current_sentence.strip())
        
        return sentences
    
    async def transcribe_track(participant: rtc.RemoteParticipant, track: rtc.Track):
        """Transcribe audio track"""
        try:
            audio_stream = rtc.AudioStream(track)
            stt_stream = stt_provider.stream()
            
            async def process_stt_stream():
                """Process STT stream and handle translations"""
                last_transcript = ""
                
                async for event in stt_stream:
                    if event.type == stt.SpeechEventType.FINAL_TRANSCRIPT:
                        text = event.alternatives[0].text.strip()
                        
                        if text and text != last_transcript:
                            logger.info(f"📝 Final transcript: {text}")
                            last_transcript = text
                            
                            # Extract complete sentences
                            sentences = extract_complete_sentences(text)
                            
                            # Process each sentence
                            for sentence in sentences:
                                if len(sentence) > 5:
                                    await session_manager.handle_transcription(sentence, track)
                    
                    elif event.type == stt.SpeechEventType.INTERIM_TRANSCRIPT:
                        # Log interim results for debugging
                        text = event.alternatives[0].text.strip()
                        if text:
                            logger.debug(f"📝 Interim: {text[:50]}...")
            
            # Start processing
            asyncio.create_task(process_stt_stream())
            
            # Stream audio to STT
            async for frame in audio_stream:
                stt_stream.push_frame(frame.frame)
                
        except Exception as e:
            logger.error(f"Error in transcribe_track: {e}")
        finally:
            await stt_stream.aclose()

    # Room event handlers
    @job.room.on("track_subscribed")
    def on_track_subscribed(
        track: rtc.Track,
        publication: rtc.TrackPublication,
        participant: rtc.RemoteParticipant,
    ):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            logger.info(f"🎤 Audio track subscribed: {participant.identity}")
            asyncio.create_task(transcribe_track(participant, track))

    @job.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info(f"👤 Participant connected: {participant.identity}")
        # Update participant count
        count = len(job.room.remote_participants) + 1  # +1 for local participant
        asyncio.create_task(session_manager.update_participant_count(count))

    @job.room.on("participant_disconnected")
    def on_participant_disconnected(participant: rtc.RemoteParticipant):
        logger.info(f"👤 Participant disconnected: {participant.identity}")
        # Update participant count
        count = len(job.room.remote_participants)
        asyncio.create_task(session_manager.update_participant_count(count))

    # RPC method for getting supported languages
    @job.room.local_participant.register_rpc_method("get/languages")
    async def get_languages(data: rtc.RpcInvocationData):
        """Return supported languages"""
        return json.dumps([
            {"code": lang.code, "name": lang.name, "flag": lang.flag}
            for lang in languages.values()
        ])

    logger.info("🚀 LiveKit agent fully initialized and ready")
    
    # Keep the agent running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("🛑 Agent stopped by user")
    finally:
        await session_manager.stop_session()


async def request_fnc(req: JobRequest):
    """Handle job requests"""
    await req.accept()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            request_fnc=request_fnc
        )
    )