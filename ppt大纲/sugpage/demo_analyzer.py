#!/usr/bin/env python3
"""
Demo 专用简历分析器 —— 精简版 G5 pipeline
- 跳过面试题生成（省 10-20s）
- 降低 PDF 图片 DPI（省上传时间）
- 简化 prompt（不分岗位匹配，直接分析）
- 保留 scoring_engine 后处理 + JD 匹配
"""

import sys, os, re, json
from pathlib import Path

# 复用 G5 引擎
_G5_PROD = '/opt/scripts/G5/prod'
if _G5_PROD not in sys.path:
    sys.path.insert(0, _G5_PROD)

from engines.mimo_engine import _pdf_to_images, _call_mimo, extract_json_from_text
from scoring_engine import post_process, calc_experience_years
from schema import llm_output_to_result

__version__ = "v20260623-demo"


def demo_analyze(pdf_path: str, positions: list = None, jds: dict = None) -> dict:
    """精简分析：一次 MiMo 多模态调用 + scoring_engine 后处理，不生成面试题
    
    Args:
        pdf_path: PDF 简历文件路径
        positions: 在招岗位列表（必须传入真实岗位）
        jds: 岗位 JD 字典（必须传入真实 JD）
    
    Returns:
        result dict（标准 G5 输出格式，不含 interview_questions）
    """
    positions = positions or ["通用岗位"]
    jds = jds or {}
    
    # 1. 加载模板
    tmpl_text = _load_output_template()
    
    # 2. 构建 prompt（保留岗位匹配逻辑）
    position_details = "\n\n".join(
        f"===== 【{p}】岗位JD与评分标准 =====\n{jds.get(p, '（无JD）')}"
        for p in positions
    ) if jds else ""
    
    prompt = _build_demo_prompt(positions, jds, position_details, tmpl_text)
    
    # 2. MiMo 多模态调用（降低 DPI 加速）
    images = _pdf_to_images(pdf_path, dpi=100, max_pages=10)
    content = [{"type": "text", "text": prompt}]
    for b64 in images:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
    
    raw_text = _call_mimo([{"role": "user", "content": content}], model="mimo-v2.5")
    raw_json = extract_json_from_text(raw_text)
    
    # 3. 提取 position
    pos = raw_json.get("position", positions[0])
    
    # 4. schema 校验
    result = llm_output_to_result(raw_json, override_name="")
    
    # 5. scoring_engine 后处理（保留评分纠偏）
    bi = result.get("basic_info", {})
    jd = result.get("jd_check", {})
    
    work_periods = []
    for wea in result.get("work_experience_analysis", []):
        period = wea.get("period", "")
        company = wea.get("company", "")
        wea_pos = wea.get("position", "")
        title = f"{company}-{wea_pos}" if company else wea_pos
        start, end = _parse_period(period)
        if start and end:
            work_periods.append({"start": start, "end": end, "title": title})
    
    jd_required_years = None
    exp_req = jd.get("experience_requirement", "")
    if exp_req:
        nums = re.findall(r"(\d+)\s*年", exp_req)
        if nums:
            jd_required_years = int(nums[0])
    
    position_rules_text = jds.get(pos, "")
    result = post_process(
        result,
        position_rules=position_rules_text,
        work_periods=work_periods if work_periods else None,
        graduation_year=None,
        jd_required_years=jd_required_years,
    )
    
    # 不生成面试题
    result["preliminary_questions"] = []
    result["interview_questions"] = []
    
    # 数据成果检查：工作经历中是否有量化数据
    _check_data_evidence(result)
    # 岗位合理性检查：刚毕业做运营、跳槽频繁
    _check_career_validity(result)
    
    return pos, result


def _check_career_validity(result: dict):
    """校验候选人岗位描述合理性"""
    bi = result.get("basic_info", {})
    wea = result.get("work_experience_analysis", [])
    all_text = json.dumps(wea, ensure_ascii=False)
    warnings = result.setdefault("warnings", [])
    sc = result.get("scores", {})
    
    # 1. 刚毕业就做运营/总监/经理：需警示
    education = bi.get("education", "")
    is_junior = any(kw in education for kw in ["应届", "实习", "刚毕业"])
    has_ops_title = any(kw in all_text for kw in ["运营总监", "运营经理", "运营主管", "运营负责人"])
    if has_ops_title and (is_junior or bi.get("relevant_experience_years", 0) < 1):
        warnings.append("刚毕业即担任运营管理岗，岗位描述合理性存疑，建议核实实际职责范围")
        sc["core_competence"] = max(0, sc.get("core_competence", 0) - 3)
        sc["total"] = max(0, sc.get("total", 0) - 3)
    
    # 2. 跳槽频繁：工作经历≥3段，平均每段<18个月
    periods = []
    for w in wea:
        period_str = w.get("period", "")
        m = re.match(r"(\d{4})[-/.](\d{1,2})", period_str)
        if m:
            periods.append((int(m.group(1)), int(m.group(2))))
    if len(periods) >= 3:
        # 计算相邻工作的间隔
        short_jobs = 0
        for i in range(1, len(periods)):
            months = (periods[i][0] - periods[i-1][0]) * 12 + (periods[i][1] - periods[i-1][1])
            if months < 18:
                short_jobs += 1
        if short_jobs >= 2:
            sc["detail_check"] = max(0, sc.get("detail_check", 0) - 5)
            sc["total"] = max(0, sc.get("total", 0) - 5)
            warnings.append(f"跳槽频繁（{len(periods)}份工作，多段<18个月）：稳定性存疑（-5分）")


