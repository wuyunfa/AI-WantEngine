import time
import requests
import random
import re
import sys
import subprocess

# 【调试用】先校验标准库subprocess是否正常
print(f"ℹ️  当前Python版本：{sys.version}")
print(f"ℹ️  subprocess模块路径：{subprocess.__file__}")
if sys.version_info < (3, 7):
    print(f"⚠️  警告：Python版本低于3.7，部分参数可能不兼容")
else:
    print(f"✅ Python版本符合要求，支持capture_output参数")

class WantEngine:
    def __init__(self):
        # ==============================================
        # 核心配置区
        # ==============================================
        self.speed_factor = 10  # 测试用10，正式运行用1
        self.enable_openclaw_call =  False#True  # True=启用真实OpenClaw调用，False=仅模拟
        self.openclaw_cli_path = r"C:\Users\wuyun\AppData\Roaming\npm\openclaw.cmd"#"openclaw"  # OpenClaw CLI命令

        # 核心状态阈值
        self.boredom_threshold = 60
        self.curiosity_threshold = 60
        self.energy_warning_line = 25
        self.energy_recovery_line = 60
        self.energy_safe_line = 40
        self.energy_healthy_line = 70
        
        # 疲劳惩罚系统配置
        self.fatigue_growth_per_tick = 1
        self.fatigue_warning_line = 10
        self.fatigue_critical_line = 20
        self.consecutive_low_energy_limit = 15
        self.force_rest_recovery_line = 80

        self.max_history = 8
        self.exploration_chance = 0.2

        # 核心状态变量
        self.boredom = 0
        self.curiosity = 0
        self.energy = 100
        self.execution_history = []
        self.is_deep_rest = False
        self.is_force_rest = False
        self.fatigue = 0
        self.consecutive_low_energy_ticks = 0

        # 全领域分类词库
        self.domain_library = {
            "sports": {
                "hobby": ["跑步", "瑜伽", "健身", "游泳", "篮球", "羽毛球", "普拉提", "骑行", "攀岩", "登山"],
                "skill": ["训练计划", "动作规范", "饮食搭配", "装备选择", "热身技巧", "拉伸方法", "体能提升", "损伤预防"],
                "knowledge": ["运动原理", "体能科学", "营养知识", "训练体系", "赛事规则", "行业动态"],
                "content": ["入门教程", "达人经验", "避坑指南", "训练计划", "装备测评"]
            },
            "food": {
                "hobby": ["美食", "烹饪", "烘焙", "咖啡", "茶饮", "甜品制作", "家常菜", "西餐", "调酒"],
                "skill": ["食谱制作", "烘焙技巧", "饮品调制", "食材处理", "火候控制", "摆盘技巧", "腌制方法", "发酵工艺"],
                "knowledge": ["食材知识", "营养搭配", "烹饪原理", "饮食文化", "器具使用", "食品安全"],
                "content": ["家常食谱", "烘焙教程", "饮品配方", "探店攻略", "食材挑选技巧"]
            },
            "art": {
                "hobby": ["绘画", "插画", "素描", "水彩", "油画", "设计", "平面设计", "UI设计", "手账", "手工DIY", "陶艺", "编织"],
                "skill": ["绘画技巧", "设计方法", "配色原理", "构图技巧", "手工制作", "材质处理", "排版设计", "创意构思"],
                "knowledge": ["艺术史", "设计理论", "色彩心理学", "创作方法", "材质知识", "流派风格"],
                "content": ["绘画教程", "设计案例", "创意灵感", "作品赏析", "工具使用技巧"]
            },
            "media": {
                "hobby": ["摄影", "拍照", "修图", "视频剪辑", "Vlog", "短视频", "影视欣赏", "音乐", "吉他", "钢琴", "唱歌", "作曲", "编曲"],
                "skill": ["拍摄技巧", "修图方法", "剪辑手法", "镜头语言", "配乐技巧", "乐器演奏", "录音方法", "后期制作"],
                "knowledge": ["摄影原理", "剪辑理论", "乐理知识", "视听语言", "器材知识", "音频处理"],
                "content": ["拍摄教程", "剪辑教学", "修图技巧", "器材测评", "作品赏析"]
            },
            "literature": {
                "hobby": ["阅读", "写作", "文学", "诗歌", "散文", "小说", "书评", "语言学习", "英语", "日语"],
                "skill": ["写作技巧", "阅读方法", "文案创作", "诗歌创作", "翻译技巧", "语法学习", "口语练习", "读书笔记"],
                "knowledge": ["文学史", "写作理论", "语言学", "文学流派", "修辞方法", "文化背景"],
                "content": ["书单推荐", "写作教程", "阅读方法", "语言学习技巧", "作品赏析"]
            },
            "travel": {
                "hobby": ["旅行", "户外", "徒步", "露营", "自驾游", "风景摄影", "登山", "潜水"],
                "skill": ["攻略制作", "露营技巧", "户外生存", "路线规划", "装备使用", "应急处理", "风景拍摄", "行李打包"],
                "knowledge": ["户外知识", "地理常识", "目的地文化", "装备知识", "气象常识", "环保理念"],
                "content": ["旅行攻略", "露营教程", "目的地推荐", "装备测评", "户外经验分享"]
            },
            "life": {
                "hobby": ["生活美学", "收纳整理", "家居装饰", "极简生活", "慢生活", "手账", "绿植养护", "宠物养护"],
                "skill": ["收纳技巧", "家居搭配", "空间规划", "断舍离方法", "绿植养护", "生活仪式感", "时间管理"],
                "knowledge": ["收纳原理", "空间设计", "植物养护知识", "生活哲学", "时间管理理论"],
                "content": ["收纳教程", "家居灵感", "生活技巧", "绿植养护方法", "时间管理方法"]
            },
            "tech": {
                "hobby": ["编程", "AI", "科技", "开源", "机器人", "自动化", "Python", "AI智能体", "具身智能", "大模型应用"],
                "skill": ["代码编写", "Python开发", "AI工具使用", "自动化脚本", "版本控制", "数据处理", "模型调用"],
                "knowledge": ["编程原理", "AI技术原理", "计算机知识", "开源文化", "自动化理论"],
                "content": ["编程教程", "开源项目", "AI工具测评", "技术进展", "开发技巧"]
            },
            "game": {
                "hobby": ["游戏", "桌游", "电子游戏", "游戏攻略", "游戏评测", "游戏设计"],
                "skill": ["游戏攻略制作", "玩法技巧", "游戏测评", "关卡设计", "数值平衡", "剧情创作"],
                "knowledge": ["游戏设计理论", "游戏史", "电竞行业", "开发引擎知识"],
                "content": ["游戏攻略", "玩法教程", "游戏测评", "行业动态", "作品赏析"]
            },
            "humanities": {
                "hobby": ["文化", "历史", "哲学", "人文", "心理学", "社会学"],
                "skill": ["史料分析", "逻辑思考", "案例分析", "读书笔记", "观点整理"],
                "knowledge": ["历史常识", "哲学理论", "心理学原理", "社会学知识", "文化研究"],
                "content": ["入门书籍", "科普文章", "学者观点", "历史事件解析", "理论科普"]
            }
        }

        # 通用领域词库
        self.general_vocab = {
            "media_type": ["音乐", "视频", "图片", "播客", "电子书", "文章", "纪录片"],
            "content_type": ["文章", "视频", "图片", "教程", "资讯", "作品", "分享", "攻略", "测评"],
            "learning_material": ["入门教程", "简单案例", "图文指南", "短视频教程", "达人分享", "系统课程", "科普文章"],
            "platform": ["B站", "知乎", "小红书", "抖音", "YouTube", "Instagram", "Pinterest", "掘金", "InfoQ"],
            "tool": ["Python", "PS", "PR", "AI绘画工具", "剪辑软件", "修图软件", "笔记软件", "设计软件", "Excel", "VS Code"],
            "plan_target": ["兴趣学习计划", "周末活动安排", "作品创作计划", "技能提升计划", "旅行计划", "健身安排"],
            "resource": ["教程资源", "素材资源", "灵感参考", "工具推荐", "知识文章", "书单推荐", "攻略合集"],
            "project": ["小作品", "自动化工具", "个人博客", "素材库", "作品集", "学习笔记", "攻略合集"],
            "project_type": ["个人博客", "作品集网站", "素材管理库", "兴趣笔记系统", "个人知识库"],
            "topic": ["兴趣爱好", "创作灵感", "技能提升", "个人成长", "生活美学", "自我提升"],
            "creation": ["小作品", "文章", "图片", "视频", "音乐", "设计", "手账", "绘画", "攻略", "笔记"]
        }

        # 全场景动作库
        self.boredom_action_categories = {
            "整理收纳": ["整理", "清理", "分类", "备份", "检查", "归档", "优化", "筛选", "排序", "归纳", "精简", "盘点", "规整"],
            "休闲放松": ["浏览", "欣赏", "观看", "收听", "翻阅", "种草", "打卡", "放松", "消遣", "闲逛"],
            "规划记录": ["规划", "记录", "盘点", "列清单", "整理", "归档", "复盘", "总结", "安排", "标记"],
            "轻量创作": ["编辑", "排版", "标注", "批注", "摘抄", "仿写", "记录", "整理", "创作", "设计"],
            "兴趣打理": ["打理", "养护", "更新", "维护", "整理", "归档", "备份", "优化", "刷新", "升级"]
        }
        self.boredom_actions = [action for category in self.boredom_action_categories.values() for action in category]

        # 无聊任务目标库
        self.boredom_targets = [
            "桌面文件", "下载文件夹", "浏览器书签", "工作文档", "图片素材",
            "代码项目", "系统垃圾文件", "待办清单", "视频文件夹", "音乐库",
            "D盘工作文件夹", "常用软件快捷方式", "PDF文档", "表格文件", "笔记内容",
            "美食食谱收藏", "旅行攻略收藏", "摄影照片", "绘画素材", "电子书库",
            "健身计划", "电影收藏", "游戏攻略", "手账素材", "手工教程收藏",
            "音乐歌单", "观影清单", "阅读书单", "探店清单", "旅行目的地清单",
            "家居收纳", "绿植养护记录", "宠物养护笔记", "学习笔记", "灵感素材库"
        ]
        self.plan_type = ["周末休闲", "下周待办", "月度阅读", "兴趣学习", "旅行计划", "健身安排", "观影计划", "探店计划"]
        self.life_target = ["购物清单", "观影清单", "阅读清单", "美食探店清单", "旅行目的地清单", "健身计划", "学习计划"]

        # 无聊任务模板库
        self.boredom_tasks = [
            {"template": "我现在有点无聊，想{action}一下{target}", "complexity": "simple"},
            {"template": "闲着没事，我来给{target}做个{action}", "complexity": "simple"},
            {"template": "有点无事可做，我去{action}电脑里的{target}", "complexity": "simple"},
            {"template": "闲着没事，我来{action}我的{target}", "complexity": "simple"},
            {"template": "我有点无聊，想找一些{hobby}相关的{media_type}放松一下", "complexity": "simple"},
            {"template": "闲着没事，我想看看{hobby}领域的热门{content_type}", "complexity": "simple"},
            {"template": "有点无事可做，我去{platform}上逛逛{hobby}相关的内容", "complexity": "simple"},
            {"template": "有点无事可做，我来列一个{plan_type}的简单清单", "complexity": "simple"},
            {"template": "闲着没事，我来整理一下我的{life_target}，让它更有条理", "complexity": "simple"},
            {"template": "我有点无聊，来做个近期{plan_type}的简单复盘", "complexity": "simple"},
            {"template": "我有点无聊，来{action}一下我的{hobby}相关的{target}", "complexity": "simple"},
            {"template": "闲着没事，我给我的{hobby}收藏做个{action}", "complexity": "simple"},
            {"template": "有点无事可做，我来更新一下我的{hobby}相关的{project}", "complexity": "medium"},
        ]

        # 求知任务模板库
        self.curiosity_tasks = [
            {"template": "我产生了求知欲，想了解{hobby}领域的{content}", "complexity": "complex"},
            {"template": "想学习点新东西，我去搜索{hobby}相关的{content}", "complexity": "complex"},
            {"template": "求知欲上来了，我想看看{hobby}领域的最新{content}", "complexity": "complex"},
            {"template": "有点好奇，我去查一下{hobby}领域的{content}", "complexity": "complex"},
            {"template": "我想深入学习一下{hobby}相关的{skill}", "complexity": "complex"},
            {"template": "求知欲上来了，我想了解{hobby}领域的{skill}怎么入门", "complexity": "complex"},
            {"template": "有点好奇，我去查一下{hobby}领域的{skill}有什么实用技巧", "complexity": "complex"},
            {"template": "有点好奇，我去查一下{hobby}领域的历史发展和核心{knowledge}", "complexity": "complex"},
            {"template": "想学习新东西，我找一套{hobby}的系统{learning_material}看看", "complexity": "complex"},
            {"template": "求知欲上来了，我想了解{hobby}领域的行业{knowledge}", "complexity": "complex"},
        ]

        # 随机探索任务模板库
        self.exploration_template = {
            "simple": [
                "我想探索一下{hobby}相关的{content_type}，找一些有趣的看看",
                "我想给我的{target}做个整理，让它更有条理",
                "我想看看今天的{content_type}，了解一下{hobby}领域的最新动态",
                "我想清理一下电脑里的{target}，释放一些存储空间",
                "我想找一些{hobby}相关的{media_type}，放松一下心情",
                "我想整理一下我的{target}，分类归档一下",
            ],
            "medium": [
                "我想学一个简单的{skill}，找个{learning_material}跟着试试",
                "我想写一段关于{hobby}的{content_type}，记录一下我的想法",
                "我想探索一下{platform}上的{hobby}相关内容，看看大家都在分享什么",
                "我想学习一下{tool}的基础用法，用于我的{hobby}爱好",
                "我想规划一下我的{plan_target}，列一个简单的执行清单",
                "我想找一些{hobby}相关的{resource}，整理成一个小资料库",
            ],
            "complex": [
                "我想尝试用{tool}做一个{project}，探索一下{hobby}领域的新玩法",
                "我想深入了解一下{hobby}领域的{knowledge}，找一些权威资料看看",
                "我想写一篇关于{topic}的思考笔记，整理一下我的观点",
                "我想学习如何{skill}，找一套完整的系统教程学习",
                "我想搭建一个{project_type}，用于记录和分享我的{hobby}爱好",
                "我想整理一套关于{hobby}的完整知识库，分类归档相关资料",
                "我想尝试创作一个{creation}，用我的{hobby}爱好做一个小作品",
            ]
        }

    # ==============================================
    # OpenClaw CLI可用性检查
    # ==============================================
    def check_cli_availability(self):
        if not self.enable_openclaw_call:
            print("ℹ️  OpenClaw调用已关闭，当前为模拟模式")
            return False
        try:
            print("🔍 正在检查OpenClaw CLI可用性...")
            result = subprocess.run(
                [self.openclaw_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ OpenClaw CLI可用：{result.stdout.strip()}")
                return True
            else:
                print(f"⚠️  OpenClaw CLI响应异常：{result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"❌ OpenClaw CLI检查失败：{type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    # 领域-内容强匹配任务生成
    def get_random_hobby_with_domain(self):
        domain_key = random.choice(list(self.domain_library.keys()))
        domain_data = self.domain_library[domain_key]
        hobby = random.choice(domain_data["hobby"])
        return hobby, domain_data

    def generate_exploration_task(self):
        complexity = random.choice(["simple", "medium", "complex"])
        template = random.choice(self.exploration_template[complexity])
        variables = re.findall(r"\{(\w+)\}", template)
        task_content = template

        hobby, domain_data = self.get_random_hobby_with_domain()

        for var in variables:
            if var == "hobby":
                replace_word = hobby
            elif var in domain_data:
                replace_word = random.choice(domain_data[var])
            elif var in self.general_vocab:
                replace_word = random.choice(self.general_vocab[var])
            elif var == "action":
                replace_word = random.choice(self.boredom_actions)
            elif var == "target":
                replace_word = random.choice(self.boredom_targets)
            elif var == "plan_type":
                replace_word = random.choice(self.plan_type)
            elif var == "life_target":
                replace_word = random.choice(self.life_target)
            else:
                replace_word = "内容"
            task_content = task_content.replace(f"{{{var}}}", replace_word)

        if "{" in task_content or "}" in task_content:
            return self.generate_exploration_task()
        if task_content in self.execution_history:
            return self.generate_exploration_task()
        
        return task_content, complexity

    def generate_base_task(self, task_type):
        if task_type == "boredom":
            task_data = random.choice(self.boredom_tasks)
            template = task_data["template"]
            complexity = task_data["complexity"]
            variables = re.findall(r"\{(\w+)\}", template)
            task = template

            hobby, domain_data = self.get_random_hobby_with_domain() if "{hobby}" in template else (None, None)

            for var in variables:
                if var == "action":
                    replace_word = random.choice(self.boredom_actions)
                elif var == "target":
                    replace_word = random.choice(self.boredom_targets)
                elif var == "plan_type":
                    replace_word = random.choice(self.plan_type)
                elif var == "life_target":
                    replace_word = random.choice(self.life_target)
                elif var == "hobby":
                    replace_word = hobby
                elif var in self.general_vocab:
                    replace_word = random.choice(self.general_vocab[var])
                else:
                    replace_word = "内容"
                task = task.replace(f"{{{var}}}", replace_word)

        elif task_type == "curiosity":
            task_data = random.choice(self.curiosity_tasks)
            template = task_data["template"]
            complexity = task_data["complexity"]
            variables = re.findall(r"\{(\w+)\}", template)
            task = template

            hobby, domain_data = self.get_random_hobby_with_domain()

            for var in variables:
                if var == "hobby":
                    replace_word = hobby
                elif var in domain_data:
                    replace_word = random.choice(domain_data[var])
                elif var in self.general_vocab:
                    replace_word = random.choice(self.general_vocab[var])
                else:
                    replace_word = "知识"
                task = task.replace(f"{{{var}}}", replace_word)

        if "{" in task or "}" in task:
            return self.generate_base_task(task_type)
        if task in self.execution_history:
            return self.generate_base_task(task_type)

        return task, complexity

    def generate_task(self, task_type):
        if random.random() < self.exploration_chance:
            task, complexity = self.generate_exploration_task()
        else:
            task, complexity = self.generate_base_task(task_type)

        self.execution_history.append(task)
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)

        return task, complexity

    # 能量消耗计算
    def calculate_energy_cost(self, complexity):
        base_cost_map = {"simple": 6, "medium": 8, "complex": 10}
        base_cost = base_cost_map.get(complexity, 8)
        variance = 4

        fatigue_penalty = 1 + (self.fatigue / 100)
        final_cost = int((base_cost + random.randint(0, variance)) * fatigue_penalty)
        
        return final_cost

    # 生命时钟+疲劳系统
    def tick(self, is_executing_task=False):
        if self.is_deep_rest:
            target_recovery_line = self.force_rest_recovery_line if self.is_force_rest else self.energy_recovery_line
            energy_growth = 0.3 * self.speed_factor
            fatigue_reduction = 2 * self.speed_factor
            boredom_growth = 0
            curiosity_growth = 0

            print(f"😴 深度休息中 | 能量恢复中... | 当前疲劳值：{self.fatigue}")

            if self.energy >= target_recovery_line:
                self.is_deep_rest = False
                self.is_force_rest = False
                self.fatigue = max(0, self.fatigue - 10)
                self.consecutive_low_energy_ticks = 0
                print(f"✅ 休息完成！精力充沛，重新开始活动 | 剩余疲劳值：{self.fatigue}")

            self.fatigue = max(0, self.fatigue - fatigue_reduction)

        else:
            is_low_energy = self.energy < self.energy_healthy_line
            is_critical_low_energy = self.energy < self.energy_safe_line

            if is_low_energy:
                self.consecutive_low_energy_ticks += 1
                self.fatigue += self.fatigue_growth_per_tick
            else:
                self.consecutive_low_energy_ticks = 0
                self.fatigue = max(0, self.fatigue - 0.5 * self.speed_factor)

            if 0 < self.consecutive_low_energy_ticks < 5:
                energy_recovery_penalty = 0.8
                boredom_growth_buff = 1.2
                print(f"⚠️ 轻度疲劳 | 连续低能量：{self.consecutive_low_energy_ticks}次 | 疲劳值：{self.fatigue}")
            elif 5 <= self.consecutive_low_energy_ticks < self.consecutive_low_energy_limit:
                energy_recovery_penalty = 0.5
                boredom_growth_buff = 1.5
                print(f"⚠️ 中度疲劳 | 连续低能量：{self.consecutive_low_energy_ticks}次 | 疲劳值：{self.fatigue}")
            elif self.consecutive_low_energy_ticks >= self.consecutive_low_energy_limit:
                energy_recovery_penalty = 0.2
                boredom_growth_buff = 2.0
                print(f"💀 重度疲劳 | 连续低能量超过上限！强制进入深度休息")
                self.is_deep_rest = True
                self.is_force_rest = True
                return
            else:
                energy_recovery_penalty = 1.0
                boredom_growth_buff = 1.0

            if self.fatigue >= self.fatigue_critical_line:
                print(f"💀 疲劳值过载！强制进入超长深度休息")
                self.is_deep_rest = True
                self.is_force_rest = True
                return

            if not is_executing_task:
                base_energy_growth = 0.15 * self.speed_factor
            else:
                base_energy_growth = 0.1 * self.speed_factor
            energy_growth = base_energy_growth * energy_recovery_penalty

            boredom_growth = 0.3 * self.speed_factor * boredom_growth_buff
            curiosity_growth = 0.25 * self.speed_factor

            if self.energy < self.energy_warning_line:
                self.is_deep_rest = True
                print(f"⚠️ 能量耗尽！进入深度休息模式")
                return

        self.boredom = min(100, self.boredom + boredom_growth)
        self.curiosity = min(100, self.curiosity + curiosity_growth)
        self.energy = min(100, self.energy + energy_growth)

    # 行为决策
    def get_intention(self):
        if self.is_deep_rest:
            return "rest", "深度休息中，请勿打扰", "simple"

        dynamic_energy_safe_line = self.energy_safe_line + self.fatigue
        if self.energy >= dynamic_energy_safe_line:
            boredom_over = self.boredom > self.boredom_threshold
            curiosity_over = self.curiosity > self.curiosity_threshold

            if boredom_over and curiosity_over:
                if random.random() < 0.5:
                    task, complexity = self.generate_task("boredom")
                    return "action", task, complexity
                else:
                    task, complexity = self.generate_task("curiosity")
                    return "search", task, complexity
            elif boredom_over:
                task, complexity = self.generate_task("boredom")
                return "action", task, complexity
            elif curiosity_over:
                task, complexity = self.generate_task("curiosity")
                return "search", task, complexity

        return "wait", "状态平稳，暂时没有特别的需求", "simple"

    # OpenClaw执行方法
    def execute(self, task):
        if not self.enable_openclaw_call:
            print(f"✅ 模拟执行：{task}")
            return True

        try:
            print(f"📤 正在发送到Telegram Bot (@WantEngine_bot)，任务：{task}")
            # 【Telegram专属命令，已填好你的Chat ID】
            cli_command = [
                self.openclaw_cli_path,
                "message",
                "send",
                "--channel",
                "telegram",
                "--to",
                "6250633698",  # 你的Chat ID，已填好
                "--message",
                task
            ]
            # 执行命令
            result = subprocess.run(
                cli_command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60
            )
            if result.returncode == 0:
                print(f"📥 发送成功！Telegram已收到任务")
                return True
            else:
                print(f"❌ 发送失败，错误：{result.stderr.strip()}")
                print(f"✅ 降级为模拟执行：{task}")
                return False
        except Exception as e:
            print(f"❌ 调用异常：{type(e).__name__}: {str(e)}")
            print(f"✅ 降级为模拟执行：{task}")
            return False

    # 单次运行逻辑
    def run(self):
        typ, text, complexity = self.get_intention()
        is_executing_task = False

        if not self.is_deep_rest:
            print(f"\n🧠 状态 | 无聊:{self.boredom:2.0f}  求知:{self.curiosity:2.0f}  能量:{self.energy:2.0f}")
        print(f"💡 想法：{text}")

        if typ in ["action", "search"]:
            is_executing_task = True
            self.execute(text)
            
            if typ == "action":
                self.boredom = max(0, self.boredom - 35)
            else:
                self.curiosity = max(0, self.curiosity - 30)
            
            energy_cost = self.calculate_energy_cost(complexity)
            self.energy = max(0, self.energy - energy_cost)
            print(f"⚡ 任务复杂度：{complexity} | 消耗能量：{energy_cost}点")

        self.tick(is_executing_task=is_executing_task)

    # 主启动方法
    def start(self):
        print("=" * 80)
        print("    WantEngine - AI 内生匮乏驱动引擎 | 对接OpenClaw CLI版")
        print(f"    当前加速倍数：{self.speed_factor}倍 | 测试模式" if self.speed_factor>1 else f"    当前加速倍数：{self.speed_factor}倍 | 正常模式")
        print(f"    OpenClaw调用：{'已启用' if self.enable_openclaw_call else '模拟模式'} | CLI命令：{self.openclaw_cli_path}")
        print("=" * 80)

        self.check_cli_availability()

        while True:
            self.run()
            time.sleep(1)

if __name__ == "__main__":
    engine = WantEngine()
    engine.start()