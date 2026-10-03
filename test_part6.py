"""
test_part6.py
-------------
Automated test suite for Part 6 Voice Interaction (STT & TTS engines).
"""

from voice import VoiceHandler, SpeechToTextRecognizer, TextToSpeechEngine


def run_tests():
    print("==========================================")
    print("RUNNING PART 6 VOICE INTERACTION VERIFICATION")
    print("==========================================")

    vh = VoiceHandler()
    stt = SpeechToTextRecognizer()
    tts = TextToSpeechEngine()

    # Test 1: STT Engine Initialization & Device Check
    print("\n[Test 1] Speech-to-Text Device Check:")
    print(f"  SR Available: {stt.sr_available}")
    mic_ok, mic_msg = stt.is_microphone_available()
    print(f"  Microphone Check: {mic_ok} | Message: '{mic_msg}'")
    assert stt.sr_available is True, "SpeechRecognition library should be installed!"

    # Test 2: TTS Result Summarizer - Large Table (> 3 rows)
    print("\n[Test 2] TTS Summarizer - Large Table Result (>3 rows):")
    res_large = {
        "success": True,
        "row_count": 15,
        "column_count": 6,
        "columns": ["id", "name", "salary", "age", "department", "city"],
        "rows": [["1", "Alice", 85000, 29, "Eng", "NY"]] * 15,
    }
    summary_large = tts.format_query_result_summary(res_large)
    print(f"  Input  : 15 rows, 6 columns")
    print(f"  Spoken : '{summary_large}'")
    assert "returned 15 records" in summary_large, "Large table summary should state total record count!"
    assert "Alice" not in summary_large, "Large table summary should NOT speak individual rows!"

    # Test 3: TTS Result Summarizer - Single Value (COUNT/AVG)
    print("\n[Test 3] TTS Summarizer - Single Value Result (COUNT/AVG):")
    res_single = {
        "success": True,
        "row_count": 1,
        "column_count": 1,
        "columns": ["average_salary"],
        "rows": [[74600.0]],
    }
    summary_single = tts.format_query_result_summary(res_single)
    print(f"  Input  : average_salary = 74600.0")
    print(f"  Spoken : '{summary_single}'")
    assert "74,600.00" in summary_single or "74600" in summary_single, "Single value summary should state exact formatted value!"

    # Test 4: TTS Result Summarizer - Zero Rows Result
    print("\n[Test 4] TTS Summarizer - Zero Rows Result:")
    res_zero = {
        "success": True,
        "row_count": 0,
        "column_count": 4,
        "columns": ["id", "name", "age", "salary"],
        "rows": [],
    }
    summary_zero = tts.format_query_result_summary(res_zero)
    print(f"  Input  : 0 rows")
    print(f"  Spoken : '{summary_zero}'")
    assert "zero" in summary_zero.lower() or "0" in summary_zero, "Zero rows summary should state zero records!"

    # Test 5: Fallback Resilience Check
    print("\n[Test 5] Fallback Resilience Check (Microphone Absence):")
    success_listen, text_listen, status_listen = stt.listen_from_microphone(timeout=1, phrase_time_limit=1)
    print(f"  Listen Result: Success={success_listen}")
    print(f"  Status Msg   : '{status_listen}'")
    # Must return cleanly with boolean status without throwing unhandled exception
    assert isinstance(success_listen, bool), "listen_from_microphone must return boolean success status!"

    print("\n==========================================")
    print("ALL PART 6 VOICE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")


if __name__ == "__main__":
    run_tests()
