import os
import torch
from loguru import logger
import soundfile as sf

# ============================================================================
# TTS 引擎配置
# 可选: "qwen3" (推荐，更好的克隆效果) 或 "openvoice" (旧版备选)
# ============================================================================
TTS_ENGINE = os.environ.get("TTS_ENGINE", "qwen3")  # 默认使用 Qwen3-TTS

# Try imports - OpenVoice (备选)
MO_INSTALLED = False
try:
    import sys
    logger.info(f"[TTS Init] Current directory: {os.getcwd()}")
    logger.info(f"[TTS Init] Python path: {sys.path[:3]}")
    logger.info(f"[TTS Init] Attempting to import OpenVoice...")
    
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    from melo.api import TTS
    
    MO_INSTALLED = True
    logger.info(f"✅ [TTS Init] OpenVoice/MeloTTS imported successfully")
except Exception as e:
    logger.warning(f"⚠️ [TTS Init] OpenVoice/MeloTTS not available: {e}")

# Try imports - Qwen3-TTS (推荐)
QWEN3_TTS_AVAILABLE = False
try:
    from app.services.qwen3_tts_service import qwen3_tts_service, QWEN3_TTS_AVAILABLE as _QWEN3_AVAIL
    QWEN3_TTS_AVAILABLE = _QWEN3_AVAIL and qwen3_tts_service.is_available()
    if QWEN3_TTS_AVAILABLE:
        logger.info(f"✅ [TTS Init] Qwen3-TTS available and ready")
    else:
        logger.warning(f"⚠️ [TTS Init] Qwen3-TTS package available but model not found")
except Exception as e:
    logger.warning(f"⚠️ [TTS Init] Qwen3-TTS not available: {e}")

# 确定使用哪个引擎
if TTS_ENGINE == "qwen3" and QWEN3_TTS_AVAILABLE:
    ACTIVE_ENGINE = "qwen3"
    logger.info(f"🎯 [TTS Init] Using Qwen3-TTS as primary TTS engine")
elif MO_INSTALLED:
    ACTIVE_ENGINE = "openvoice"
    logger.info(f"🎯 [TTS Init] Using OpenVoice as TTS engine (Qwen3 not available)")
else:
    ACTIVE_ENGINE = None
    logger.error(f"❌ [TTS Init] No TTS engine available!")

