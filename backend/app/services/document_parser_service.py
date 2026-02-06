"""
文档解析服务 - 支持 DOCX/DOC/PDF
将文档转换为结构化JSON，保留段落序号和层次结构
"""
import re
from typing import List, Dict, Any
from loguru import logger
from docx import Document
from pypdf import PdfReader
import io
import uuid
from pathlib import Path


class DocumentParserService:
    """文档解析服务"""
    
    def __init__(self):
        # 过滤规则：明显无信息的段落模式
        self.noise_patterns = [
            r'^copyright\s*©',
            r'^©\s*\d{4}',
            r'^email\s*:',
            r'^e-mail\s*:',
            r'^tel\s*:',
            r'^phone\s*:',
            r'^fax\s*:',
            r'^\s*$',  # 空行
            r'^page\s+\d+',
            r'^\d+\s*/\s*\d+$',  # 页码
        ]
        
    def is_noise(self, text: str) -> bool:
        """判断是否为噪音段落"""
        text_lower = text.strip().lower()
        
        # 空段落
        if not text_lower:
            return True
        
        # 太短的段落（小于5个字符）
        if len(text_lower) < 5:
            return True
        
        # 匹配噪音模式
        for pattern in self.noise_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def extract_images_from_docx(self, doc_obj) -> List[Dict[str, str]]:
        """从文档对象中提取图片并保存"""
        images = []
        try:
            # 获取当前文件所在目录，向上两级到达backend目录
            current_file = Path(__file__)
            backend_dir = current_file.parent.parent.parent  # backend/
            save_dir = backend_dir / "static" / "images" / "extracted"
            
            # 确保目录存在
            try:
                save_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"图片保存目录: {save_dir}")
            except Exception as e:
                logger.error(f"无法创建图片保存目录: {e}")
                # 尝试备用路径
                try:
                    save_dir = Path("/www/wwwroot/voxchina/backend/static/images/extracted")
                    save_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(f"使用备用图片保存目录: {save_dir}")
                except Exception as e2:
                    logger.error(f"无法创建备用图片保存目录: {e2}")
                    return []
            
            # 遍历所有关系寻找图片
            processed_blobs = set()
            
            for rel in doc_obj.part.rels.values():
                if "image" in rel.target_ref:
                    if hasattr(rel, "target_part"):
                        try:
                            image_data = rel.target_part.blob
                            # 使用内容哈希去重
                            import hashlib
                            img_hash = hashlib.md5(image_data).hexdigest()
                            if img_hash in processed_blobs:
                                continue
                            processed_blobs.add(img_hash)

                            content_type = rel.target_part.content_type
                            
                            # 确定扩展名
                            ext = ".jpg"
                            if "png" in content_type: ext = ".png"
                            elif "jpeg" in content_type: ext = ".jpg"
                            elif "gif" in content_type: ext = ".gif"
                            
                            # 生成文件名
                            img_filename = f"img_{uuid.uuid4().hex[:12]}{ext}"
                            img_path = save_dir / img_filename
                            
                            # 保存文件
                            with open(img_path, "wb") as f:
                                f.write(image_data)
                                
                            images.append({
                                "url": f"/static/images/extracted/{img_filename}",
                                "path": str(img_path),
                                "filename": img_filename
                            })
                        except Exception as img_err:
                            logger.warning(f"Failed to save extracted image: {img_err}")
                            continue
                            
            logger.info(f"Extracted {len(images)} images from document")
        except Exception as e:
            logger.error(f"提取图片整体流程失败: {e}")
            
        return images

    def parse_docx(self, file_content: bytes) -> Dict[str, Any]:
        """解析DOCX文档"""
        try:
            doc = Document(io.BytesIO(file_content))
            
            # 提取图片
            extracted_images = self.extract_images_from_docx(doc)
            
            title = ""
            paragraphs = []
            paragraph_id = 0
            
            for idx, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                
                # 跳过噪音段落
                if self.is_noise(text):
                    continue
                
                # 第一个非空段落作为标题
                if not title and text:
                    title = text
                    continue
                
                # 提取段落样式信息（标题级别）
                style_name = para.style.name if para.style else "Normal"
                is_heading = "Heading" in style_name
                heading_level = 0
                
                if is_heading:
                    # 提取标题级别 (Heading 1 -> level 1)
                    match = re.search(r'Heading\s+(\d+)', style_name)
                    if match:
                        heading_level = int(match.group(1))
                
                paragraphs.append({
                    "paragraph_id": paragraph_id,
                    "text": text,
                    "type": "heading" if is_heading else "paragraph",
                    "heading_level": heading_level,
                    "original_index": idx
                })
                
                paragraph_id += 1
            
            # 处理表格内容
            table_count = 0
            for table_idx, table in enumerate(doc.tables):
                table_count += 1
                for row in table.rows:
                    row_text = " | ".join([cell.text.strip() for cell in row.cells])
                    if row_text and not self.is_noise(row_text):
                        paragraphs.append({
                            "paragraph_id": paragraph_id,
                            "text": row_text,
                            "type": "table_row",
                            "heading_level": 0,
                            "original_index": f"table_{table_idx}"
                        })
                        paragraph_id += 1
            
            logger.info(f"✅ Parsed DOCX: {len(paragraphs)} paragraphs, {table_count} tables, {len(extracted_images)} images, title: {title[:50]}")
            
            # 详细记录图片信息
            if extracted_images:
                logger.info(f"📸 提取到 {len(extracted_images)} 张图片:")
                for idx, img in enumerate(extracted_images):
                    logger.info(f"   图片 {idx+1}: {img.get('filename')} - URL: {img.get('url')}")
            else:
                logger.warning("⚠️  未提取到任何图片")
            
            result = {
                "title": title,
                "total_paragraphs": len(paragraphs),
                "total_tables": table_count,  # 表格数量
                "paragraphs": paragraphs,
                "images": extracted_images,  # 添加提取的图片
                "format": "docx"
            }
            
            logger.info(f"📦 返回的 result 包含 images 字段: {'images' in result}, 值: {len(result.get('images', []))} 张图片")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse DOCX: {e}")
            raise Exception(f"DOCX解析失败: {str(e)}")
    
    def parse_pdf(self, file_content: bytes) -> Dict[str, Any]:
        """解析PDF文档"""
        try:
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            title = ""
            paragraphs = []
            paragraph_id = 0
            
            # 尝试从metadata获取标题
            if pdf_reader.metadata and pdf_reader.metadata.title:
                title = pdf_reader.metadata.title
            
            all_text = []
            
            # 逐页提取文本
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
                    continue
            
            # 合并所有页面文本
            full_text = "\n".join(all_text)
            
            # 按段落分割（以双换行或单换行+缩进为分隔）
            raw_paragraphs = re.split(r'\n\s*\n|\n(?=[A-Z])', full_text)
            
            for idx, para_text in enumerate(raw_paragraphs):
                text = para_text.strip()
                
                # 跳过噪音段落
                if self.is_noise(text):
                    continue
                
                # 如果还没有标题，第一个段落作为标题
                if not title and text:
                    title = text[:200]  # PDF标题可能较长，截取前200字符
                    continue
                
                # 判断是否为标题（全大写或较短且以数字/罗马数字开头）
                is_heading = False
                heading_level = 0
                
                if len(text) < 100 and (text.isupper() or re.match(r'^[\dIVXLCDM]+\.\s+', text)):
                    is_heading = True
                    heading_level = 1
                
                paragraphs.append({
                    "paragraph_id": paragraph_id,
                    "text": text,
                    "type": "heading" if is_heading else "paragraph",
                    "heading_level": heading_level,
                    "original_index": idx
                })
                
                paragraph_id += 1
            
            logger.info(f"Parsed PDF: {len(paragraphs)} paragraphs, title: {title[:50]}")
            
            return {
                "title": title,
                "total_paragraphs": len(paragraphs),
                "paragraphs": paragraphs,
                "images": [],  # PDF暂不支持图片提取，返回空数组
                "total_tables": 0,  # PDF表格数量
                "format": "pdf"
            }
            
        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            raise Exception(f"PDF解析失败: {str(e)}")
    
    def parse_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        根据文件类型解析文档
        
        Args:
            file_content: 文件二进制内容
            filename: 文件名
            
        Returns:
            结构化文档数据
        """
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext in ['docx', 'doc']:
            return self.parse_docx(file_content)
        elif file_ext == 'pdf':
            return self.parse_pdf(file_content)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}，目前仅支持 .docx, .doc, .pdf")


document_parser_service = DocumentParserService()

