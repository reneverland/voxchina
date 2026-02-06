"""
Qwen3-TTS Service for VoxChina
基于 Qwen3-TTS 的语音克隆服务
作者：Ren CBIT https://github.com/reneverland/
"""

import os
import re
import torch
import soundfile as sf
from loguru import logger
from typing import Optional, Tuple, List
import numpy as np

# 长文本分段阈值（字符数）
MAX_TEXT_LENGTH = 500  # Qwen3-TTS 对于过长文本可能会超时，分段处理

# Qwen3-TTS 模型路径
QWEN3_TTS_MODEL_PATH = "/www/wwwroot/voxchina/backend/models/qwen3-tts/Qwen3-TTS-12Hz-1.7B-Base"
QWEN3_TTS_TOKENIZER_PATH = "/www/wwwroot/voxchina/backend/models/qwen3-tts/Qwen3-TTS-Tokenizer-12Hz"

# 尝试导入 qwen_tts
QWEN3_TTS_AVAILABLE = False
try:
    from qwen_tts import Qwen3TTSModel
    QWEN3_TTS_AVAILABLE = True
    logger.info("✅ [Qwen3TTS] qwen_tts package imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ [Qwen3TTS] qwen_tts package not available: {e}")


class Qwen3TTSService:
    """Qwen3-TTS 语音克隆服务"""
    
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.output_dir = "static/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.model = None
        self.loaded = False
        self._voice_prompts = {}  # 缓存已创建的 voice_clone_prompt
        
        logger.info(f"[Qwen3TTS] Initialized with device: {self.device}")
    
    def load_model(self):
        """加载 Qwen3-TTS 模型"""
        if self.loaded:
            logger.info("[Qwen3TTS] Model already loaded, skipping")
            return True
        
        if not QWEN3_TTS_AVAILABLE:
            logger.error("[Qwen3TTS] qwen_tts package not available")
            return False
        
        try:
            logger.info(f"[Qwen3TTS] Loading model from: {QWEN3_TTS_MODEL_PATH}")
            
            # 检查模型文件是否存在
            if not os.path.exists(QWEN3_TTS_MODEL_PATH):
                logger.error(f"[Qwen3TTS] Model path not found: {QWEN3_TTS_MODEL_PATH}")
                return False
            
            # 加载模型
            self.model = Qwen3TTSModel.from_pretrained(
                QWEN3_TTS_MODEL_PATH,
                device_map=self.device,
                dtype=torch.bfloat16,
            )
            
            self.loaded = True
            logger.info("✅ [Qwen3TTS] Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ [Qwen3TTS] Failed to load model: {e}")
            import traceback
            logger.error(f"[Qwen3TTS] Traceback: {traceback.format_exc()}")
            return False
    
    def create_voice_prompt(self, voice_id: str, ref_audio_path: str, ref_text: str = "") -> bool:
        """
        为指定的声音创建可复用的 voice_clone_prompt
        
        Args:
            voice_id: 声音ID
            ref_audio_path: 参考音频文件路径
            ref_text: 参考音频的文本内容（可选，但提供会提高克隆质量）
        
        Returns:
            是否成功创建
        """
        if not self.loaded:
            if not self.load_model():
                return False
        
        try:
            logger.info(f"[Qwen3TTS] Creating voice prompt for voice_id: {voice_id}")
            logger.info(f"[Qwen3TTS] ref_audio_path: {ref_audio_path}")
            logger.info(f"[Qwen3TTS] ref_text: {ref_text[:50]}..." if ref_text else "[Qwen3TTS] ref_text: (empty)")
            
            # 创建 voice_clone_prompt
            # 如果没有提供 ref_text，使用 x_vector_only_mode
            if ref_text:
                prompt = self.model.create_voice_clone_prompt(
                    ref_audio=ref_audio_path,
                    ref_text=ref_text,
                    x_vector_only_mode=False,
                )
            else:
                prompt = self.model.create_voice_clone_prompt(
                    ref_audio=ref_audio_path,
                    ref_text="",
                    x_vector_only_mode=True,
                )
            
            # 缓存 prompt
            self._voice_prompts[voice_id] = prompt
            logger.info(f"✅ [Qwen3TTS] Voice prompt created and cached for: {voice_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ [Qwen3TTS] Failed to create voice prompt: {e}")
            import traceback
            logger.error(f"[Qwen3TTS] Traceback: {traceback.format_exc()}")
            return False
    
    def _split_text_into_segments(self, text: str, max_length: int = MAX_TEXT_LENGTH) -> List[str]:
        """
        将长文本分割成多个段落
        
        按句子边界分割，确保每段不超过 max_length
        """
        if len(text) <= max_length:
            return [text]
        
        # 按句子分割（中英文标点）
        sentence_endings = r'[。！？.!?\n]+'
        sentences = re.split(f'({sentence_endings})', text)
        
        # 重新组合句子和标点
        combined = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            ending = sentences[i + 1] if i + 1 < len(sentences) else ''
            combined.append(sentence + ending)
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            combined.append(sentences[-1])
        
        # 合并成段落
        segments = []
        current_segment = ""
        
        for sentence in combined:
            if not sentence.strip():
                continue
            
            if len(current_segment) + len(sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment.strip():
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment.strip():
            segments.append(current_segment.strip())
        
        # 如果分割后仍有超长段落，强制按长度切分
        final_segments = []
        for seg in segments:
            if len(seg) <= max_length:
                final_segments.append(seg)
            else:
                # 强制切分
                for i in range(0, len(seg), max_length):
                    final_segments.append(seg[i:i + max_length])
        
        logger.info(f"[Qwen3TTS] Split text into {len(final_segments)} segments")
        return final_segments

    def generate_audio(
        self, 
        text: str, 
        output_filename: str, 
        voice_id: str = None,
        ref_audio_path: str = None,
        ref_text: str = "",
        language: str = "Chinese",
        speed: float = 1.0
    ) -> Optional[str]:
        """
        使用 Qwen3-TTS 生成语音
        
        Args:
            text: 要合成的文本
            output_filename: 输出文件名
            voice_id: 声音ID（如果已缓存 prompt）
            ref_audio_path: 参考音频路径（如果没有缓存 prompt）
            ref_text: 参考音频文本
            language: 语言 (Chinese, English, Japanese, Korean, etc.)
            speed: 语速（目前 Qwen3-TTS 不直接支持，保留参数）
        
        Returns:
            生成的音频文件路径，失败返回 None
        """
        if not self.loaded:
            logger.info("[Qwen3TTS] Model not loaded, loading now...")
            if not self.load_model():
                logger.error("[Qwen3TTS] Failed to load model")
                return None
        
        logger.info(f"[Qwen3TTS] 🎤 Generating audio: text_length={len(text)}, voice_id={voice_id}")
        
        try:
            final_path = os.path.join(self.output_dir, output_filename)
            
            # 获取或创建 voice_clone_prompt
            voice_prompt = None
            
            if voice_id and voice_id in self._voice_prompts:
                # 使用缓存的 prompt
                voice_prompt = self._voice_prompts[voice_id]
                logger.info(f"[Qwen3TTS] Using cached voice prompt for: {voice_id}")
            elif ref_audio_path:
                # 即时创建 prompt
                logger.info(f"[Qwen3TTS] Creating voice prompt on-the-fly from: {ref_audio_path}")
                if ref_text:
                    voice_prompt = self.model.create_voice_clone_prompt(
                        ref_audio=ref_audio_path,
                        ref_text=ref_text,
                        x_vector_only_mode=False,
                    )
                else:
                    voice_prompt = self.model.create_voice_clone_prompt(
                        ref_audio=ref_audio_path,
                        ref_text="",
                        x_vector_only_mode=True,
                    )
                
                # 如果有 voice_id，缓存起来
                if voice_id:
                    self._voice_prompts[voice_id] = voice_prompt
            
            if voice_prompt is None:
                logger.error("[Qwen3TTS] No voice prompt available (no voice_id or ref_audio_path)")
                return None
            
            # 检查是否需要分段处理
            if len(text) > MAX_TEXT_LENGTH:
                logger.info(f"[Qwen3TTS] Long text detected ({len(text)} chars), using segmented generation")
                return self._generate_audio_segmented(
                    text=text,
                    output_filename=output_filename,
                    voice_prompt=voice_prompt,
                    language=language,
                    final_path=final_path
                )
            
            # 短文本：直接生成
            logger.info(f"[Qwen3TTS] Generating voice clone with language: {language}")
            wavs, sr = self.model.generate_voice_clone(
                text=text,
                language=language,
                voice_clone_prompt=voice_prompt,
            )
            
            # 保存音频
            sf.write(final_path, wavs[0], sr)
            logger.info(f"✅ [Qwen3TTS] Audio saved to: {final_path}")
            
            return final_path
            
        except Exception as e:
            logger.error(f"❌ [Qwen3TTS] Audio generation failed: {e}")
            import traceback
            logger.error(f"[Qwen3TTS] Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_audio_segmented(
        self,
        text: str,
        output_filename: str,
        voice_prompt,
        language: str,
        final_path: str
    ) -> Optional[str]:
        """
        分段生成长文本的音频，然后合并
        """
        try:
            segments = self._split_text_into_segments(text)
            logger.info(f"[Qwen3TTS] Processing {len(segments)} segments...")
            
            all_audio = []
            sr = None
            
            for i, segment in enumerate(segments):
                logger.info(f"[Qwen3TTS] Generating segment {i+1}/{len(segments)} ({len(segment)} chars)")
                
                try:
                    wavs, sample_rate = self.model.generate_voice_clone(
                        text=segment,
                        language=language,
                        voice_clone_prompt=voice_prompt,
                    )
                    
                    if sr is None:
                        sr = sample_rate
                    
                    all_audio.append(wavs[0])
                    logger.info(f"[Qwen3TTS] ✅ Segment {i+1} completed")
                    
                except Exception as seg_error:
                    logger.error(f"[Qwen3TTS] ❌ Segment {i+1} failed: {seg_error}")
                    # 继续处理其他段落
                    continue
            
            if not all_audio:
                logger.error("[Qwen3TTS] No audio segments generated successfully")
                return None
            
            # 合并所有音频段落
            logger.info(f"[Qwen3TTS] Concatenating {len(all_audio)} audio segments...")
            
            # 在段落之间添加短暂停顿（0.3秒静音）
            silence_duration = int(sr * 0.3)
            silence = np.zeros(silence_duration, dtype=np.float32)
            
            combined_audio = []
            for i, audio in enumerate(all_audio):
                combined_audio.append(audio)
                if i < len(all_audio) - 1:
                    combined_audio.append(silence)
            
            final_audio = np.concatenate(combined_audio)
            
            # 保存合并后的音频
            sf.write(final_path, final_audio, sr)
            logger.info(f"✅ [Qwen3TTS] Segmented audio saved to: {final_path} (total {len(final_audio)/sr:.1f}s)")
            
            return final_path
            
        except Exception as e:
            logger.error(f"❌ [Qwen3TTS] Segmented generation failed: {e}")
            import traceback
            logger.error(f"[Qwen3TTS] Traceback: {traceback.format_exc()}")
            return None
    
    def clear_voice_prompt(self, voice_id: str):
        """清除指定声音的缓存 prompt"""
        if voice_id in self._voice_prompts:
            del self._voice_prompts[voice_id]
            logger.info(f"[Qwen3TTS] Cleared voice prompt cache for: {voice_id}")
    
    def is_available(self) -> bool:
        """检查 Qwen3-TTS 是否可用"""
        return QWEN3_TTS_AVAILABLE and os.path.exists(QWEN3_TTS_MODEL_PATH)


# 全局单例
qwen3_tts_service = Qwen3TTSService()
