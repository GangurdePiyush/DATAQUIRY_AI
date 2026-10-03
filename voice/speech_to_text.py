"""
voice/speech_to_text.py
-----------------------
Handles microphone audio capture and speech-to-text recognition using standard/local libraries.
Includes fallback mechanisms if microphone hardware or audio packages are unavailable.
"""

from typing import Tuple, Optional

# Safe import of SpeechRecognition
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    sr = None
    SR_AVAILABLE = False


class SpeechToTextRecognizer:
    """
    Captures microphone input and converts speech into text.
    Handles hardware absence and audio errors without application crashes.
    """

    def __init__(self):
        self.sr_available = SR_AVAILABLE

    def is_microphone_available(self) -> Tuple[bool, str]:
        """
        Checks if SpeechRecognition package is installed and a working microphone is detected.
        """
        if not self.sr_available:
            return False, "SpeechRecognition library is not installed."

        try:
            mics = sr.Microphone.list_microphone_names()
            if not mics:
                return False, "No microphone input device found on this system."
            return True, f"Found {len(mics)} microphone device(s)."
        except OSError as oe:
            return False, f"Microphone hardware access error: {str(oe)}"
        except Exception as ex:
            return False, f"Audio device error: {str(ex)}"

    def listen_from_microphone(self, timeout: int = 5, phrase_time_limit: int = 8) -> Tuple[bool, str, str]:
        """
        Listens to microphone input and converts spoken audio into text.

        Parameters:
            timeout (int): Seconds to wait for speech to start.
            phrase_time_limit (int): Maximum phrase length in seconds.

        Returns:
            Tuple[bool, str, str]: (Success boolean, Recognized text or empty string, Status message)
        """
        if not self.sr_available:
            return (
                False,
                "",
                "SpeechRecognition library is missing. Install with 'pip install SpeechRecognition'.",
            )

        mic_ok, mic_msg = self.is_microphone_available()
        if not mic_ok:
            return False, "", mic_msg

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            # Recognize speech using free Google Web Speech endpoint
            text = recognizer.recognize_google(audio_data)
            text = text.strip()

            if not text:
                return False, "", "No speech detected."

            return True, text, f"Recognized: '{text}'"

        except sr.WaitTimeoutError:
            return False, "", "Listening timed out (No speech detected)."
        except sr.UnknownValueError:
            return False, "", "Speech unintelligible. Please speak clearly or use text input."
        except sr.RequestError as re:
            return False, "", f"Speech service unavailable (Network error: {str(re)}). Please use text input."
        except OSError as oe:
            return False, "", f"Microphone error: {str(oe)}. Text input remains active."
        except Exception as ex:
            return False, "", f"Speech recognition error: {str(ex)}"