def _check_data_evidence(result: dict):
    """检查工作经历中是否有量化数据，无则扣分"""
    wea = result.get("work_experience_analysis", [])
    has_data = False
    data_patterns = [r'\d+%', r'\d+万', r'\d+亿', r'\d+倍', r'增长\d+', r'提升\d+', r'降低\d+',
                     r'营收\d+', r'GMV\d+', r'DAU\d+', r'MAU\d+', r'转化率\d+',
                     r'\d+[个只台套件]', r'\d+[元块]', r'\d+[年月日天周].*?完成']
    
    all_text = json.dumps(wea, ensure_ascii=False)
    for pat in data_patterns:
        if re.search(pat, all_text):
            has_data = True
            break
    
    sc = result.get("scores", {})
    if not has_data:
        # 仅简单描述工作内容，无量化成果 → 核心能力/细节审查/表达沟通各扣5分
        deduct = 5
        for key in ["core_competence", "detail_check", "expression"]:
            sc[key] = max(0, sc.get(key, 0) - deduct)
        sc["total"] = max(0, sc.get("total", 0) - deduct * 3)
        result.setdefault("warnings", []).append(
            "工作经历仅描述职责未体现量化成果（-15分）：候选人对自己工作成果重视度不足，对岗位核心价值认知欠缺"
        )
    else:
        # 有数据：检查是否可信（简单规则）
        suspicious = False
        for pat in [r'(\d+)亿', r'(\d+)千万', r'(\d+)万']:
            m = re.search(pat, all_text)
            if m and int(m.group(1)) > 1000:
                suspicious = True
                break
        if suspicious:
            result.setdefault("warnings", []).append("工作成果数据量级较大，建议面试时核实真实性")


def _build_demo_prompt(positions: list, jds: dict, position_details: str, tmpl: str) -> str:
    """构建 prompt：保留岗位匹配逻辑，简化评分标准"""
    from datetime import datetime

    prompt = f"""你是资深HR招聘专家。**当前日期：{datetime.now().strftime("%Y年%m月%d日")}**

任务：分析候选人简历，完成以下两步：

**第一步：从岗位列表中选出最匹配的岗位**
- 提取候选人核心工作职能
- 逐个岗位对标，判断核心职能与JD的重叠度
- 重叠度≥50%才算匹配，否则选最接近的

**第二步：按选中的岗位进行完整简历分析，输出JSON**

**数据成果评估（必须检查）：**
- 工作经历中是否有量化数据（如"销售额提升30%"、"月活用户从1万增长到5万"）？
- 无数据展现 → 表达能力和营销思维各扣5分，在 warnings 中注明"工作成果缺少数据支撑"
- 有数据展现 → 判断数据是否合理可信（如"应届生一年创收1000万"明显夸大），不可信则在 warnings 中标注"数据疑似夸大"

=== 候选人简历（PDF图片已附在消息后） ===

{position_details}

===== 分析模板（严格按此JSON格式输出，不要加```标记） =====
{tmpl}

===== 输出要求 =====
1. position 字段填选中的岗位名称
2. position_reason 说明为什么选这个岗位（一句话）
3. 评分按该岗位的 JD 标准打分
4. 简历乱码忽略，不要放到预警中
"""
    return prompt


def _load_output_template() -> str:
    """加载简化版输出模板"""
    return """{
  "position": "岗位名",
  "position_reason": "一句话原因",
  "basic_info": {
    "name": "", "gender": "", "age": 0, "education": "",
    "is_full_time": "", "school": "", "major": "",
    "relevant_experience_years": 0, "contact": ""
  },
  "jd_check": {
    "education_requirement": "", "education_actual": "", "education_pass": false,
    "experience_requirement": "", "experience_actual": "", "experience_pass": false,
    "skills_details": [{"item": "", "requirement": "", "actual": "", "pass": false}],
    "bonus_details": [{"item": "", "requirement": "", "actual": "", "pass": false}]
  },
  "scores": {
    "education": 0, "experience": 0, "core_competence": 0,
    "detail_check": 0, "expression": 0, "bonus": 0, "total": 0
  },
  "work_experience_analysis": [
    {
      "period": "", "company": "", "position": "",
      "summary": "",
      "interpretations": [{"quote": "", "interpretation": ""}]
    }
  ],
  "highlights": [""],
  "warnings": [""],
  "recommendation": ""
}"""


def _parse_period(period_str: str) -> tuple:
    """解析时间段 2022-06 至 2024-12 → (start, end)"""
    if not period_str:
        return None, None
    m = re.match(r"(\d{4}[-/]\d{1,2}).*?(\d{4}[-/]\d{1,2}|至今|现在)", period_str)
    if m:
        return m.group(1), m.group(2)
    return None, None
