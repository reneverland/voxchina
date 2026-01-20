"""
VoxChina 统一内容生成器
统一入口：自动判断文档数量，选择单篇摘要或多篇口播模式
速度优先，但禁止编造数据
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 文档解析
from .document_parser import extract_text_from_doc, truncate_non_core_sections
from app.services.document_parser_service import document_parser_service
from app.services.academic_extract_service import academic_extract_service
# LLM 调用
from .llm_client import call_llm
# Prompt 模板
from .prompt_templates import (
    build_single_summary_prompt,
    build_quick_brief_prompt,
    build_final_script_prompt
)
# DOCX 导出
from .docx_exporter import export_to_docx


class VoxContentGenerator:
    """VoxChina 统一内容生成器"""
    
    def __init__(self, llm_provider="openai", model_name="gpt-4o", max_workers=5):
        """
        初始化生成器
        
        Args:
            llm_provider: LLM 提供商 (openai/anthropic/azure)
            model_name: 模型名称
            max_workers: 并行调用最大线程数
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.max_workers = max_workers
        
    def generate_vox_content(
        self,
        inputs: List[str],  # 文档路径列表
        options: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        统一入口：自动判断模式并生成内容
        
        Args:
            inputs: 文档路径列表（docx/doc/pdf）
            options: {
                'speaker_name': str,
                'speaker_affiliation': str,
                'topic_hint': str (可选),
                'duration_target_sec': int (默认150),
                'include_figure_placeholders': bool (默认True),
                'output_docx': str (输出路径，可选)
            }
            progress_callback: 回调函数 (step_name, progress_percent)
        
        Returns:
            {
                'mode': 'SINGLE_SUMMARY' | 'MULTI_SCRIPT',
                'content': str,  # 生成的内容文本
                'title': str (可选),
                'docx_path': str (如果 output_docx 指定),
                'processing_time_sec': float,
                'metadata': dict,
                'structured_fact_table': dict (Optional)
            }
        """
        start_time = time.time()
        
        # 参数校验
        if not inputs or len(inputs) == 0:
            raise ValueError("inputs 不能为空")
        
        # 默认 options
        if options is None:
            options = {}
        
        options.setdefault('speaker_name', '研究员')
        options.setdefault('speaker_affiliation', 'VoxChina')
        options.setdefault('topic_hint', '')
        options.setdefault('duration_target_sec', 150)
        options.setdefault('include_figure_placeholders', True)
        
        # Helper to call progress safely
        def report_progress(step: str, percent: int):
            if progress_callback:
                progress_callback(step, percent)
        
        # 判断模式
        num_docs = len(inputs)
        
        report_progress("文档获取与预处理", 10)
        
        if num_docs == 1:
            # 单篇摘要模式
            result = self._single_summary_mode(inputs[0], options, report_progress)
        else:
            # 多篇整合口播模式
            result = self._multi_script_mode(inputs, options, report_progress)
        
        # 计算耗时
        result['processing_time_sec'] = round(time.time() - start_time, 2)
        
        # 导出 DOCX
        if options.get('output_docx'):
            report_progress("准备输送结果", 92)
            docx_path = self._export_docx(result, options)
            result['docx_path'] = docx_path
            report_progress("准备输送结果", 98)
        
        report_progress("完成", 100)
        return result
    
    def _single_summary_mode(
        self,
        doc_path: str,
        options: Dict[str, Any],
        report_progress: Callable[[str, int], None]
    ) -> Dict[str, Any]:
        """
        单篇摘要模式：使用高精度文章提取服务
        完整流程：文档解析 → 分块 → 事实提取 → 合并 → 证据校验 → 生成摘要
        """
        print(f"[单篇摘要模式] 处理文档: {doc_path}")
        
        # 1. 文档解析（使用 document_parser_service）
        report_progress("文档获取与预处理", 10)
        print(f"  - 解析文档...")
        
        with open(doc_path, 'rb') as f:
            file_content = f.read()
        
        filename = os.path.basename(doc_path)
        
        report_progress("结构化解析与噪音过滤", 20)
        document_data = document_parser_service.parse_document(file_content, filename)
        
        print(f"  - 解析完成: 标题={document_data.get('title', 'N/A')[:30]}..., 段落数={len(document_data['paragraphs'])}")
        
        # 2-6. 使用 academic_extract_service 进行高精度提取
        report_progress("智能分块与覆盖率保障", 30)
        
        # 创建异步事件循环来运行 academic_extract_service（它是异步的）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 调用学术文章提取服务（带进度回调）
            print(f"  - 调用高精度学术文章提取服务...")
            
            extract_result = loop.run_until_complete(
                academic_extract_service.extract_academic_article(
                    document_data, 
                    progress_callback=report_progress
                )
            )
            
            # 提取结果
            validated_fact_table = extract_result.get('fact_table', {})
            
            summary_zh = extract_result.get('summary_zh', '')
            summary_en = extract_result.get('summary_en', '')
            title = document_data.get('title', '')
            
            # 添加详细日志
            print(f"[VoxGenerator] Extract result keys: {list(extract_result.keys())}")
            print(f"[VoxGenerator] Summary_zh type: {type(summary_zh)}, length: {len(summary_zh) if summary_zh else 0}")
            print(f"[VoxGenerator] Summary_en type: {type(summary_en)}, length: {len(summary_en) if summary_en else 0}")
            
            report_progress("准备输送结果", 90)
            
            print(f"  - 生成摘要字数: 中文{len(summary_zh) if summary_zh else 0}, 英文{len(summary_en) if summary_en else 0}")
            
            # 构建结构化事实表（适配前端显示格式）
            structured_data = self._adapt_fact_table_format(validated_fact_table)
            
            return {
                'mode': 'SINGLE_SUMMARY',
                'content': summary_zh,  # 保持向后兼容
                'summary_zh': summary_zh,
                'summary_en': summary_en,
                'title': title,
                'structured_fact_table': structured_data,
                'images': document_data.get('images', []),  # 传递提取的图片
                'metadata': {
                    'doc_path': doc_path,
                    'total_chunks': extract_result.get('total_chunks', 0),
                    'processed_chunks': extract_result.get('processed_chunks', 0)
                }
            }
            
        finally:
            loop.close()
    
    def _adapt_fact_table_format(self, fact_table: Dict[str, Any]) -> Dict[str, Any]:
        """
        将 academic_extract_service 的 FactTable 格式适配为前端显示格式
        """
        adapted = {
            'author_affiliation': '',
            'research_question': fact_table.get('research_question', ''),
            'core_findings': [],
            'mechanism_explanation': ''
        }
        
        # 作者信息
        authors = fact_table.get('authors_affiliations', [])
        if isinstance(authors, list) and len(authors) > 0:
            adapted['author_affiliation'] = '; '.join(authors)
        
        # 核心发现
        key_findings = fact_table.get('key_findings', [])
        if isinstance(key_findings, list):
            for finding in key_findings:
                core_finding = {
                    'finding': finding.get('finding', ''),
                    'source_snippet': finding.get('evidence_quote', ''),
                    'data_points': finding.get('effect_size', '')
                }
                adapted['core_findings'].append(core_finding)
        
        # 机制解释
        mechanisms = fact_table.get('mechanism', [])
        if isinstance(mechanisms, list) and len(mechanisms) > 0:
            adapted['mechanism_explanation'] = '; '.join([m.get('claim', '') for m in mechanisms])
        
        return adapted
    
    def _multi_script_mode(
        self,
        doc_paths: List[str],
        options: Dict[str, Any],
        report_progress: Callable[[str, int], None]
    ) -> Dict[str, Any]:
        """
        多篇整合口播模式：N+1 次 LLM 调用
        1) 每篇文档并行提取 QuickBrief (N 次)
        2) 整合生成 FinalScript (1 次)
        """
        print(f"[多篇口播模式] 处理 {len(doc_paths)} 篇文档")
        
        # ===== Step A: 并行提取 QuickBrief =====
        report_progress("文档获取与预处理", 15)
        print("\n[Step A] 并行提取每篇文档要点...")
        
        all_briefs = []
        total_docs = len(doc_paths)
        completed_docs = 0
        
        report_progress("结构化解析与噪音过滤", 25)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_doc = {
                executor.submit(self._extract_quick_brief, doc_path, idx): (doc_path, idx)
                for idx, doc_path in enumerate(doc_paths)
            }
            
            for future in as_completed(future_to_doc):
                doc_path, idx = future_to_doc[future]
                completed_docs += 1
                # Update progress based on completion (30% to 60%)
                current_progress = 30 + int((completed_docs / total_docs) * 30)
                report_progress("CBIT-LLM 语义分析", current_progress)
                
                try:
                    brief = future.result()
                    all_briefs.append((idx, brief))
                    print(f"  ✓ 文档 {idx+1}: {brief.get('title_guess', 'N/A')[:30]}... ({len(brief.get('bullets', []))} 条要点)")
                except Exception as e:
                    print(f"  ✗ 文档 {idx+1} 失败: {e}")
                    # 失败时创建空 brief
                    all_briefs.append((idx, {'doc_id': idx, 'title_guess': '', 'bullets': []}))
        
        # 按索引排序
        all_briefs.sort(key=lambda x: x[0])
        briefs_list = [b[1] for b in all_briefs]
        
        # ===== Step B: 整合生成 FinalScript =====
        report_progress("深度理解与事实提取", 65)
        print("\n[Step B] 整合生成最终口播稿...")
        
        # 计算目标字数范围
        duration_target = options['duration_target_sec']
        min_chars = int(duration_target * 5.5)
        max_chars = int(duration_target * 9)
        print(f"  - 目标时长: {duration_target}秒")
        print(f"  - 目标字数: {min_chars}-{max_chars}字")
        
        prompt_messages = build_final_script_prompt(
            briefs_list=briefs_list,
            speaker_name=options['speaker_name'],
            speaker_affiliation=options['speaker_affiliation'],
            duration_target_sec=duration_target,
            topic_hint=options.get('topic_hint', ''),
            include_figure_placeholders=options['include_figure_placeholders']
        )
        
        report_progress("证据一致性校验", 75)
        print(f"  - 调用 LLM ({self.model_name})...")
        llm_response = call_llm(
            provider=self.llm_provider,
            model=self.model_name,
            messages=prompt_messages,
            response_format="json"
        )
        
        report_progress("摘要生成与风格对齐", 85)
        
        # 解析响应
        try:
            parsed = json.loads(llm_response)
            script_text = parsed.get('script_text', llm_response)
            episode_title = parsed.get('episode_title', '')
        except json.JSONDecodeError:
            script_text = llm_response
            episode_title = ''
        
        actual_chars = len(script_text)
        print(f"  - 生成口播稿字数: {actual_chars}字 (目标: {min_chars}-{max_chars}字)")
        
        # 验证字数是否在合理范围内
        if actual_chars < min_chars * 0.8:
            print(f"  ⚠️ 警告: 字数偏少 ({actual_chars} < {int(min_chars * 0.8)})，可能不够{duration_target}秒")
        elif actual_chars > max_chars * 1.2:
            print(f"  ⚠️ 警告: 字数偏多 ({actual_chars} > {int(max_chars * 1.2)})，可能超过{duration_target}秒")
        
        # 收集所有文档的图片
        all_images = []
        for brief in briefs_list:
            if 'images' in brief:
                all_images.extend(brief['images'])
        
        return {
            'mode': 'MULTI_SCRIPT',
            'content': script_text,
            'title': episode_title,
            'images': all_images,  # 返回所有图片
            'metadata': {
                'num_docs': len(doc_paths),
                'doc_paths': doc_paths,
                'briefs': briefs_list
            }
        }
    
    def _extract_quick_brief(
        self,
        doc_path: str,
        doc_idx: int
    ) -> Dict[str, Any]:
        """
        提取单篇文档的 QuickBrief（要点列表）
        """
        # 解析文档 (改用 parse_document 以支持图片提取)
        with open(doc_path, 'rb') as f:
            file_content = f.read()
        filename = os.path.basename(doc_path)
        
        document_data = document_parser_service.parse_document(file_content, filename)
        
        # 重建文本用于 prompt
        doc_text = "\n".join([p['text'] for p in document_data['paragraphs']])
        doc_text_truncated = truncate_non_core_sections(doc_text, mode='moderate')
        
        # 提取图片
        images = document_data.get('images', [])
        
        # 构建 Prompt
        prompt_messages = build_quick_brief_prompt(
            doc_text=doc_text_truncated,
            doc_id=f"doc_{doc_idx}"
        )
        
        # 调用 LLM
        llm_response = call_llm(
            provider=self.llm_provider,
            model=self.model_name,
            messages=prompt_messages,
            response_format="json"
        )
        
        # 解析
        result = {}
        try:
            result = json.loads(llm_response)
        except json.JSONDecodeError:
            result = {
                'doc_id': f"doc_{doc_idx}",
                'title_guess': '',
                'bullets': [llm_response]
            }
            
        # 附加图片信息
        result['images'] = images
        return result
    
    def _export_docx(
        self,
        result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
        导出为 DOCX 文档
        """
        output_path = options.get('output_docx', 'output.docx')
        
        print(f"\n[导出 DOCX] {output_path}")
        
        docx_path = export_to_docx(
            content=result['content'],
            title=result.get('title', ''),
            mode=result['mode'],
            output_path=output_path,
            images=result.get('images', [])
        )
        
        print(f"  ✓ 已保存: {docx_path}")
        
        return docx_path


