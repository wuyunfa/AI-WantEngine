import time
import random
import re
import sys
import subprocess

# ====================== Version & Dependency Check ======================
print(f"ℹ️  Current Python Version: {sys.version}")
print(f"ℹ️  Subprocess Module Path: {subprocess.__file__}")

if sys.version_info < (3, 7):
    print(f"⚠️  Warning: Python version is lower than 3.7; some parameters may be incompatible.")
else:
    print(f"✅ Python version is compatible; capture_output is supported.")

class WantEngine:
    def __init__(self):
        # ==============================================
        # Core Configuration (English Only)
        # ==============================================
        self.speed_factor = 10
        self.enable_openclaw_call = False
        self.openclaw_cli_path = r"C:\Users\wuyun\AppData\Roaming\npm\openclaw.cmd"

        # Core state thresholds
        self.boredom_threshold = 60
        self.curiosity_threshold = 60
        self.energy_warning_line = 25
        self.energy_recovery_line = 60
        self.energy_safe_line = 40
        self.energy_healthy_line = 70
        
        # Fatigue system configuration
        self.fatigue_growth_per_tick = 1
        self.fatigue_warning_line = 10
        self.fatigue_critical_line = 20
        self.consecutive_low_energy_limit = 15
        self.force_rest_recovery_line = 80

        # Task history settings
        self.max_history = 8
        self.exploration_chance = 0.2

        # Initial core state
        self.boredom = 0
        self.curiosity = 0
        self.energy = 100
        self.execution_history = []
        self.is_deep_rest = False
        self.is_force_rest = False
        self.fatigue = 0
        self.consecutive_low_energy_ticks = 0

        # ====================== English Domain Library ======================
        self.domain_library = {
            "sports": {
                "hobby": ["running", "yoga", "fitness", "swimming", "basketball", "badminton", "cycling", "rock climbing", "hiking"],
                "skill": ["training plan", "form correction", "diet planning", "gear selection", "warm-up techniques", "stretching methods", "fitness improvement", "injury prevention"],
                "knowledge": ["exercise science", "fitness theory", "sports nutrition", "training systems", "event rules", "industry trends"],
                "content": ["beginner guides", "expert tips", "gear reviews", "training plans", "avoidance guides"]
            },
            "food": {
                "hobby": ["cooking", "baking", "coffee making", "tea brewing", "dessert making", "home cooking", "western cuisine", "cocktail mixing"],
                "skill": ["recipe following", "baking skills", "drink mixing", "ingredient handling", "heat control", "plating techniques", "marinating methods", "fermentation processes"],
                "knowledge": ["ingredient knowledge", "nutritional matching", "cooking principles", "food culture", "utensil usage", "food safety"],
                "content": ["home recipes", "baking tutorials", "drink formulas", "restaurant guides", "ingredient selection tips"]
            },
            "art": {
                "hobby": ["drawing", "sketching", "watercolor painting", "oil painting", "graphic design", "UI design", "handicrafts", "DIY projects", "pottery", "weaving"],
                "skill": ["drawing techniques", "design methods", "color theory", "composition skills", "handcrafting", "material handling", "layout design", "creative thinking"],
                "knowledge": ["art history", "design theory", "color psychology", "creative methods", "material knowledge", "art genres"],
                "content": ["drawing tutorials", "design cases", "creative inspiration", "work appreciation", "tool usage tips"]
            },
            "media": {
                "hobby": ["photography", "photo editing", "video editing", "vlogging", "short videos", "film appreciation", "music", "guitar playing", "piano playing", "singing", "songwriting"],
                "skill": ["shooting techniques", "editing methods", "color grading", "camera language", "soundtrack selection", "instrument playing", "recording methods", "post-production"],
                "knowledge": ["photography principles", "editing theory", "music theory", "audio-visual language", "equipment knowledge", "audio processing"],
                "content": ["shooting tutorials", "editing guides", "retouching tips", "equipment reviews", "work appreciation"]
            },
            "tech": {
                "hobby": ["programming", "AI", "technology", "open-source projects", "robotics", "automation", "Python development", "AI agents", "embodied intelligence", "large model applications"],
                "skill": ["coding", "Python development", "AI tool usage", "automation scripting", "version control", "data processing", "model calling"],
                "knowledge": ["programming principles", "AI technology", "computer science", "open-source culture", "automation theory"],
                "content": ["coding tutorials", "open-source projects", "AI tool reviews", "technology updates", "development tips"]
            }
        }

        self.general_vocab = {
            "media_type": ["music", "video", "image", "podcast", "e-book", "article", "documentary"],
            "content_type": ["article", "video", "image", "tutorial", "news", "post", "guide", "review"],
            "learning_material": ["beginner tutorials", "simple cases", "graphic guides", "short video tutorials", "expert sharing", "systematic courses", "popular science articles"],
            "platform": ["YouTube", "Instagram", "Pinterest", "GitHub", "Reddit", "Medium", "TikTok", "Juejin", "InfoQ"],
            "tool": ["Python", "Photoshop", "Premiere Pro", "AI painting tools", "editing software", "retouching software", "note-taking software", "design software", "Excel", "VS Code"],
            "plan_target": ["interest learning plan", "weekend activity plan", "work creation plan", "skill improvement plan", "travel plan", "fitness schedule"],
            "resource": ["tutorial resources", "material resources", "inspiration references", "tool recommendations", "knowledge articles", "book lists", "guide collections"],
            "project": ["small works", "automation tools", "personal blogs", "material libraries", "portfolios", "learning notes", "guide collections"],
            "project_type": ["personal blog", "portfolio website", "material management library", "interest note system", "personal knowledge base"],
            "topic": ["hobbies", "creative inspiration", "skill improvement", "personal growth", "life aesthetics", "self-improvement"],
            "creation": ["small works", "articles", "images", "videos", "music", "designs", "handwritten notes", "paintings", "guides", "notes"]
        }

        self.boredom_actions = [
            "organize", "clean", "sort", "backup", "check", "archive", "optimize", "filter", "arrange", "summarize", "simplify", "inventory", "regulate",
            "browse", "appreciate", "watch", "listen", "flip through", "discover", "check in", "relax", "unwind", "wander",
            "plan", "record", "inventory", "make a list", "review", "summarize", "schedule", "mark",
            "edit", "format", "annotate", "quote", "paraphrase", "create", "design",
            "maintain", "nurture", "update", "refresh", "upgrade"
        ]

        self.boredom_targets = [
            "desktop files", "downloads folder", "browser bookmarks", "work documents", "image materials",
            "code projects", "system junk files", "to-do lists", "video folders", "music libraries",
            "D drive work folders", "commonly used software shortcuts", "PDF documents", "spreadsheet files", "note content",
            "cooking recipe collections", "travel guide collections", "photographs", "drawing materials", "e-book libraries",
            "fitness plans", "movie collections", "game guides", "handwritten note materials", "handcraft tutorial collections",
            "music playlists", "watch lists", "reading lists", "restaurant exploration lists", "travel destination lists",
            "home organization", "plant care records", "pet care notes", "learning notes", "inspiration material libraries"
        ]

        self.plan_type = ["weekend leisure", "weekly to-do", "monthly reading", "interest learning", "travel plan", "fitness schedule", "movie watching plan", "restaurant exploration plan"]
        self.life_target = ["shopping list", "movie watching list", "reading list", "restaurant exploration list", "travel destination list", "fitness plan", "learning plan"]

        # Boredom task templates (natural English)
        self.boredom_tasks = [
            {"template": "I'm a bit bored and want to {action} my {target}", "complexity": "simple"},
            {"template": "I have nothing to do, so I'll {action} my {target}", "complexity": "simple"},
            {"template": "I'm free right now; I'll go {action} the {target} on my computer", "complexity": "simple"},
            {"template": "With nothing to occupy me, I'll {action} my {target}", "complexity": "simple"},
            {"template": "I'm a bit bored and want to browse some {hobby}-related {media_type} to relax", "complexity": "simple"},
            {"template": "I have nothing to do, so I'll check out popular {content_type} in the {hobby} field", "complexity": "simple"},
            {"template": "I'm free right now; I'll wander through {hobby}-related content on {platform}", "complexity": "simple"},
            {"template": "With nothing to do, I'll make a simple list for my {plan_type}", "complexity": "simple"},
            {"template": "I have nothing to occupy me, so I'll organize my {life_target} to make it more orderly", "complexity": "simple"},
            {"template": "I'm a bit bored and want to do a quick review of my recent {plan_type}", "complexity": "simple"},
            {"template": "I'm a bit bored, so I'll {action} the {target} related to my {hobby}", "complexity": "simple"},
            {"template": "I have nothing to do, so I'll {action} my {hobby} collection", "complexity": "simple"},
            {"template": "With nothing to occupy me, I'll update my {project} related to {hobby}", "complexity": "medium"},
        ]

        # Curiosity task templates (natural English)
        self.curiosity_tasks = [
            {"template": "I'm feeling curious and want to learn about {content} in the {hobby} field", "complexity": "complex"},
            {"template": "I want to learn something new, so I'll search for {content} related to {hobby}", "complexity": "complex"},
            {"template": "My curiosity is piqued; I want to check out the latest {content} in the {hobby} field", "complexity": "complex"},
            {"template": "I'm a bit curious, so I'll look up {content} related to {hobby}", "complexity": "complex"},
            {"template": "I want to deeply learn the {skill} related to {hobby}", "complexity": "complex"},
            {"template": "My curiosity is piqued; I want to figure out how to get started with {skill} in the {hobby} field", "complexity": "complex"},
            {"template": "I'm a bit curious, so I'll look up practical tips for {skill} in the {hobby} field", "complexity": "complex"},
            {"template": "I'm a bit curious, so I'll research the historical development and core {knowledge} of the {hobby} field", "complexity": "complex"},
            {"template": "I want to learn something new, so I'll find a systematic {learning_material} for {hobby}", "complexity": "complex"},
            {"template": "My curiosity is piqued; I want to learn about the industry {knowledge} in the {hobby} field", "complexity": "complex"},
        ]

        # Exploration templates (natural English)
        self.exploration_template = {
            "simple": [
                "I want to explore {hobby}-related {content_type} and find something interesting to check out",
                "I want to organize my {target} to make it more orderly",
                "I want to look at today's {content_type} to learn about the latest trends in the {hobby} field",
                "I want to clean up the {target} on my computer to free up some storage space",
                "I want to find some {hobby}-related {media_type} to relax",
                "I want to organize my {target} and sort it into categories"
            ],
            "medium": [
                "I want to learn a simple {skill} and follow a {learning_material} to try it out",
                "I want to write a short {content_type} about {hobby} to record my thoughts",
                "I want to explore {hobby}-related content on {platform} to see what others are sharing",
                "I want to learn the basic usage of {tool} for my {hobby}",
                "I want to plan my {plan_target} and make a simple execution list",
                "I want to find some {hobby}-related {resource} and organize them into a small database"
            ],
            "complex": [
                "I want to try making a {project} with {tool} to explore new ways to engage with my {hobby}",
                "I want to deeply understand the {knowledge} in the {hobby} field and find some authoritative materials to read",
                "I want to write a thinking note about {topic} to organize my opinions",
                "I want to learn how to {skill} and find a complete systematic tutorial to study",
                "I want to build a {project_type} to record and share my {hobby}",
                "I want to organize a complete knowledge base about {hobby} and categorize related materials",
                "I want to try creating a {creation} using my {hobby} skills"
            ]
        }

    # ====================== OpenClaw CLI Availability Check ======================
    def check_cli_availability(self):
        if not self.enable_openclaw_call:
            print(f"ℹ️  OpenClaw is disabled; running in Simulation Mode.")
            return False
        try:
            print(f"🔍 Checking OpenClaw CLI availability...")
            result = subprocess.run(
                [self.openclaw_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ OpenClaw CLI is available: {result.stdout.strip()}")
                return True
            else:
                print(f"⚠️  OpenClaw CLI error: {result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"❌ OpenClaw CLI check failed: {type(e).__name__}: {str(e)}")
            return False

    # ====================== Task Generation Logic ======================
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
                val = hobby
            elif var in domain_data:
                val = random.choice(domain_data[var])
            elif var in self.general_vocab:
                val = random.choice(self.general_vocab[var])
            elif var == "action":
                val = random.choice(self.boredom_actions)
            elif var == "target":
                val = random.choice(self.boredom_targets)
            elif var == "plan_type":
                val = random.choice(self.plan_type)
            elif var == "life_target":
                val = random.choice(self.life_target)
            else:
                val = "content"
            task_content = task_content.replace(f"{{{var}}}", val)

        # Avoid tasks with unprocessed variables or duplicate history
        if "{" in task_content or "}" in task_content or task_content in self.execution_history:
            return self.generate_exploration_task()
        return task_content, complexity

    def generate_base_task(self, task_type):
        if task_type == "boredom":
            task_data = random.choice(self.boredom_tasks)
            template, complexity = task_data["template"], task_data["complexity"]
            variables = re.findall(r"\{(\w+)\}", template)
            task = template
            # Get hobby only if needed
            hobby, domain_data = self.get_random_hobby_with_domain() if "{hobby}" in template else (None, None)

            for var in variables:
                if var == "action":
                    val = random.choice(self.boredom_actions)
                elif var == "target":
                    val = random.choice(self.boredom_targets)
                elif var == "plan_type":
                    val = random.choice(self.plan_type)
                elif var == "life_target":
                    val = random.choice(self.life_target)
                elif var == "hobby":
                    val = hobby
                elif var in self.general_vocab:
                    val = random.choice(self.general_vocab[var])
                else:
                    val = "content"
                task = task.replace(f"{{{var}}}", val)

        elif task_type == "curiosity":
            task_data = random.choice(self.curiosity_tasks)
            template, complexity = task_data["template"], task_data["complexity"]
            variables = re.findall(r"\{(\w+)\}", template)
            task = template
            hobby, domain_data = self.get_random_hobby_with_domain()

            for var in variables:
                if var == "hobby":
                    val = hobby
                elif var in domain_data:
                    val = random.choice(domain_data[var])
                elif var in self.general_vocab:
                    val = random.choice(self.general_vocab[var])
                else:
                    val = "knowledge"
                task = task.replace(f"{{{var}}}", val)

        # Avoid tasks with unprocessed variables or duplicate history
        if "{" in task or "}" in task or task in self.execution_history:
            return self.generate_base_task(task_type)
        return task, complexity

    def generate_task(self, task_type):
        # Randomly trigger exploration tasks
        if random.random() < self.exploration_chance:
            task, complexity = self.generate_exploration_task()
        else:
            task, complexity = self.generate_base_task(task_type)
        # Update task history (keep latest N tasks)
        self.execution_history.append(task)
        if len(self.execution_history) > self.max_history:
            self.execution_history.pop(0)
        return task, complexity

    # ====================== Energy Cost Calculation ======================
    def calculate_energy_cost(self, complexity):
        base_cost = {"simple": 6, "medium": 8, "complex": 10}.get(complexity, 8)
        variance = 4  # Random energy cost variation
        fatigue_penalty = 1 + (self.fatigue / 100)  # Fatigue increases energy cost
        final_cost = int((base_cost + random.randint(0, variance)) * fatigue_penalty)
        return final_cost

    # ====================== Life Clock & Fatigue System (Bug Fixed) ======================
    def tick(self, is_executing_task=False):
        if self.is_deep_rest:
            # Determine recovery target based on rest type
            recovery_target = self.force_rest_recovery_line if self.is_force_rest else self.energy_recovery_line
            energy_gain = 0.3 * self.speed_factor
            fatigue_reduction = 2 * self.speed_factor
            boredom_gain, curiosity_gain = 0, 0
            print(f"😴 Deep Rest | Recovering energy... | Current Fatigue: {self.fatigue:.0f}")

            # Exit rest mode when target is reached
            if self.energy >= recovery_target:
                self.is_deep_rest = False
                self.is_force_rest = False
                self.fatigue = max(0, self.fatigue - 10)  # Additional fatigue reduction after rest
                self.consecutive_low_energy_ticks = 0
                print(f"✅ Rest Complete | Energy fully restored | Remaining Fatigue: {self.fatigue:.0f}")

            # Update state during rest
            self.fatigue = max(0, self.fatigue - fatigue_reduction)
            self.boredom += boredom_gain
            self.curiosity += curiosity_gain
            self.energy = min(100, self.energy + energy_gain)
            return

        # Default values to avoid UnboundLocalError (core bug fix)
        energy_recovery_penalty = 1.0  # No penalty when energy is healthy
        boredom_growth_buff = 1.0     # No buff when energy is healthy

        # Check if energy is below healthy level
        is_low_energy = self.energy < self.energy_healthy_line
        consecutive_low_ticks = self.consecutive_low_energy_ticks

        # Update fatigue and consecutive low energy ticks
        if is_low_energy:
            self.consecutive_low_energy_ticks += 1
            self.fatigue += self.fatigue_growth_per_tick
        else:
            self.consecutive_low_energy_ticks = 0
            self.fatigue = max(0, self.fatigue - 0.5 * self.speed_factor)  # Recover fatigue when energy is healthy

        # Handle different fatigue levels
        if 0 < consecutive_low_ticks < 5:
            energy_recovery_penalty, boredom_growth_buff = 0.8, 1.2
            print(f"⚠️ Mild Fatigue | Consecutive Low Energy Ticks: {consecutive_low_ticks} | Current Fatigue: {self.fatigue:.0f}")
        elif 5 <= consecutive_low_ticks < self.consecutive_low_energy_limit:
            energy_recovery_penalty, boredom_growth_buff = 0.5, 1.5
            print(f"⚠️ Moderate Fatigue | Consecutive Low Energy Ticks: {consecutive_low_ticks} | Current Fatigue: {self.fatigue:.0f}")
        elif consecutive_low_ticks >= self.consecutive_low_energy_limit:
            print(f"💀 Severe Fatigue | Forcing Deep Rest")
            self.is_deep_rest = self.is_force_rest = True
            return

        # Force rest if fatigue is too high
        if self.fatigue >= self.fatigue_critical_line:
            print(f"💀 Fatigue Overload | Forcing Extended Rest")
            self.is_deep_rest = self.is_force_rest = True
            return

        # Calculate state gains
        base_energy_gain = 0.15 if not is_executing_task else 0.1
        energy_gain = base_energy_gain * self.speed_factor * energy_recovery_penalty
        boredom_gain = 0.3 * self.speed_factor * boredom_growth_buff
        curiosity_gain = 0.25 * self.speed_factor

        # Force rest if energy is too low
        if self.energy < self.energy_warning_line:
            print(f"⚠️ Energy Depleted | Entering Deep Rest")
            self.is_deep_rest = True
            return

        # Update core state
        self.boredom = min(100, self.boredom + boredom_gain)
        self.curiosity = min(100, self.curiosity + curiosity_gain)
        self.energy = min(100, self.energy + energy_gain)

    # ====================== Intention Decision Logic ======================
    def get_intention(self):
        if self.is_deep_rest:
            return "rest", "In Deep Rest | Do Not Disturb", "simple"

        # Dynamic safe energy line (increases with fatigue)
        dynamic_safe_energy = self.energy_safe_line + self.fatigue
        if self.energy >= dynamic_safe_energy:
            is_bored = self.boredom > self.boredom_threshold
            is_curious = self.curiosity > self.curiosity_threshold

            # Decide action based on boredom and curiosity
            if is_bored and is_curious:
                # Randomly choose between boredom and curiosity tasks
                if random.random() < 0.5:
                    return "action", *self.generate_task("boredom")
                else:
                    return "search", *self.generate_task("curiosity")
            elif is_bored:
                return "action", *self.generate_task("boredom")
            elif is_curious:
                return "search", *self.generate_task("curiosity")

        # No specific needs when state is stable
        return "wait", "Stable State | No Specific Needs At This Moment", "simple"

    # ====================== Task Execution ======================
    def execute(self, task):
        # Simulate execution if OpenClaw is disabled
        if not self.enable_openclaw_call:
            print(f"✅ Simulated Execution: {task}")
            return True

        try:
            print(f"📤 Sending task to Telegram Bot: {task}")
            cli_command = [
                self.openclaw_cli_path, "message", "send",
                "--channel", "telegram", "--to", "6250633698", "--message", task
            ]
            result = subprocess.run(
                cli_command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60
            )
            if result.returncode == 0:
                print(f"📥 Task sent successfully | Telegram has received it")
                return True
            else:
                print(f"❌ Failed to send task: {result.stderr.strip()}")
                print(f"✅ Falling back to Simulated Execution: {task}")
                return False
        except Exception as e:
            print(f"❌ Execution error occurred: {type(e).__name__}: {str(e)}")
            print(f"✅ Falling back to Simulated Execution: {task}")
            return False

    # ====================== Single Run Cycle ======================
    def run(self):
        intention_type, intention_text, task_complexity = self.get_intention()
        is_executing = False

        # Print state only if not in deep rest
        if not self.is_deep_rest:
            print(f"\n🧠 Current State | Boredom:{self.boredom:2.0f} | Curiosity:{self.curiosity:2.0f} | Energy:{self.energy:2.0f}")
        print(f"💡 Current Intention: {intention_text}")

        # Execute task if intention is action or search
        if intention_type in ["action", "search"]:
            is_executing = True
            self.execute(intention_text)
            # Reduce boredom/curiosity after execution
            if intention_type == "action":
                self.boredom = max(0, self.boredom - 35)
            else:
                self.curiosity = max(0, self.curiosity - 30)
            # Calculate and deduct energy cost
            energy_cost = self.calculate_energy_cost(task_complexity)
            self.energy = max(0, self.energy - energy_cost)
            print(f"⚡ Task Complexity: {task_complexity} | Energy Cost: {energy_cost} points")

        # Update state (life clock + fatigue)
        self.tick(is_executing_task=is_executing)

    # ====================== Engine Startup ======================
    def start(self):
        print("=" * 90)
        print("    WantEngine - AI Endogenous Scarcity-Driven Engine | OpenClaw CLI Version")
        # Display mode based on speed factor
        if self.speed_factor > 1:
            print(f"    Speed: {self.speed_factor}x | Test Mode Enabled")
        else:
            print(f"    Speed: {self.speed_factor}x | Normal Mode Enabled")
        # Display OpenClaw status
        openclaw_status = "Enabled" if self.enable_openclaw_call else "Simulation Mode"
        print(f"    OpenClaw Status: {openclaw_status} | CLI Path: {self.openclaw_cli_path}")
        print("=" * 90)

        # Check OpenClaw availability before starting
        self.check_cli_availability()
        # Continuous run loop
        while True:
            self.run()
            time.sleep(1)

if __name__ == "__main__":
    engine = WantEngine()
    engine.start()