#!/usr/bin/env python3
"""
AI Jobs CN — 数据构建脚本
从采集的行业宏观数据 + 职业级参考数据，合并生成最终 data.json
"""

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ============================================================
# 职业完整定义：147 个职业
# 每个职业包含：行业映射、默认学历、行业内占比系数、增长率调整
# ============================================================

OCCUPATION_DEFS = [
    # ---- 信息技术 (15) ----
    {"name": "软件工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.08, "education": "本科", "growth_adj": 0},
    {"name": "数据分析师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.025, "education": "本科", "growth_adj": 0.05},
    {"name": "数据库管理员", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.015, "education": "本科", "growth_adj": -0.02},
    {"name": "网络工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.03, "education": "本科", "growth_adj": -0.01},
    {"name": "系统运维工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.035, "education": "大专", "growth_adj": -0.03},
    {"name": "UI/UX设计师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.02, "education": "本科", "growth_adj": 0},
    {"name": "产品经理", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.025, "education": "本科", "growth_adj": 0.02},
    {"name": "测试工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.04, "education": "本科", "growth_adj": -0.02},
    {"name": "算法工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.015, "education": "硕士", "growth_adj": 0.08},
    {"name": "前端开发工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.04, "education": "本科", "growth_adj": 0},
    {"name": "信息安全工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.015, "education": "本科", "growth_adj": 0.03},
    {"name": "游戏开发工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.012, "education": "本科", "growth_adj": 0},
    {"name": "技术支持专员", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.03, "education": "大专", "growth_adj": -0.03},
    {"name": "IT项目经理", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.015, "education": "本科", "growth_adj": 0},
    {"name": "嵌入式开发工程师", "category": "信息技术", "industry": "信息传输软件和信息技术服务业", "share": 0.02, "education": "本科", "growth_adj": 0.02},

    # ---- 金融 (13) ----
    {"name": "银行柜员", "category": "金融", "industry": "金融业", "share": 0.10, "education": "本科", "growth_adj": -0.08},
    {"name": "会计师", "category": "金融", "industry": "金融业", "share": 0.08, "education": "本科", "growth_adj": -0.02},
    {"name": "审计师", "category": "金融", "industry": "金融业", "share": 0.03, "education": "本科", "growth_adj": 0},
    {"name": "金融分析师", "category": "金融", "industry": "金融业", "share": 0.02, "education": "硕士", "growth_adj": 0.02},
    {"name": "证券经纪人", "category": "金融", "industry": "金融业", "share": 0.025, "education": "本科", "growth_adj": -0.05},
    {"name": "保险代理人", "category": "金融", "industry": "金融业", "share": 0.12, "education": "高中中专", "growth_adj": -0.06},
    {"name": "基金经理", "category": "金融", "industry": "金融业", "share": 0.005, "education": "硕士", "growth_adj": 0.02},
    {"name": "风控专员", "category": "金融", "industry": "金融业", "share": 0.015, "education": "本科", "growth_adj": 0.03},
    {"name": "税务师", "category": "金融", "industry": "金融业", "share": 0.01, "education": "本科", "growth_adj": 0},
    {"name": "精算师", "category": "金融", "industry": "金融业", "share": 0.003, "education": "硕士", "growth_adj": 0.02},
    {"name": "信贷审批员", "category": "金融", "industry": "金融业", "share": 0.03, "education": "本科", "growth_adj": -0.06},
    {"name": "投资顾问", "category": "金融", "industry": "金融业", "share": 0.015, "education": "本科", "growth_adj": 0},
    {"name": "出纳员", "category": "金融", "industry": "金融业", "share": 0.04, "education": "大专", "growth_adj": -0.05},

    # ---- 教育 (11) ----
    {"name": "小学教师", "category": "教育", "industry": "教育", "share": 0.0, "education": "本科", "growth_adj": 0},
    {"name": "中学教师", "category": "教育", "industry": "教育", "share": 0.0, "education": "本科", "growth_adj": 0},
    {"name": "大学教授", "category": "教育", "industry": "教育", "share": 0.0, "education": "博士", "growth_adj": 0.02},
    {"name": "幼儿教师", "category": "教育", "industry": "教育", "share": 0.0, "education": "大专", "growth_adj": -0.03},
    {"name": "特殊教育教师", "category": "教育", "industry": "教育", "share": 0.0, "education": "本科", "growth_adj": 0.02},
    {"name": "职业培训讲师", "category": "教育", "industry": "教育", "share": 0.04, "education": "本科", "growth_adj": 0},
    {"name": "教育咨询师", "category": "教育", "industry": "教育", "share": 0.02, "education": "本科", "growth_adj": -0.02},
    {"name": "在线教育讲师", "category": "教育", "industry": "教育", "share": 0.015, "education": "本科", "growth_adj": 0.03},
    {"name": "高校辅导员", "category": "教育", "industry": "教育", "share": 0.01, "education": "硕士", "growth_adj": 0},
    {"name": "驾校教练", "category": "教育", "industry": "教育", "share": 0.02, "education": "高中中专", "growth_adj": -0.02},
    {"name": "体育教师/教练", "category": "教育", "industry": "教育", "share": 0.02, "education": "本科", "growth_adj": 0.01},

    # ---- 医疗健康 (13) ----
    {"name": "临床医生", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.0, "education": "本科", "growth_adj": 0.02},
    {"name": "护士", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.0, "education": "大专", "growth_adj": 0.03},
    {"name": "药剂师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.03, "education": "本科", "growth_adj": 0.01},
    {"name": "中医师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.02, "education": "本科", "growth_adj": 0.02},
    {"name": "牙科医生", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.015, "education": "本科", "growth_adj": 0.03},
    {"name": "医学检验师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.02, "education": "本科", "growth_adj": 0.01},
    {"name": "康复治疗师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.01, "education": "本科", "growth_adj": 0.05},
    {"name": "心理咨询师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.005, "education": "硕士", "growth_adj": 0.05},
    {"name": "医学影像技师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.015, "education": "本科", "growth_adj": 0.02},
    {"name": "公共卫生医师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.01, "education": "本科", "growth_adj": 0.03},
    {"name": "护工/护理员", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.05, "education": "初中及以下", "growth_adj": 0.05},
    {"name": "营养师", "category": "医疗健康", "industry": "卫生和社会工作", "share": 0.005, "education": "本科", "growth_adj": 0.03},
    {"name": "兽医", "category": "医疗健康", "industry": "农林牧渔业", "share": 0.002, "education": "本科", "growth_adj": 0.02},

    # ---- 制造业 (13) ----
    {"name": "机械工程师", "category": "制造业", "industry": "制造业", "share": 0.02, "education": "本科", "growth_adj": 0.01},
    {"name": "电气工程师", "category": "制造业", "industry": "制造业", "share": 0.015, "education": "本科", "growth_adj": 0.02},
    {"name": "质量检验员", "category": "制造业", "industry": "制造业", "share": 0.03, "education": "大专", "growth_adj": -0.02},
    {"name": "焊工", "category": "制造业", "industry": "制造业", "share": 0.025, "education": "高中中专", "growth_adj": -0.03},
    {"name": "数控机床操作工", "category": "制造业", "industry": "制造业", "share": 0.03, "education": "高中中专", "growth_adj": -0.02},
    {"name": "装配工", "category": "制造业", "industry": "制造业", "share": 0.06, "education": "初中及以下", "growth_adj": -0.04},
    {"name": "工业设计师", "category": "制造业", "industry": "制造业", "share": 0.005, "education": "本科", "growth_adj": 0.02},
    {"name": "化工技术员", "category": "制造业", "industry": "制造业", "share": 0.015, "education": "大专", "growth_adj": 0},
    {"name": "纺织工", "category": "制造业", "industry": "制造业", "share": 0.03, "education": "初中及以下", "growth_adj": -0.05},
    {"name": "食品加工工", "category": "制造业", "industry": "制造业", "share": 0.025, "education": "初中及以下", "growth_adj": -0.02},
    {"name": "电子装配工", "category": "制造业", "industry": "制造业", "share": 0.04, "education": "高中中专", "growth_adj": -0.03},
    {"name": "生产主管", "category": "制造业", "industry": "制造业", "share": 0.01, "education": "大专", "growth_adj": 0},
    {"name": "模具工", "category": "制造业", "industry": "制造业", "share": 0.015, "education": "高中中专", "growth_adj": -0.03},

    # ---- 建筑工程 (11) ----
    {"name": "建筑工人", "category": "建筑工程", "industry": "建筑业", "share": 0.25, "education": "初中及以下", "growth_adj": -0.04},
    {"name": "钢筋工", "category": "建筑工程", "industry": "建筑业", "share": 0.08, "education": "初中及以下", "growth_adj": -0.04},
    {"name": "水泥工/泥工", "category": "建筑工程", "industry": "建筑业", "share": 0.08, "education": "初中及以下", "growth_adj": -0.04},
    {"name": "建筑设计师", "category": "建筑工程", "industry": "建筑业", "share": 0.01, "education": "本科", "growth_adj": -0.02},
    {"name": "土木工程师", "category": "建筑工程", "industry": "建筑业", "share": 0.015, "education": "本科", "growth_adj": -0.01},
    {"name": "装修工", "category": "建筑工程", "industry": "建筑业", "share": 0.10, "education": "初中及以下", "growth_adj": -0.02},
    {"name": "测量员", "category": "建筑工程", "industry": "建筑业", "share": 0.01, "education": "大专", "growth_adj": -0.01},
    {"name": "起重机操作员", "category": "建筑工程", "industry": "建筑业", "share": 0.015, "education": "高中中专", "growth_adj": -0.03},
    {"name": "电梯安装维修工", "category": "建筑工程", "industry": "建筑业", "share": 0.01, "education": "高中中专", "growth_adj": 0.01},
    {"name": "水暖工", "category": "建筑工程", "industry": "建筑业", "share": 0.03, "education": "初中及以下", "growth_adj": -0.02},
    {"name": "室内设计师", "category": "建筑工程", "industry": "建筑业", "share": 0.008, "education": "本科", "growth_adj": -0.01},

    # ---- 农林牧渔 (7) ----
    {"name": "种植农民", "category": "农林牧渔", "industry": "农林牧渔业", "share": 0.70, "education": "初中及以下", "growth_adj": -0.03},
    {"name": "畜牧养殖户", "category": "农林牧渔", "industry": "农林牧渔业", "share": 0.12, "education": "初中及以下", "growth_adj": -0.02},
    {"name": "渔民", "category": "农林牧渔", "industry": "农林牧渔业", "share": 0.03, "education": "初中及以下", "growth_adj": -0.04},
    {"name": "林业工人", "category": "农林牧渔", "industry": "农林牧渔业", "share": 0.02, "education": "初中及以下", "growth_adj": -0.02},
    {"name": "农业技术员", "category": "农林牧渔", "industry": "农林牧渔业", "share": 0.008, "education": "大专", "growth_adj": 0.02},
    {"name": "园艺师", "category": "农林牧渔", "industry": "农林牧渔业", "share": 0.01, "education": "大专", "growth_adj": 0.01},
    {"name": "农机操作员", "category": "农林牧渔", "industry": "农林牧渔业", "share": 0.03, "education": "初中及以下", "growth_adj": 0.02},

    # ---- 商业服务 (12) ----
    {"name": "人力资源专员", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.06, "education": "本科", "growth_adj": 0},
    {"name": "市场营销专员", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.05, "education": "本科", "growth_adj": 0},
    {"name": "管理咨询师", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.02, "education": "硕士", "growth_adj": 0.02},
    {"name": "行政助理/文员", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.08, "education": "大专", "growth_adj": -0.03},
    {"name": "客户服务代表", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.07, "education": "大专", "growth_adj": -0.04},
    {"name": "翻译/口译员", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.01, "education": "本科", "growth_adj": -0.05},
    {"name": "公关专员", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.015, "education": "本科", "growth_adj": 0},
    {"name": "广告策划", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.02, "education": "本科", "growth_adj": -0.01},
    {"name": "商务代表/销售", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.10, "education": "大专", "growth_adj": -0.02},
    {"name": "采购专员", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.03, "education": "大专", "growth_adj": -0.01},
    {"name": "法务专员", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.01, "education": "本科", "growth_adj": 0.01},
    {"name": "企业培训师", "category": "商业服务", "industry": "租赁和商务服务业", "share": 0.015, "education": "本科", "growth_adj": 0},

    # ---- 公共管理与法律 (8) ----
    {"name": "公务员", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.0, "education": "本科", "growth_adj": 0},
    {"name": "社区工作者", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.04, "education": "大专", "growth_adj": 0.03},
    {"name": "消防员", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.0, "education": "高中中专", "growth_adj": 0.01},
    {"name": "警察", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.0, "education": "本科", "growth_adj": 0},
    {"name": "律师", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.0, "education": "本科", "growth_adj": 0.03},
    {"name": "法官", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.0, "education": "本科", "growth_adj": 0},
    {"name": "公证员", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.0, "education": "本科", "growth_adj": 0},
    {"name": "城管执法人员", "category": "公共管理与法律", "industry": "公共管理社会保障和社会组织", "share": 0.01, "education": "大专", "growth_adj": 0},

    # ---- 交通运输与物流 (9) ----
    {"name": "网约车/出租车司机", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.0, "education": "高中中专", "growth_adj": 0.02},
    {"name": "货车司机", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.15, "education": "初中及以下", "growth_adj": -0.02},
    {"name": "公交车司机", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.03, "education": "高中中专", "growth_adj": -0.03},
    {"name": "快递员", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.0, "education": "初中及以下", "growth_adj": 0.02},
    {"name": "外卖骑手", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.0, "education": "初中及以下", "growth_adj": 0.03},
    {"name": "飞行员", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.0, "education": "本科", "growth_adj": 0.02},
    {"name": "船员", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.02, "education": "高中中专", "growth_adj": -0.02},
    {"name": "仓储物流员", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.06, "education": "初中及以下", "growth_adj": 0},
    {"name": "调度员", "category": "交通运输与物流", "industry": "交通运输仓储和邮政业", "share": 0.015, "education": "大专", "growth_adj": -0.01},

    # ---- 文化传媒 (10) ----
    {"name": "记者/新闻编辑", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.04, "education": "本科", "growth_adj": -0.03},
    {"name": "摄影师/摄像师", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.03, "education": "大专", "growth_adj": -0.01},
    {"name": "平面设计师", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.04, "education": "大专", "growth_adj": -0.02},
    {"name": "视频剪辑师", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.03, "education": "大专", "growth_adj": 0.03},
    {"name": "播音主持人", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.008, "education": "本科", "growth_adj": -0.02},
    {"name": "作家/编剧", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.01, "education": "本科", "growth_adj": -0.02},
    {"name": "图书馆员", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.015, "education": "本科", "growth_adj": -0.02},
    {"name": "档案管理员", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.015, "education": "大专", "growth_adj": -0.03},
    {"name": "网络主播/自媒体", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.05, "education": "高中中专", "growth_adj": 0.08},
    {"name": "动画设计师", "category": "文化传媒", "industry": "文化体育和娱乐业", "share": 0.015, "education": "本科", "growth_adj": 0.02},

    # ---- 零售餐饮住宿 (9) ----
    {"name": "零售店员", "category": "零售餐饮住宿", "industry": "批发和零售业", "share": 0.15, "education": "高中中专", "growth_adj": -0.03},
    {"name": "收银员", "category": "零售餐饮住宿", "industry": "批发和零售业", "share": 0.05, "education": "初中及以下", "growth_adj": -0.06},
    {"name": "厨师", "category": "零售餐饮住宿", "industry": "住宿和餐饮业", "share": 0.15, "education": "初中及以下", "growth_adj": 0},
    {"name": "餐厅服务员", "category": "零售餐饮住宿", "industry": "住宿和餐饮业", "share": 0.25, "education": "初中及以下", "growth_adj": -0.01},
    {"name": "电商运营", "category": "零售餐饮住宿", "industry": "批发和零售业", "share": 0.03, "education": "大专", "growth_adj": 0.05},
    {"name": "直播带货主播", "category": "零售餐饮住宿", "industry": "批发和零售业", "share": 0.01, "education": "高中中专", "growth_adj": 0.10},
    {"name": "超市理货员", "category": "零售餐饮住宿", "industry": "批发和零售业", "share": 0.06, "education": "初中及以下", "growth_adj": -0.03},
    {"name": "酒店前台", "category": "零售餐饮住宿", "industry": "住宿和餐饮业", "share": 0.05, "education": "大专", "growth_adj": -0.02},
    {"name": "酒店管理人员", "category": "零售餐饮住宿", "industry": "住宿和餐饮业", "share": 0.02, "education": "本科", "growth_adj": 0},

    # ---- 生活服务 (10) ----
    {"name": "美容师", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.08, "education": "高中中专", "growth_adj": 0.01},
    {"name": "美发师", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.06, "education": "初中及以下", "growth_adj": 0},
    {"name": "家政服务员", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.15, "education": "初中及以下", "growth_adj": 0.03},
    {"name": "月嫂/育儿嫂", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.05, "education": "初中及以下", "growth_adj": 0.05},
    {"name": "健身教练", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.03, "education": "高中中专", "growth_adj": 0.03},
    {"name": "房产经纪人", "category": "生活服务", "industry": "房地产业", "share": 0.10, "education": "大专", "growth_adj": -0.05},
    {"name": "搬运工/搬家工", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.04, "education": "初中及以下", "growth_adj": -0.02},
    {"name": "保安", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.12, "education": "初中及以下", "growth_adj": -0.01},
    {"name": "物业管理员", "category": "生活服务", "industry": "房地产业", "share": 0.08, "education": "高中中专", "growth_adj": 0.01},
    {"name": "婚庆策划师", "category": "生活服务", "industry": "居民服务修理和其他服务业", "share": 0.01, "education": "大专", "growth_adj": 0},

    # ---- 能源矿产 (6) ----
    {"name": "煤矿工人", "category": "能源矿产", "industry": "采矿业", "share": 0.30, "education": "初中及以下", "growth_adj": -0.05},
    {"name": "石油钻井工", "category": "能源矿产", "industry": "采矿业", "share": 0.10, "education": "高中中专", "growth_adj": -0.03},
    {"name": "电力工程师", "category": "能源矿产", "industry": "电力热力燃气及水生产和供应业", "share": 0.05, "education": "本科", "growth_adj": 0.02},
    {"name": "电网维护电工", "category": "能源矿产", "industry": "电力热力燃气及水生产和供应业", "share": 0.08, "education": "大专", "growth_adj": 0},
    {"name": "新能源技术员", "category": "能源矿产", "industry": "电力热力燃气及水生产和供应业", "share": 0.03, "education": "大专", "growth_adj": 0.08},
    {"name": "环保工程师", "category": "能源矿产", "industry": "水利环境和公共设施管理业", "share": 0.02, "education": "本科", "growth_adj": 0.03},
]

# ============================================================
# 薪酬调整系数：基于职业相对行业平均的薪酬倍率
# ============================================================

SALARY_MULTIPLIERS = {
    # 信息技术 - 基准为行业平均
    "软件工程师": 1.25, "数据分析师": 1.10, "数据库管理员": 1.05,
    "网络工程师": 0.95, "系统运维工程师": 0.85, "UI/UX设计师": 1.05,
    "产品经理": 1.30, "测试工程师": 0.90, "算法工程师": 1.60,
    "前端开发工程师": 1.15, "信息安全工程师": 1.15, "游戏开发工程师": 1.20,
    "技术支持专员": 0.65, "IT项目经理": 1.35, "嵌入式开发工程师": 1.10,

    # 金融
    "银行柜员": 0.75, "会计师": 0.85, "审计师": 1.00,
    "金融分析师": 1.40, "证券经纪人": 1.10, "保险代理人": 0.55,
    "基金经理": 2.50, "风控专员": 1.10, "税务师": 0.95,
    "精算师": 2.00, "信贷审批员": 0.80, "投资顾问": 1.20, "出纳员": 0.60,

    # 教育
    "小学教师": 0.85, "中学教师": 0.90, "大学教授": 1.40,
    "幼儿教师": 0.60, "特殊教育教师": 0.80, "职业培训讲师": 1.00,
    "教育咨询师": 0.90, "在线教育讲师": 1.05, "高校辅导员": 0.85,
    "驾校教练": 0.75, "体育教师/教练": 0.80,

    # 医疗
    "临床医生": 1.30, "护士": 0.80, "药剂师": 0.95,
    "中医师": 1.10, "牙科医生": 1.50, "医学检验师": 0.85,
    "康复治疗师": 0.80, "心理咨询师": 1.10, "医学影像技师": 0.85,
    "公共卫生医师": 0.90, "护工/护理员": 0.45, "营养师": 0.85, "兽医": 0.90,

    # 制造
    "机械工程师": 1.20, "电气工程师": 1.25, "质量检验员": 0.80,
    "焊工": 0.90, "数控机床操作工": 0.85, "装配工": 0.65,
    "工业设计师": 1.30, "化工技术员": 0.85, "纺织工": 0.60,
    "食品加工工": 0.60, "电子装配工": 0.65, "生产主管": 1.15, "模具工": 0.85,

    # 建筑
    "建筑工人": 0.80, "钢筋工": 0.85, "水泥工/泥工": 0.75,
    "建筑设计师": 1.50, "土木工程师": 1.30, "装修工": 0.90,
    "测量员": 1.00, "起重机操作员": 0.95, "电梯安装维修工": 1.05,
    "水暖工": 0.85, "室内设计师": 1.20,

    # 农林牧渔
    "种植农民": 0.50, "畜牧养殖户": 0.60, "渔民": 0.70,
    "林业工人": 0.55, "农业技术员": 1.20, "园艺师": 1.00, "农机操作员": 0.75,

    # 商业服务
    "人力资源专员": 0.90, "市场营销专员": 0.95, "管理咨询师": 1.80,
    "行政助理/文员": 0.65, "客户服务代表": 0.60, "翻译/口译员": 1.10,
    "公关专员": 1.00, "广告策划": 1.05, "商务代表/销售": 0.85,
    "采购专员": 0.80, "法务专员": 1.10, "企业培训师": 1.15,

    # 公共管理
    "公务员": 1.00, "社区工作者": 0.65, "消防员": 0.85,
    "警察": 0.95, "律师": 1.80, "法官": 1.30, "公证员": 1.20, "城管执法人员": 0.75,

    # 交通物流
    "网约车/出租车司机": 0.80, "货车司机": 0.90, "公交车司机": 0.85,
    "快递员": 0.75, "外卖骑手": 0.70, "飞行员": 3.50,
    "船员": 1.00, "仓储物流员": 0.65, "调度员": 0.80,

    # 文化传媒
    "记者/新闻编辑": 1.00, "摄影师/摄像师": 0.80, "平面设计师": 0.85,
    "视频剪辑师": 0.80, "播音主持人": 1.30, "作家/编剧": 1.10,
    "图书馆员": 0.70, "档案管理员": 0.65, "网络主播/自媒体": 1.50, "动画设计师": 0.90,

    # 零售餐饮住宿
    "零售店员": 0.70, "收银员": 0.60, "厨师": 0.85,
    "餐厅服务员": 0.60, "电商运营": 1.20, "直播带货主播": 1.50,
    "超市理货员": 0.60, "酒店前台": 0.70, "酒店管理人员": 1.30,

    # 生活服务
    "美容师": 0.90, "美发师": 0.80, "家政服务员": 0.70,
    "月嫂/育儿嫂": 1.00, "健身教练": 1.10, "房产经纪人": 0.90,
    "搬运工/搬家工": 0.65, "保安": 0.55, "物业管理员": 0.70, "婚庆策划师": 1.00,

    # 能源矿产
    "煤矿工人": 0.85, "石油钻井工": 1.10, "电力工程师": 1.30,
    "电网维护电工": 0.95, "新能源技术员": 1.10, "环保工程师": 1.05,
}


def load_json(filename):
    path = DATA_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def build_industry_lookup(industry_data):
    """构建行业名 → {employment_wan, avg_salary} 的查找表"""
    lookup = {}
    if not industry_data:
        return lookup
    for ind in industry_data.get("industries", []):
        name = ind["name"]
        emp = ind.get("employment_wan", 0)
        # 加权平均工资：非私营 60% + 私营 40%（私营单位占比更大但工资更低）
        sal_np = ind.get("avg_salary_non_private", 0)
        sal_p = ind.get("avg_salary_private", 0)
        if sal_np and sal_p:
            avg_sal = sal_np * 0.55 + sal_p * 0.45
        elif sal_np:
            avg_sal = sal_np
        elif sal_p:
            avg_sal = sal_p
        else:
            avg_sal = 0
        lookup[name] = {"employment_wan": emp, "avg_salary_yuan": avg_sal}
    return lookup


def build_authoritative_lookup(auth_data):
    """构建职业名 → employment_wan 的查找表（含名称映射）"""
    # 权威数据中的名称 → OCCUPATION_DEFS 中的名称
    NAME_MAP = {
        "幼儿教师": "幼儿教师",
        "小学教师": "小学教师",
        "特殊教育教师": "特殊教育教师",
        "高校教师": "大学教授",
        "临床医生（执业医师+执业助理医师）": "临床医生",
        "注册护士": "护士",
        "律师": "律师",
        "公证员": "公证员",
        "法官（员额法官）": "法官",
        "注册会计师（执业）": None,  # 跳过，用含非执业的数据
        "注册会计师（含非执业）": None,  # 会计师范围不同，不直接映射
        "税务师": "税务师",
        "公务员": "公务员",
        "公安民警": "警察",
        "消防员（国家综合性消防救援队伍）": "消防员",
        "快递从业人员": "快递员",
        "网约车驾驶员": "网约车/出租车司机",
        "外卖骑手": "外卖骑手",
        "民航飞行员（运输航空）": "飞行员",
        "一级注册建筑师": None,  # 不直接对应
        "仲裁员": None,
        "司法鉴定人": None,
    }

    lookup = {}
    if not auth_data:
        return lookup

    for item in auth_data.get("data", []):
        raw_name = item["occupation"]
        mapped_name = NAME_MAP.get(raw_name, raw_name)
        if mapped_name is not None:
            lookup[mapped_name] = item["employment_wan"]

    # 合并初中+高中教师 → 中学教师
    chu_zhong = 0
    gao_zhong = 0
    for item in auth_data.get("data", []):
        if item["occupation"] == "初中教师":
            chu_zhong = item["employment_wan"]
        elif item["occupation"] == "高中教师":
            gao_zhong = item["employment_wan"]
    if chu_zhong or gao_zhong:
        lookup["中学教师"] = round(chu_zhong + gao_zhong, 2)

    return lookup


def build_salary_ref_lookup(salary_data):
    """构建职业名 → salary_wan 的查找表（含名称映射）"""
    # 直接匹配的职业
    DIRECT_MAP = {
        "算法工程师": "算法工程师",
        "律师": "律师",
        "外卖骑手": "外卖骑手",
        "网约车司机": "网约车/出租车司机",
        "快递员": "快递员",
        "护士": "护士",
        "临床医生": "临床医生",
        "公务员（科员）": "公务员",
    }

    lookup = {}
    if not salary_data:
        return lookup

    for item in salary_data.get("data", []):
        raw_name = item["occupation"]
        # 直接映射
        if raw_name in DIRECT_MAP:
            lookup[DIRECT_MAP[raw_name]] = item["salary_ref_wan"]
        # 精确匹配
        elif raw_name in SALARY_MULTIPLIERS:
            lookup[raw_name] = item["salary_ref_wan"]

    return lookup


def compute_employment(occ, industry_lookup, auth_lookup):
    """计算职业就业人数（万人）"""
    name = occ["name"]

    # 优先使用权威数据
    if name in auth_lookup:
        return round(auth_lookup[name])

    # 否则用行业总量 × 占比系数
    industry = occ["industry"]
    ind_data = industry_lookup.get(industry, {})
    ind_emp = ind_data.get("employment_wan", 0)

    if ind_emp > 0 and occ["share"] > 0:
        return round(ind_emp * occ["share"])

    # fallback: 返回一个合理默认值
    return 50


def compute_salary(occ, industry_lookup, salary_ref_lookup):
    """计算职业薪酬（万元/年）"""
    name = occ["name"]
    industry = occ["industry"]
    ind_data = industry_lookup.get(industry, {})
    ind_avg = ind_data.get("avg_salary_yuan", 0)

    # 行业平均转为万元
    ind_avg_wan = ind_avg / 10000 if ind_avg > 0 else 8.0

    # 基于行业平均 × 职业薪酬倍率
    multiplier = SALARY_MULTIPLIERS.get(name, 1.0)
    industry_based = ind_avg_wan * multiplier

    # 如果有职业级薪酬参考数据，加权融合
    ref_salary = salary_ref_lookup.get(name)
    if ref_salary:
        # 行业基础 40% + 职业参考 60%
        final = industry_based * 0.4 + ref_salary * 0.6
    else:
        final = industry_based

    # 保留一位小数，最低 2 万
    return max(round(final, 1), 2.0)


def compute_growth(occ, industry_lookup):
    """计算增长率"""
    # 基础行业年均增长率（五经普 vs 四经普，2018-2023，5年）
    INDUSTRY_GROWTH_BASE = {
        "农林牧渔业": -0.03,
        "采矿业": -0.04,
        "制造业": -0.01,
        "电力热力燃气及水生产和供应业": 0.02,
        "建筑业": -0.02,
        "批发和零售业": 0.02,
        "交通运输仓储和邮政业": 0.01,
        "住宿和餐饮业": 0.01,
        "信息传输软件和信息技术服务业": 0.08,
        "金融业": 0.02,
        "房地产业": -0.03,
        "租赁和商务服务业": 0.04,
        "科学研究和技术服务业": 0.06,
        "水利环境和公共设施管理业": 0.02,
        "居民服务修理和其他服务业": 0.02,
        "教育": 0.02,
        "卫生和社会工作": 0.04,
        "文化体育和娱乐业": 0.03,
        "公共管理社会保障和社会组织": 0.01,
    }

    industry = occ["industry"]
    base = INDUSTRY_GROWTH_BASE.get(industry, 0.01)
    adj = occ.get("growth_adj", 0)
    total = base + adj

    # 格式化为百分比字符串
    pct = round(total * 100)
    if pct >= 0:
        return f"+{pct}%"
    else:
        return f"{pct}%"


def main():
    print("加载数据文件...")

    industry_data = load_json("industry_base.json")
    auth_data = load_json("authoritative_employment.json")
    salary_ref_data = load_json("occupation_salary_ref.json")

    industry_lookup = build_industry_lookup(industry_data)
    auth_lookup = build_authoritative_lookup(auth_data)
    salary_ref_lookup = build_salary_ref_lookup(salary_ref_data)

    print(f"行业数据: {len(industry_lookup)} 个行业")
    print(f"权威就业数据: {len(auth_lookup)} 个职业")
    print(f"薪酬参考数据: {len(salary_ref_lookup)} 个职业")

    results = []
    sources = []

    for occ in OCCUPATION_DEFS:
        name = occ["name"]

        employment = compute_employment(occ, industry_lookup, auth_lookup)
        salary = compute_salary(occ, industry_lookup, salary_ref_lookup)
        growth = compute_growth(occ, industry_lookup)
        education = occ["education"]

        # AI 评分
        from ai_scores_data import AI_SCORES
        ai_score_data = AI_SCORES.get(name, (5, "评分数据缺失"))
        ai_score = ai_score_data[0]
        rationale = ai_score_data[1]

        entry = {
            "name": name,
            "category": occ["category"],
            "industry": occ["industry"],
            "employment": employment,
            "salary": salary,
            "education": education,
            "growth": growth,
            "ai_score": ai_score,
            "rationale": rationale,
        }
        results.append(entry)

        # 数据溯源
        emp_source = "权威统计数据" if name in auth_lookup else f"行业拆分({occ['industry']})"
        sal_source = "职业参考+行业加权" if name in salary_ref_lookup else "行业平均×职业系数"
        sources.append({
            "name": name,
            "employment_source": emp_source,
            "salary_source": sal_source,
            "industry": occ["industry"],
        })

    # 写入结果
    output_path = BASE_DIR / "data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"已写入 {output_path} ({len(results)} 条记录)")

    # 写入数据溯源
    sources_doc = {
        "description": "AI Jobs CN 数据溯源文件",
        "generated": "2026-03-16",
        "global_sources": {
            "industry_employment": "第五次全国经济普查公报 (2024年12月发布, 统计时点2023年末)",
            "industry_salary": "国家统计局2024年城镇单位就业人员年平均工资 (2025年5月发布)",
            "education_employment": "教育部2024年全国教育事业发展统计公报",
            "health_employment": "国家卫健委2024年我国卫生健康事业发展统计公报",
            "legal_employment": "司法部/律师协会/注册会计师协会等行业统计",
            "gig_employment": "交通运输部/国家邮政局/新闻报道等公开数据",
            "salary_refs": "国家统计局分岗位工资数据 + 智联招聘/Indeed等招聘平台公开报告",
            "ai_scores": "基于AI对就业影响研究的专家评估 (评分标准0-10)",
        },
        "occupations": sources,
    }
    sources_path = BASE_DIR / "data_sources.json"
    with open(sources_path, "w", encoding="utf-8") as f:
        json.dump(sources_doc, f, ensure_ascii=False, indent=2)
    print(f"已写入 {sources_path}")

    # 验证
    validate(results, industry_lookup)


def validate(results, industry_lookup):
    """数据验证"""
    print("\n===== 验证 =====")

    total_emp = sum(r["employment"] for r in results)
    print(f"总就业人数: {total_emp} 万人")

    # 行业约束检查
    industry_sums = {}
    for occ_def, result in zip(OCCUPATION_DEFS, results):
        ind = occ_def["industry"]
        industry_sums[ind] = industry_sums.get(ind, 0) + result["employment"]

    # 灵活就业密集行业不受法人单位上限约束
    FLEX_INDUSTRIES = {"交通运输仓储和邮政业", "居民服务修理和其他服务业", "农林牧渔业"}
    violations = []
    for ind, total in industry_sums.items():
        if ind in FLEX_INDUSTRIES:
            continue
        ind_data = industry_lookup.get(ind, {})
        ind_emp = ind_data.get("employment_wan", 0)
        if ind_emp > 0 and total > ind_emp:
            violations.append(f"  {ind}: 职业之和 {total} > 行业总量 {ind_emp}")

    if violations:
        print("行业约束违反:")
        for v in violations:
            print(v)
    else:
        print("行业约束检查: 通过")

    # 薪资合理性
    salaries = [r["salary"] for r in results]
    print(f"薪资范围: {min(salaries):.1f} - {max(salaries):.1f} 万元/年")
    print(f"薪资均值: {sum(salaries)/len(salaries):.1f} 万元/年")

    # 学历分布
    edu_dist = {}
    for r in results:
        edu_dist[r["education"]] = edu_dist.get(r["education"], 0) + 1
    print(f"学历分布: {edu_dist}")


if __name__ == "__main__":
    main()