class TTSService:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.output_dir = "static/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.loaded = False
        self.tone_color_converter = None
        self.model = None
        self.speaker_ids = None
        self.active_engine = ACTIVE_ENGINE
        
        logger.info(f"[TTS] Initialized with engine: {self.active_engine}, device: {self.device}")

    def load_models(self):
        if self.loaded:
            logger.info("[TTS] Models already loaded, skipping")
            return
        
        # 根据活动引擎加载模型
        if self.active_engine == "qwen3":
            self._load_qwen3_models()
        elif self.active_engine == "openvoice":
            self._load_openvoice_models()
        else:
            logger.error("[TTS] No TTS engine available to load")
    
    def _load_qwen3_models(self):
        """加载 Qwen3-TTS 模型"""
        try:
            logger.info("[TTS] Loading Qwen3-TTS models...")
            from app.services.qwen3_tts_service import qwen3_tts_service
            
            if qwen3_tts_service.load_model():
                self.loaded = True
                logger.info("✅ [TTS] Qwen3-TTS models loaded successfully")
                
                # 同时加载 OpenVoice 的 converter 用于 voice_service 的 SE 提取（如果可用）
                # 这样可以保持与现有声音库的兼容性
                if MO_INSTALLED:
                    try:
                        self._load_openvoice_converter_only()
                    except Exception as e:
                        logger.warning(f"[TTS] OpenVoice converter not loaded (optional): {e}")
            else:
                logger.error("[TTS] Failed to load Qwen3-TTS, falling back to OpenVoice")
                self.active_engine = "openvoice"
                self._load_openvoice_models()
                
        except Exception as e:
            logger.error(f"[TTS] Qwen3-TTS loading failed: {e}")
            import traceback
            logger.error(f"[TTS] Traceback: {traceback.format_exc()}")
            # 回退到 OpenVoice
            if MO_INSTALLED:
                logger.info("[TTS] Falling back to OpenVoice...")
                self.active_engine = "openvoice"
                self._load_openvoice_models()
    
    def _load_openvoice_converter_only(self):
        """仅加载 OpenVoice 的 ToneColorConverter（用于 SE 提取）"""
        ckpt_converter = 'OpenVoice/checkpoints_v2/converter'
        self.tone_color_converter = ToneColorConverter(
            f'{ckpt_converter}/config.json', 
            device=self.device,
            enable_watermark=False
        )
        self.tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
        
        # Inject converter into VoiceService
        from app.services.voice_service import voice_service
        voice_service.set_converter(self.tone_color_converter)
        logger.info("[TTS] OpenVoice converter loaded for SE extraction")
    
    def _load_openvoice_models(self):
        """加载 OpenVoice 模型（完整版）"""
        if not MO_INSTALLED:
            logger.warning("[TTS] OpenVoice/MeloTTS not installed, cannot load models")
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
            
            logger.info("✅ [TTS] OpenVoice V2 models loaded successfully")
        except Exception as e:
            logger.error(f"[TTS] Failed to load OpenVoice models: {e}")

    def generate_audio(self, text: str, output_filename: str, speed: float = 1.0, voice_id: str = None, language: str = "Chinese"):
        """
        生成语音音频
        
        Args:
            text: 要合成的文本
            output_filename: 输出文件名
            speed: 语速（仅 OpenVoice 支持）
            voice_id: 声音ID
            language: 语言 (Chinese, English, etc.)
        """
        if self.active_engine is None:
            logger.error("[TTS] ❌ No TTS engine available")
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

        logger.info(f"[TTS] 🎤 Starting audio generation (engine={self.active_engine}): text_length={len(text)}, voice_id={voice_id}, filename={output_filename}")
        
        # 使用 Qwen3-TTS 引擎
        if self.active_engine == "qwen3":
            return self._generate_with_qwen3(text, output_filename, voice_id, language)
        
        # 使用 OpenVoice 引擎（原有逻辑）
        return self._generate_with_openvoice(text, output_filename, speed, voice_id)
    
    def _generate_with_qwen3(self, text: str, output_filename: str, voice_id: str = None, language: str = "Chinese"):
        """使用 Qwen3-TTS 生成语音"""
        try:
            from app.services.qwen3_tts_service import qwen3_tts_service
            from app.services.voice_service import voice_service
            
            # 获取参考音频路径
            ref_audio_path = None
            ref_text = ""
            
            if voice_id:
                target_voice = voice_service.get_voice(voice_id)
                if target_voice:
                    # 使用原始音频文件作为参考
                    audio_url = target_voice.get('audio_url', '')
                    if audio_url:
                        ref_audio_path = os.path.join("static/voices", os.path.basename(audio_url))
                        if not os.path.exists(ref_audio_path):
                            ref_audio_path = audio_url.lstrip('/')
                    
                    # 获取参考文本（如果有）
                    ref_text = target_voice.get('ref_text', '')
                    
                    logger.info(f"[TTS-Qwen3] Using voice: {target_voice.get('name')}, ref_audio: {ref_audio_path}")
                else:
                    logger.warning(f"[TTS-Qwen3] Voice {voice_id} not found, generating without voice clone")
            
            # 生成音频
            result = qwen3_tts_service.generate_audio(
                text=text,
                output_filename=output_filename,
                voice_id=voice_id,
                ref_audio_path=ref_audio_path,
                ref_text=ref_text,
                language=language,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[TTS-Qwen3] Generation failed: {e}")
            import traceback
            logger.error(f"[TTS-Qwen3] Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_with_openvoice(self, text: str, output_filename: str, speed: float = 1.0, voice_id: str = None):
        """使用 OpenVoice 生成语音（原有逻辑）"""
        if not MO_INSTALLED:
            logger.error("[TTS] ❌ OpenVoice not installed")
            return None
        
        if self.model is None or self.speaker_ids is None:
            logger.error("[TTS] ❌ OpenVoice MeloTTS model not loaded")
            return None
        
        try:
            # Temporary path for base audio
            tmp_path = f"{self.output_dir}/tmp_{output_filename}"
            final_path = f"{self.output_dir}/{output_filename}"
            
            # 1. Generate base audio with MeloTTS (Source Voice)
            # We use standard ZH voice as source
            speaker_key = 'ZH' 
            speaker_id = self.speaker_ids[speaker_key]
            
            logger.info(f"[TTS-OpenVoice] 🔊 Generating base audio with MeloTTS: speaker={speaker_key}, id={speaker_id}")
            
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
                logger.info(f"[TTS] ========== VOICE CONVERSION START ==========")
                try:
                    logger.info(f"[TTS] 🎨 Starting voice conversion for voice_id: {voice_id}")
                    from app.services.voice_service import voice_service
                    target_voice = voice_service.get_voice(voice_id)
                    
                    logger.info(f"[TTS] Target voice lookup result: {target_voice}")
                    
                    if not target_voice:
                        logger.warning(f"[TTS] ⚠️ Voice {voice_id} not found in database, using default voice")
                    elif not os.path.exists(target_voice['se_path']):
                        logger.warning(f"[TTS] ⚠️ SE file not found: {target_voice['se_path']}, using default voice")
                    else:
                        logger.info(f"[TTS] ✅ Target voice found: {target_voice['name']}, SE path: {target_voice['se_path']}")
                        logger.info(f"[TTS] 📁 Loading target SE from: {target_voice['se_path']}")
                        # Load Target SE
                        try:
                            target_se = torch.load(target_voice['se_path'], map_location=self.device)
                        except Exception as se_load_error:
                            logger.error(f"[TTS] ❌ Failed to load target SE: {se_load_error}")
                            raise
                        
                        logger.info("[TTS] 🔍 Extracting source SE from generated audio...")
                        logger.info(f"[TTS]    Source audio path: {tmp_path}")
                        # Get Source SE (from the generated tmp_path)
                        # Note: Ideally we pre-compute source_se for the base speaker to save time, 
                        # but extracting from generated audio ensures match.
                        try:
                            # 使用VAD方法提取
                            logger.info(f"[TTS]    Attempting VAD extraction...")
                            try:
                                source_se, _ = se_extractor.get_se(tmp_path, self.tone_color_converter, target_dir=self.output_dir, vad=True)
                                logger.info(f"[TTS]    ✅ VAD extraction successful")
                            except Exception as vad_error:
                                logger.warning(f"[TTS]    VAD extraction failed: {vad_error}")
                                logger.info(f"[TTS]    Trying direct extraction (skipping Whisper due to CUDA issues)...")
                                # 直接提取，跳过Whisper
                                source_se = self.tone_color_converter.extract_se(tmp_path)
                                logger.info(f"[TTS]    ✅ Direct extraction successful")
                        except Exception as se_extract_error:
                            logger.error(f"[TTS] ❌ Failed to extract source SE: {se_extract_error}")
                            import traceback
                            logger.error(f"[TTS] ❌ Traceback:\n{traceback.format_exc()}")
                            raise
                        
                        logger.info("[TTS] 🔄 Running tone color conversion...")
                        logger.info(f"[TTS]    Source SE shape: {source_se.shape if hasattr(source_se, 'shape') else 'N/A'}")
                        logger.info(f"[TTS]    Target SE shape: {target_se.shape if hasattr(target_se, 'shape') else 'N/A'}")
                        # Run Conversion
                        # encode_message allows for watermarking, we skip for now
                        convert_path = f"{self.output_dir}/conv_{output_filename}"
                        logger.info(f"[TTS]    Conversion output path: {convert_path}")
                        try:
                            self.tone_color_converter.convert(
                                audio_src_path=tmp_path, 
                                src_se=source_se, 
                                tgt_se=target_se, 
                                output_path=convert_path,
                                message="@VoxChina" # Optional Watermark
                            )
                            logger.info(f"[TTS]    ✅ Conversion completed")
                        except Exception as convert_error:
                            logger.error(f"[TTS] ❌ Tone color conversion failed: {convert_error}")
                            import traceback
                            logger.error(f"[TTS] ❌ Traceback:\n{traceback.format_exc()}")
                            raise
                        
                        # Replace final path with converted file
                        if os.path.exists(convert_path):
                            logger.info(f"[TTS] ✅ Voice conversion successful: {convert_path}")
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                                logger.info(f"[TTS]    Removed temp file: {tmp_path}")
                            os.rename(convert_path, final_path)
                            logger.info(f"[TTS] ✅ Audio generation complete with voice conversion: {final_path}")
                            logger.info(f"[TTS] ========== VOICE CONVERSION SUCCESS ==========")
                            return final_path
                        else:
                            logger.error(f"[TTS] ❌ Conversion output not found: {convert_path}")
                except Exception as voice_e:
                    logger.error(f"[TTS] ❌ Voice conversion failed, falling back to default voice")
                    logger.error(f"[TTS] ❌ Error: {voice_e}")
                    import traceback
                    logger.error(f"[TTS] ❌ Traceback:\n{traceback.format_exc()}")
                    logger.info(f"[TTS] ========== VOICE CONVERSION FAILED ==========")
            else:
                logger.info(f"[TTS] No voice_id provided, using default voice")
            
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