# ===== 便捷函数 =====

def generate_vox_content(
    inputs: List[str],
    options: Optional[Dict[str, Any]] = None,
    llm_provider: str = "openai",
    model_name: str = "gpt-4o-mini",
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> Dict[str, Any]:
    """
    便捷函数：统一入口生成内容
    
    示例：
        # 单篇摘要
        result = generate_vox_content(
            inputs=['paper1.pdf'],
            options={'output_docx': 'summary.docx'}
        )
        
        # 多篇口播
        result = generate_vox_content(
            inputs=['paper1.pdf', 'paper2.pdf', 'paper3.pdf'],
            options={
                'speaker_name': '张教授',
                'speaker_affiliation': '清华大学',
                'duration_target_sec': 180,
                'output_docx': 'script.docx'
            }
        )
    """
    generator = VoxContentGenerator(
        llm_provider=llm_provider,
        model_name=model_name
    )
    
    return generator.generate_vox_content(inputs, options, progress_callback)


if __name__ == "__main__":
    # 快速测试
    print("VoxChina 统一内容生成器")
    print("=" * 60)
    
    def on_progress(step, percent):
        print(f"[Progress] {percent}%: {step}")
    
    # 测试单篇模式
    test_single = False
    if test_single:
        result = generate_vox_content(
            inputs=['test_data/paper1.pdf'],
            options={'output_docx': 'output_single.docx'},
            progress_callback=on_progress
        )
        print(f"\n模式: {result['mode']}")
        print(f"标题: {result.get('title', 'N/A')}")
        print(f"内容预览:\n{result['content'][:200]}...")
        print(f"耗时: {result['processing_time_sec']}秒")
