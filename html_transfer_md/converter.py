#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML Table to Markdown Converter

功能:
    1. 将HTML表格转换为Markdown格式
    2. 支持处理带有rowspan和colspan的合并单元格
    3. 提供选项控制是否按行/列填充合并单元格
    4. 可自定义合并单元格的填充标记

作者: lrs33 
邮箱: aslongrushan@gmail.com
创建日期: 2025-04-24
最后修改日期: 2025-04-24
版本: 0.1.0
Python版本要求: >=3.7
依赖库:
    - beautifulsoup4>=4.9.0
    - html2text>=2020.1.16

使用示例:
    >>> from html_transfer_md import html_converter
    >>> html = "<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>"
    >>> markdown = html_converter(html)
    >>> print(markdown)
"""

import logging
from datetime import datetime
from bs4 import BeautifulSoup
from html2text import html2text

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

__author__ = "aslongrushan@gmail.com"
__version__ = "0.1.0"
__created_date__ = "2025-04-24"
__modified_date__ = "2025-04-24"


def html_converter(html_text: str, row_fill_merged: bool = True, col_fill_merged: bool = True, 
                     fill_mark: str = '无', verbose: bool = True) -> str:
    """
    将包含HTML表格的文本转换为Markdown格式，保留表格结构
    
    参数:
        html_text (str): 包含HTML表格的字符串
        row_fill_merged (bool): 是否自动按行填充合并的单元格 (默认: True)
        col_fill_merged (bool): 是否自动按列填充合并的单元格 (默认: True)
        fill_mark (str): 用于填充合并单元格的标记 (默认: '无')
        verbose (bool): 是否显示处理日志 (默认: True)
        
    返回:
        str: 转换后的Markdown格式文本
        
    示例:
        >>> html = "<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>"
        >>> markdown = html_converter(html)
    """
    start_time = datetime.now()
    if verbose:
        logger.info(f"开始处理HTML文本，长度: {len(html_text)} 字符")
    
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        tables = soup.find_all('table')
        
        if verbose:
            logger.info(f"找到 {len(tables)} 个表格")
        
        # 从最后一个表格开始处理，避免影响后续操作
        for i, table in enumerate(reversed(tables), 1):
            if verbose:
                logger.debug(f"正在处理表格 {i}/{len(tables)}")
                
            markdown_table = single_html_table_to_markdown(
                table, row_fill_merged, col_fill_merged, fill_mark, verbose
            )
            
            # 创建新的pre标签放置Markdown表格
            replacement = soup.new_tag("pre")
            replacement.string = markdown_table
            
            # 替换原始表格
            table.replace_with(replacement)
        
        reparse_html_str = str(soup.prettify())
        result = html2text(reparse_html_str)
        
        if verbose:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"处理完成，耗时: {elapsed:.2f}秒")
            
        return result
        
    except Exception as e:
        logger.error(f"处理HTML文本时出错: {str(e)}")
        raise


def single_html_table_to_markdown(table, row_fill_merged: bool, col_fill_merged: bool, 
                                fill_mark: str, verbose: bool = False) -> str:
    """
    将单个HTML表格转换为Markdown格式的表格
    
    参数:
        table (bs4.element.Tag): BeautifulSoup表格对象
        row_fill_merged (bool): 是否按行填充合并单元格
        col_fill_merged (bool): 是否按列填充合并单元格
        fill_mark (str): 合并单元格的填充标记
        verbose (bool): 是否显示详细日志
        
    返回:
        str: Markdown格式的表格字符串
    """
    if not table:
        if verbose:
            logger.warning("传入的表格对象为空")
        return ""

    start_time = datetime.now()
    if verbose:
        logger.debug("开始处理单个表格")
    
    try:
        # 提取所有行
        rows = []
        for tr in table.find_all('tr'):
            row = []
            exist_text = False
            for cell in tr.find_all(['th', 'td']):
                # 获取单元格文本并清理
                cell_text = ' '.join(cell.get_text(' ', strip=True).split())
                if cell_text.replace(" ", ""):
                    exist_text = True
                    
                # 处理rowspan和colspan属性
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                
                # 存储单元格信息
                row.append({
                    'text': cell_text,
                    'rowspan': rowspan,
                    'colspan': colspan,
                    'is_empty': not bool(cell_text) and not cell.find(True)
                })
            
            if exist_text:
                rows.append(row)

        if not rows:
            if verbose:
                logger.warning("表格中没有找到有效行")
            return ""
        
        # 计算最大列数
        max_cols = max(sum(cell['colspan'] for cell in row) for row in rows)
        
        if verbose:
            logger.debug(f"表格结构 - 行数: {len(rows)}, 最大列数: {max_cols}")
        
        # 创建填充网格
        grid = [[{'type': 'unfilled', 'value': ''} for _ in range(max_cols)] for _ in range(len(rows))]
        
        # 填充网格数据
        for i, row in enumerate(rows):
            col_pos = 0
            for cell in row:
                # 找到第一个未填充位置
                while col_pos < max_cols and grid[i][col_pos]['type'] != 'unfilled':
                    col_pos += 1
                if col_pos >= max_cols:
                    break
                   
                # 标记主单元格
                if cell['is_empty']:
                    grid[i][col_pos] = {'type': 'original_empty', 'value': fill_mark}
                else:
                    grid[i][col_pos] = {'type': 'original', 'value': cell['text']}
                
                # 标记合并的单元格位置
                for r in range(i, i + cell['rowspan']):
                    for c in range(col_pos, col_pos + cell['colspan']):
                        if r == i and c == col_pos:
                            continue
                        if r < len(grid) and c < max_cols:
                            should_fill = (
                                (r != i and c == col_pos and row_fill_merged) or  # 按行填充
                                (r == i and c != col_pos and col_fill_merged) or  # 按列填充
                                (r != i and c != col_pos and row_fill_merged and col_fill_merged)  # 同时填充
                            )
                            if should_fill:
                                grid[r][c] = {'type': 'filled', 'value': cell['text'] if cell['text'] else fill_mark}
                
                col_pos += cell['colspan']
        
        # 生成Markdown表格
        markdown_lines = []
        
        # 表头行
        if len(grid) > 0:
            headers = [cell['value'] for cell in grid[0]]
            markdown_lines.append("| " + " | ".join(headers) + " |")
            
            # 分隔线
            markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            
            # 数据行
            for row in grid[1:]:
                row_content = [cell['value'] if cell['value'] else fill_mark for cell in row]
                # 去除重复的行
                md_content = "| " + " | ".join(row_content) + " |"
                if md_content not in markdown_lines:
                    markdown_lines.append(md_content)
        
        if verbose:
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(f"表格处理完成，耗时: {elapsed:.4f}秒")
        
        return "\n".join(markdown_lines)
    
    except Exception as e:
        logger.error(f"处理表格时出错: {str(e)}")
        raise



