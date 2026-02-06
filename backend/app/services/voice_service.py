import os
import json
import uuid
import shutil
import torch
import datetime
from loguru import logger
from typing import List, Optional, Dict

# Try imports
try:
    from openvoice import se_extractor
    MO_INSTALLED = True
except ImportError as e:
    logger.warning(f"OpenVoice dependencies not found: {e}")
    MO_INSTALLED = False

class VoiceService:
    def __init__(self):
        self.voices_dir = "static/voices"
        self.db_file = os.path.join(self.voices_dir, "voices.json")
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        os.makedirs(self.voices_dir, exist_ok=True)
        self._ensure_db()
        self.tone_color_converter = None

    def _ensure_db(self):
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump([], f)

    def _load_db(self) -> List[Dict]:
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_db(self, data: List[Dict]):
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)

    def list_voices(self) -> List[Dict]:
        return self._load_db()

    def get_voice(self, voice_id: str) -> Optional[Dict]:
        voices = self._load_db()
        for v in voices:
            if v['id'] == voice_id:
                return v
        return None

    async def add_voice(self, name: str, file_content: bytes, filename: str):
        logger.info(f"[VoiceService.add_voice] ========== START ==========")
        logger.info(f"[VoiceService.add_voice] name={name}, filename={filename}, size={len(file_content)} bytes")
        
        if not MO_INSTALLED:
            logger.error(f"[VoiceService.add_voice] OpenVoice not installed!")
            raise Exception("OpenVoice libraries not installed")
        
        logger.info(f"[VoiceService.add_voice] Checking tone_color_converter...")
        if self.tone_color_converter is None:
            logger.error(f"[VoiceService.add_voice] tone_color_converter is None!")
            raise Exception("Voice processing models are not loaded yet. Please try again in a moment or trigger an audio generation first.")
        
        logger.info(f"[VoiceService.add_voice] tone_color_converter OK")

        voice_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1]
        save_filename = f"{voice_id}{file_ext}"
        save_path = os.path.join(self.voices_dir, save_filename)
        se_path = os.path.join(self.voices_dir, f"{voice_id}_se.pth")
        
        logger.info(f"[VoiceService.add_voice] Generated voice_id={voice_id}")
        logger.info(f"[VoiceService.add_voice] save_path={save_path}")
        logger.info(f"[VoiceService.add_voice] se_path={se_path}")

        # 1. Save audio file
        logger.info(f"[VoiceService.add_voice] Step 1: Saving audio file...")
        with open(save_path, "wb") as buffer:
            buffer.write(file_content)
        logger.info(f"[VoiceService.add_voice] Audio file saved successfully")

        try:
            # 2. Extract Tone Color Embedding (SE)
            # Use OpenVoice's se_extractor
            logger.info(f"[VoiceService.add_voice] Step 2: Extracting tone color embedding...")
            try:
                # 尝试使用VAD方法（更快，但需要足够长的音频）
                logger.info(f"[VoiceService.add_voice] Trying VAD extraction method...")
                target_se, audio_name = se_extractor.get_se(save_path, self.tone_color_converter, target_dir=self.voices_dir, vad=True)
                logger.info(f"[VoiceService.add_voice] VAD extraction successful!")
            except Exception as vad_error:
                logger.warning(f"[VoiceService.add_voice] VAD extraction failed: {vad_error}")
                # 跳过Whisper方法（会导致CUDA/cuDNN崩溃），直接使用direct extraction
                logger.info("[VoiceService.add_voice] Trying direct extraction method (skipping Whisper due to CUDA issues)...")
                try:
                    target_se = self.tone_color_converter.extract_se(save_path)
                    audio_name = os.path.basename(save_path)
                    logger.info("[VoiceService.add_voice] Direct extraction successful!")
                except Exception as direct_error:
                    logger.error(f"[VoiceService.add_voice] Direct extraction failed: {direct_error}")
                    raise Exception(f"无法提取声音特征。请确保：1) 音频文件至少3秒长 2) 音频清晰且包含人声 3) 音频格式正确（wav/mp3）。错误详情: VAD={vad_error}, Direct={direct_error}")

            # Note: se_extractor.get_se saves the se directly if target_dir is provided, 
            # but we want to control the filename or load it. 
            # Actually se_extractor.get_se returns (se, name). 
            # Let's look at how to save/load properly.
            # Usually we save it manually if needed, or just keep it in memory if we were a single session app.
            # For persistence, we save the tensor.
            
            logger.info(f"[VoiceService.add_voice] Step 3: Saving SE tensor to {se_path}...")
            torch.save(target_se, se_path)
            logger.info(f"[VoiceService.add_voice] SE tensor saved successfully")
            
            # 3. Update DB
            logger.info(f"[VoiceService.add_voice] Step 4: Updating database...")
            new_voice = {
                "id": voice_id,
                "name": name,
                "audio_url": f"/static/voices/{save_filename}",
                "se_path": se_path,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            voices = self._load_db()
            voices.append(new_voice)
            self._save_db(voices)
            logger.info(f"[VoiceService.add_voice] Database updated successfully")
            
            logger.info(f"[VoiceService.add_voice] ========== SUCCESS: {voice_id} ==========")
            return new_voice

        except Exception as e:
            logger.error(f"[VoiceService.add_voice] ❌ Failed to extract voice features: {e}")
            import traceback
            logger.error(f"[VoiceService.add_voice] ❌ Traceback:\n{traceback.format_exc()}")
            # Cleanup
            logger.info(f"[VoiceService.add_voice] Cleaning up saved file: {save_path}")
            if os.path.exists(save_path):
                os.remove(save_path)
            logger.info(f"[VoiceService.add_voice] ========== FAILED ==========")
            raise Exception(f"Failed to process voice audio: {e}")

    def delete_voice(self, voice_id: str):
        voices = self._load_db()
        voice_to_delete = None
        updated_voices = []
        
        for v in voices:
            if v['id'] == voice_id:
                voice_to_delete = v
            else:
                updated_voices.append(v)
        
        if voice_to_delete:
            self._save_db(updated_voices)
            # Remove files
            try:
                audio_path = os.path.join(self.voices_dir, os.path.basename(voice_to_delete['audio_url']))
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if os.path.exists(voice_to_delete['se_path']):
                    os.remove(voice_to_delete['se_path'])
            except Exception as e:
                logger.error(f"Error cleaning up voice files: {e}")
            return True
        return False

    # Helper to inject converter dependency from TTSService (circular dep avoidance)
    def set_converter(self, converter):
        self.tone_color_converter = converter

voice_service = VoiceService()

