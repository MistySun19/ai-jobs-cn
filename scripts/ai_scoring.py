#!/usr/bin/env python3
"""
AI Jobs CN — AI 暴露评分 Pipeline
对每个职业生成 AI 暴露评分 (0-10) 和中文理由
使用 Claude API 批量处理
"""

import json
import os
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("请先安装 anthropic SDK: pip install anthropic")
    raise

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data.json"

SCORING_PROMPT = """你是一位AI对就业影响的研究专家。请评估以下职业被AI影响/替代的程度。

职业: {name}
行业类别: {category}
就业人数: {employment}万人
年薪: {salary}万元
学历要求: {education}

请根据以下标准打分（0-10分）：
- 0-2分：几乎不受AI影响（纯体力劳动、需要物理在场、高度人际互动）
- 3-4分：轻度影响（部分辅助环节可AI化，但核心工作仍需人工）
- 5-6分：中度影响（AI可替代部分核心工作，但仍需人工监督和决策）
- 7-8分：高度影响（大部分工作可被AI自动化，人员需求将显著减少）
- 9-10分：极高影响（工作产出几乎完全可数字化，AI已能独立完成大部分任务）

核心评判依据：
1. 工作产出的数字化程度（文本/代码/数据 vs 物理产品/服务）
2. 任务的标准化/重复程度
3. 是否需要物理在场和手工操作
4. 是否需要复杂人际互动和情感判断
5. 当前AI技术的实际成熟度

请严格输出JSON格式（不要加```json标记）：
{{"ai_score": 整数0-10, "rationale": "100字以内的中文理由"}}"""


def score_batch(client, occupations, batch_size=10):
    """批量评分，每次处理 batch_size 个职业"""
    results = {}

    for i in range(0, len(occupations), batch_size):
        batch = occupations[i:i + batch_size]
        batch_names = [o["name"] for o in batch]
        print(f"评分中 [{i+1}-{i+len(batch)}/{len(occupations)}]: {', '.join(batch_names[:3])}...")

        # 构建批量 prompt
        prompts = []
        for occ in batch:
            prompts.append(f"职业{len(prompts)+1}: {occ['name']} | {occ['category']} | {occ['employment']}万人 | {occ['salary']}万元/年 | {occ['education']}")

        batch_prompt = f"""你是一位AI对就业影响的研究专家。请对以下{len(batch)}个职业逐一评估被AI影响/替代的程度。

{chr(10).join(prompts)}

评分标准（0-10分）：
- 0-2分：几乎不受AI影响（纯体力劳动、需要物理在场）
- 3-4分：轻度影响（辅助环节可AI化，核心工作仍需人工）
- 5-6分：中度影响（AI可替代部分核心工作，仍需人工监督）
- 7-8分：高度影响（大部分工作可被AI自动化）
- 9-10分：极高影响（工作产出几乎完全可数字化，AI已能独立完成）

核心依据：工作产出数字化程度、任务标准化程度、是否需物理在场、是否需复杂人际互动、当前AI技术成熟度。

请严格输出JSON数组格式（不要加```json标记），每个元素包含 name, ai_score(整数), rationale(80字内中文理由)：
[{{"name": "职业名", "ai_score": 5, "rationale": "理由"}}, ...]"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                messages=[{"role": "user", "content": batch_prompt}],
            )

            text = response.content[0].text.strip()
            # 尝试解析 JSON
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            batch_results = json.loads(text)
            for item in batch_results:
                results[item["name"]] = {
                    "ai_score": int(item["ai_score"]),
                    "rationale": item["rationale"],
                }
        except Exception as e:
            print(f"  批量评分失败，降级为逐个评分: {e}")
            for occ in batch:
                result = score_single(client, occ)
                if result:
                    results[occ["name"]] = result

        # 避免速率限制
        if i + batch_size < len(occupations):
            time.sleep(1)

    return results


def score_single(client, occ):
    """单个职业评分（降级方案）"""
    prompt = SCORING_PROMPT.format(**occ)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(text)
        return {
            "ai_score": int(result["ai_score"]),
            "rationale": result["rationale"],
        }
    except Exception as e:
        print(f"  评分失败 {occ['name']}: {e}")
        return None


def validate_scores(data):
    """一致性校验"""
    print("\n===== AI评分一致性校验 =====")

    # 体力劳动职业应该分数较低
    physical_jobs = ["建筑工人", "钢筋工", "水泥工/泥工", "焊工", "搬运工/搬家工",
                     "种植农民", "煤矿工人", "装修工", "水暖工"]
    # 纯数字化职业应该分数较高
    digital_jobs = ["数据分析师", "软件工程师", "会计师", "银行柜员", "翻译/口译员",
                    "行政助理/文员", "客户服务代表"]

    physical_scores = []
    digital_scores = []

    for item in data:
        if item["name"] in physical_jobs:
            physical_scores.append(item["ai_score"])
        if item["name"] in digital_jobs:
            digital_scores.append(item["ai_score"])

    if physical_scores and digital_scores:
        avg_physical = sum(physical_scores) / len(physical_scores)
        avg_digital = sum(digital_scores) / len(digital_scores)
        print(f"体力劳动平均分: {avg_physical:.1f}")
        print(f"数字化工作平均分: {avg_digital:.1f}")
        if avg_physical < avg_digital:
            print("✓ 通过: 体力劳动 < 数字化工作")
        else:
            print("✗ 警告: 体力劳动分数不应高于数字化工作")

    # 分数分布
    score_dist = {}
    for item in data:
        s = item["ai_score"]
        score_dist[s] = score_dist.get(s, 0) + 1
    print(f"分数分布: {dict(sorted(score_dist.items()))}")


def main():
    # 检查 API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        print("请运行: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # 加载数据
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"加载了 {len(data)} 个职业")

    client = anthropic.Anthropic(api_key=api_key)

    # 批量评分
    scores = score_batch(client, data, batch_size=15)

    print(f"\n成功评分: {len(scores)}/{len(data)}")

    # 合并评分到数据
    missing = []
    for item in data:
        name = item["name"]
        if name in scores:
            item["ai_score"] = scores[name]["ai_score"]
            item["rationale"] = scores[name]["rationale"]
        else:
            missing.append(name)
            # 保留默认值
            item["ai_score"] = 5
            item["rationale"] = "评分数据缺失，使用默认值"

    if missing:
        print(f"缺失评分: {missing}")

    # 写入更新后的数据
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已更新 {DATA_FILE}")

    # 验证
    validate_scores(data)


if __name__ == "__main__":
    main()
