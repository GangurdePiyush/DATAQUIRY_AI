"""
voice/voice_handler.py
-----------------------
High-level facade integrating SpeechToTextRecognizer and TextToSpeechEngine.
Exposes clean methods for voice recording, speech recognition, and audio summaries.
"""

from typing import Tuple, Dict, Any
from .speech_to_text import SpeechToTextRecognizer
from .text_to_speech import TextToSpeechEngine


class VoiceHandler:
    """
    High-level voice interaction manager for speech recognition and TTS feedback.
    """

    def __init__(self):
        self.stt = SpeechToTextRecognizer()
        self.tts = TextToSpeechEngine()

    def listen_and_recognize(self) -> Tuple[bool, str, str]:
        """
        Captures microphone audio and converts speech to text.

        Returns:
            Tuple[bool, str, str]: (Success boolean, Recognized text, Status message)
        """
        return self.stt.listen_from_microphone()

    def speak_text(self, text: str) -> bool:
        """Speaks a text string using offline TTS engine."""
        return self.tts.speak(text)

    def speak_query_result(self, result_dict: Dict[str, Any]) -> str:
        """
        Formats a concise audio summary of query results and speaks it.

        Returns:
            str: The summary string that was spoken.
        """
        summary = self.tts.format_query_result_summary(result_dict)
        self.tts.speak(summary)
        return summary

    def is_stt_available(self) -> bool:
        """Returns True if STT package is available."""
        return self.stt.sr_available

    def is_tts_available(self) -> bool:
        """Returns True if TTS engine is available."""
        return self.tts.is_tts_available()
