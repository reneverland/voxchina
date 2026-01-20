"""
口播稿生成 - 文档分块服务
实现智能分块、覆盖率跟踪
"""
from typing import List, Dict, Any
from loguru import logger


class ScriptChunkingService:
    """文档分块服务"""
    
    def __init__(self):
        self.chunk_size_min = 800    # 最小chunk大小（中文字符）
        self.chunk_size_max = 1500   # 目标chunk大小（中文字符）
        self.chunk_overlap = 150     # 重叠字符数
    
    def chunk_document(self, paragraphs: List[Dict[str, Any]], doc_id: str) -> Dict[str, Any]:
        """
        对单个文档进行分块
        
        Args:
            paragraphs: 段落列表（来自document_parser_service）
            doc_id: 文档标识符
            
        Returns:
            {
                "doc_id": str,
                "total_chunks": int,
                "chunks": [
                    {
                        "chunk_id": "doc1_c00",
                        "text": str,
                        "para_start": int,
                        "para_end": int,
                        "char_count": int
                    }
                ]
            }
        """
        chunks = []
        current_chunk_text = ""
        current_para_start = None
        current_para_end = None
        
        for para in paragraphs:
            para_text = para["text"]
            para_id = para["paragraph_id"]
            
            # 初始化第一个chunk
            if current_para_start is None:
                current_para_start = para_id
                current_chunk_text = para_text
                current_para_end = para_id
                continue
            
            # 尝试添加当前段落
            potential_text = current_chunk_text + "\n\n" + para_text
            potential_length = len(potential_text)
            
            # 如果超过目标大小且当前chunk已达最小值，保存当前chunk
            if potential_length > self.chunk_size_max and len(current_chunk_text) >= self.chunk_size_min:
                chunks.append({
                    "chunk_id": f"{doc_id}_c{len(chunks):02d}",
                    "text": current_chunk_text,
                    "para_start": current_para_start,
                    "para_end": current_para_end,
                    "char_count": len(current_chunk_text)
                })
                
                # 开始新chunk（带overlap）
                # 简化处理：从当前段落开始
                current_chunk_text = para_text
                current_para_start = para_id
                current_para_end = para_id
            else:
                # 继续累加到当前chunk
                current_chunk_text = potential_text
                current_para_end = para_id
        
        # 保存最后一个chunk
        if current_chunk_text:
            chunks.append({
                "chunk_id": f"{doc_id}_c{len(chunks):02d}",
                "text": current_chunk_text,
                "para_start": current_para_start,
                "para_end": current_para_end,
                "char_count": len(current_chunk_text)
            })
        
        logger.info(f"Document {doc_id} chunked into {len(chunks)} chunks")
        
        return {
            "doc_id": doc_id,
            "total_chunks": len(chunks),
            "chunks": chunks
        }
    
    def verify_coverage(self, chunking_result: Dict[str, Any], total_paragraphs: int) -> Dict[str, Any]:
        """
        验证分块覆盖率
        
        Args:
            chunking_result: 分块结果
            total_paragraphs: 原文总段落数
            
        Returns:
            {
                "is_complete": bool,
                "covered_paragraphs": int,
                "total_paragraphs": int,
                "coverage_rate": float,
                "missing_ranges": List[tuple]  # 如果有缺失
            }
        """
        chunks = chunking_result["chunks"]
        covered = set()
        
        for chunk in chunks:
            para_start = chunk["para_start"]
            para_end = chunk["para_end"]
            for p in range(para_start, para_end + 1):
                covered.add(p)
        
        coverage_rate = len(covered) / total_paragraphs if total_paragraphs > 0 else 0
        is_complete = coverage_rate >= 0.95  # 允许5%的页眉页脚等噪音段落
        
        # 查找缺失段落范围
        missing_ranges = []
        all_paras = set(range(total_paragraphs))
        missing = sorted(all_paras - covered)
        
        if missing:
            range_start = missing[0]
            range_end = missing[0]
            for p in missing[1:]:
                if p == range_end + 1:
                    range_end = p
                else:
                    missing_ranges.append((range_start, range_end))
                    range_start = p
                    range_end = p
            missing_ranges.append((range_start, range_end))
        
        result = {
            "is_complete": is_complete,
            "covered_paragraphs": len(covered),
            "total_paragraphs": total_paragraphs,
            "coverage_rate": round(coverage_rate, 3),
            "missing_ranges": missing_ranges
        }
        
        if not is_complete:
            logger.warning(f"Coverage incomplete: {coverage_rate:.1%}, missing: {missing_ranges}")
        else:
            logger.info(f"Coverage verified: {coverage_rate:.1%}")
        
        return result


script_chunking_service = ScriptChunkingService()

