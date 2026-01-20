import os
import torch
from loguru import logger
import soundfile as sf

# Try imports
try:
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    from melo.api import TTS
    MO_INSTALLED = True
except Exception as e:
    logger.warning(f"OpenVoice/MeloTTS dependencies not found or failed to load (run in limited mode): {e}")
    MO_INSTALLED = False

class TTSService:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.output_dir = "static/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.loaded = False
        self.tone_color_converter = None
        self.model = None
        self.speaker_ids = None

    def load_models(self):
        if self.loaded or not MO_INSTALLED:
            return

        try:
            # Checkpoints path
            ckpt_converter = 'OpenVoice/checkpoints_v2/converter'
            
            # Initialize Tone Color Converter (禁用水印功能避免下载WavMark模型)
            self.tone_color_converter = ToneColorConverter(
                f'{ckpt_converter}/config.json', 
                device=self.device,
                enable_watermark=False  # 禁用音频水印，避免下载额外模型
            )
            self.tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

            # Initialize MeloTTS (using Chinese by default for VoxChina)
            self.model = TTS(language='ZH', device=self.device)
            self.speaker_ids = self.model.hps.data.spk2id
            
            self.loaded = True
            
            # Inject converter into VoiceService
            from app.services.voice_service import voice_service
            voice_service.set_converter(self.tone_color_converter)
            
            logger.info("OpenVoice V2 models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load OpenVoice models: {e}")

    def generate_audio(self, text: str, output_filename: str, speed: float = 1.0, voice_id: str = None):
        if not MO_INSTALLED:
            logger.error("[TTS] ❌ TTS dependencies not installed (MeloTTS/OpenVoice)")
            return None

        if not self.loaded:
            logger.info("[TTS] Models not loaded yet, loading now...")
            try:
                self.load_models()
            except Exception as load_error:
                logger.error(f"[TTS] ❌ Failed to load models: {load_error}")
                import traceback
                logger.error(f"[TTS] Traceback: {traceback.format_exc()}")
                return None
                
            if not self.loaded:
                logger.error("[TTS] ❌ Models failed to load after attempt")
                return None

        logger.info(f"[TTS] 🎤 Starting audio generation: text_length={len(text)}, voice_id={voice_id}, filename={output_filename}")
        
        try:
            # Temporary path for base audio
            tmp_path = f"{self.output_dir}/tmp_{output_filename}"
            final_path = f"{self.output_dir}/{output_filename}"
            
            # 1. Generate base audio with MeloTTS (Source Voice)
            # We use standard ZH voice as source
            speaker_key = 'ZH' 
            speaker_id = self.speaker_ids[speaker_key]
            
            logger.info(f"[TTS] 🔊 Generating base audio with MeloTTS: speaker={speaker_key}, id={speaker_id}")
            
            # Note: MeloTTS tts_to_file generates audio.
            # For OpenVoice conversion, we need the source SE (Speaker Embedding).
            # OpenVoice V2 MeloTTS uses a default source SE which is handled internally or can be extracted.
            # For simplicity, we generate base audio first.
            try:
                self.model.tts_to_file(text, speaker_id, tmp_path, speed=speed)
            except Exception as tts_error:
                logger.error(f"[TTS] ❌ MeloTTS generation failed: {tts_error}")
                import traceback
                logger.error(f"[TTS] Traceback: {traceback.format_exc()}")
                return None
            
            if not os.path.exists(tmp_path):
                logger.error(f"[TTS] ❌ Base audio file not created: {tmp_path}")
                return None
            
            logger.info(f"[TTS] ✅ Base audio generated successfully: {tmp_path}")

            # 2. Tone Color Conversion (if voice_id provided)
            if voice_id:
                try:
                    logger.info(f"[TTS] 🎨 Starting voice conversion for voice_id: {voice_id}")
                    from app.services.voice_service import voice_service
                    target_voice = voice_service.get_voice(voice_id)
                    
                    if not target_voice:
                        logger.warning(f"[TTS] ⚠️ Voice {voice_id} not found, using default voice")
                    elif not os.path.exists(target_voice['se_path']):
                        logger.warning(f"[TTS] ⚠️ SE file not found: {target_voice['se_path']}, using default voice")
                    else:
                        logger.info(f"[TTS] 📁 Loading target SE from: {target_voice['se_path']}")
                        # Load Target SE
                        try:
                            target_se = torch.load(target_voice['se_path'], map_location=self.device)
                        except Exception as se_load_error:
                            logger.error(f"[TTS] ❌ Failed to load target SE: {se_load_error}")
                            raise
                        
                        logger.info("[TTS] 🔍 Extracting source SE from generated audio...")
                        # Get Source SE (from the generated tmp_path)
                        # Note: Ideally we pre-compute source_se for the base speaker to save time, 
                        # but extracting from generated audio ensures match.
                        try:
                            source_se, _ = se_extractor.get_se(tmp_path, self.tone_color_converter, target_dir=self.output_dir)
                        except Exception as se_extract_error:
                            logger.error(f"[TTS] ❌ Failed to extract source SE: {se_extract_error}")
                            raise
                        
                        logger.info("[TTS] 🔄 Running tone color conversion...")
                        # Run Conversion
                        # encode_message allows for watermarking, we skip for now
                        convert_path = f"{self.output_dir}/conv_{output_filename}"
                        try:
                            self.tone_color_converter.convert(
                                audio_src_path=tmp_path, 
                                src_se=source_se, 
                                tgt_se=target_se, 
                                output_path=convert_path,
                                message="@VoxChina" # Optional Watermark
                            )
                        except Exception as convert_error:
                            logger.error(f"[TTS] ❌ Tone color conversion failed: {convert_error}")
                            raise
                        
                        # Replace final path with converted file
                        if os.path.exists(convert_path):
                            logger.info(f"[TTS] ✅ Voice conversion successful: {convert_path}")
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                            os.rename(convert_path, final_path)
                            logger.info(f"[TTS] ✅ Audio generation complete: {final_path}")
                            return final_path
                        else:
                            logger.error(f"[TTS] ❌ Conversion output not found: {convert_path}")
                except Exception as voice_e:
                    logger.error(f"[TTS] ❌ Voice conversion failed, falling back to default voice: {voice_e}")
                    import traceback
                    logger.error(f"[TTS] Traceback: {traceback.format_exc()}")
            
            # If no voice_id or conversion failed, just use base audio
            if os.path.exists(tmp_path):
                logger.info(f"[TTS] 📦 Using base audio (no conversion): {tmp_path} -> {final_path}")
                os.rename(tmp_path, final_path)
            
            if os.path.exists(final_path):
                logger.info(f"[TTS] ✅ Audio generation complete: {final_path}")
                return final_path
            else:
                logger.error(f"[TTS] ❌ Final audio file not found: {final_path}")
                return None
            
        except Exception as e:
            logger.error(f"[TTS] ❌ TTS Generation failed: {e}")
            import traceback
            logger.error(f"[TTS] Traceback: {traceback.format_exc()}")
            return None

tts_service = TTSService()
