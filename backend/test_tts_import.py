#!/usr/bin/env python3
"""
Test TTS Service Import and Initialization
"""
import sys
import os

print("=" * 60)
print("TTS Service Diagnostic Test")
print("=" * 60)

# Test 1: Check Python path
print("\n[1] Python Path:")
for p in sys.path:
    print(f"  - {p}")

# Test 2: Try importing OpenVoice
print("\n[2] Testing OpenVoice import...")
try:
    import openvoice
    print(f"  ✅ openvoice imported successfully from: {openvoice.__file__}")
except Exception as e:
    print(f"  ❌ Failed to import openvoice: {e}")

# Test 3: Try importing MeloTTS
print("\n[3] Testing MeloTTS import...")
try:
    import melo
    print(f"  ✅ melo imported successfully from: {melo.__file__}")
except Exception as e:
    print(f"  ❌ Failed to import melo: {e}")

# Test 4: Try importing se_extractor
print("\n[4] Testing se_extractor import...")
try:
    from openvoice import se_extractor
    print(f"  ✅ se_extractor imported successfully")
except Exception as e:
    print(f"  ❌ Failed to import se_extractor: {e}")

# Test 5: Try importing ToneColorConverter
print("\n[5] Testing ToneColorConverter import...")
try:
    from openvoice.api import ToneColorConverter
    print(f"  ✅ ToneColorConverter imported successfully")
except Exception as e:
    print(f"  ❌ Failed to import ToneColorConverter: {e}")

# Test 6: Try importing MeloTTS TTS
print("\n[6] Testing MeloTTS TTS import...")
try:
    from melo.api import TTS
    print(f"  ✅ MeloTTS TTS imported successfully")
except Exception as e:
    print(f"  ❌ Failed to import MeloTTS TTS: {e}")

# Test 7: Check if checkpoint files exist
print("\n[7] Checking checkpoint files...")
converter_path = "OpenVoice/checkpoints_v2/converter"
if os.path.exists(converter_path):
    print(f"  ✅ Converter directory exists: {converter_path}")
    config_file = f"{converter_path}/config.json"
    checkpoint_file = f"{converter_path}/checkpoint.pth"
    print(f"    - config.json: {'✅' if os.path.exists(config_file) else '❌'}")
    print(f"    - checkpoint.pth: {'✅' if os.path.exists(checkpoint_file) else '❌'}")
else:
    print(f"  ❌ Converter directory not found: {converter_path}")

# Test 8: Try initializing TTS Service
print("\n[8] Testing TTS Service initialization...")
try:
    from app.services.tts_service import tts_service
    print(f"  ✅ TTS Service imported")
    print(f"    - MO_INSTALLED: {tts_service is not None}")
    if hasattr(tts_service, 'loaded'):
        print(f"    - Models loaded: {tts_service.loaded}")
except Exception as e:
    print(f"  ❌ Failed to initialize TTS Service: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
