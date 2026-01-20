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
        if not MO_INSTALLED:
            raise Exception("OpenVoice libraries not installed")
        
        if self.tone_color_converter is None:
            raise Exception("Voice processing models are not loaded yet. Please try again in a moment or trigger an audio generation first.")

        voice_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1]
        save_filename = f"{voice_id}{file_ext}"
        save_path = os.path.join(self.voices_dir, save_filename)
        se_path = os.path.join(self.voices_dir, f"{voice_id}_se.pth")

        # 1. Save audio file
        with open(save_path, "wb") as buffer:
            buffer.write(file_content)

        try:
            # 2. Extract Tone Color Embedding (SE)
            # Use OpenVoice's se_extractor
            try:
                # 尝试使用VAD方法（更快，但需要足够长的音频）
                target_se, audio_name = se_extractor.get_se(save_path, self.tone_color_converter, target_dir=self.voices_dir, vad=True)
            except Exception as vad_error:
                logger.warning(f"VAD extraction failed ({vad_error}), retrying with Whisper method...")
                try:
                    # 使用Whisper方法（更慢，但对短音频更宽容）
                    # 注意：需要CPU模式，因为服务器没有CUDA
                    target_se, audio_name = se_extractor.get_se(save_path, self.tone_color_converter, target_dir=self.voices_dir, vad=False)
                except Exception as whisper_error:
                    logger.error(f"Whisper extraction also failed: {whisper_error}")
                    # 如果两种方法都失败，尝试直接提取（不使用VAD或Whisper）
                    try:
                        logger.info("Trying direct extraction without VAD/Whisper...")
                        target_se = self.tone_color_converter.extract_se(save_path)
                        audio_name = os.path.basename(save_path)
                        logger.info("Direct extraction successful!")
                    except Exception as direct_error:
                        logger.error(f"Direct extraction failed: {direct_error}")
                        raise Exception(f"无法提取声音特征。请确保：1) 音频文件至少3-5秒长 2) 音频清晰且包含人声 3) 音频格式正确（wav/mp3）。错误详情: VAD={vad_error}, Whisper={whisper_error}, Direct={direct_error}")

            # Note: se_extractor.get_se saves the se directly if target_dir is provided, 
            # but we want to control the filename or load it. 
            # Actually se_extractor.get_se returns (se, name). 
            # Let's look at how to save/load properly.
            # Usually we save it manually if needed, or just keep it in memory if we were a single session app.
            # For persistence, we save the tensor.
            
            torch.save(target_se, se_path)
            
            # 3. Update DB
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
            
            return new_voice

        except Exception as e:
            logger.error(f"Failed to extract voice features: {e}")
            # Cleanup
            if os.path.exists(save_path):
                os.remove(save_path)
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

