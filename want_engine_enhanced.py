"""
AI-WantEngine Enhanced Version
AI-Powered Endogenous Scarcity-Driven Engine with improved configuration,
logging, error handling, and OpenClaw integration.
"""

import time
import random
import re
import sys
import subprocess
import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ====================== Configuration ======================
@dataclass
class WantEngineConfig:
    """Configuration class for WantEngine"""
    # Core settings
    speed_factor: int = 10
    enable_openclaw_call: bool = False
    openclaw_cli_path: str = "openclaw"
    
    # State thresholds
    boredom_threshold: int = 60
    curiosity_threshold: int = 60
    energy_warning_line: int = 25
    energy_recovery_line: int = 60
    energy_safe_line: int = 40
    energy_healthy_line: int = 70
    
    # Fatigue system
    fatigue_growth_per_tick: int = 1
    fatigue_warning_line: int = 10
    fatigue_critical_line: int = 20
    consecutive_low_energy_limit: int = 15
    force_rest_recovery_line: int = 80
    
    # Task history
    max_history: int = 8
    exploration_chance: float = 0.2
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: str) -> "WantEngineConfig":
        """Load configuration from JSON file"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        return cls()
    
    def to_file(self, config_path: str):
        """Save configuration to JSON file"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)


# ====================== Logger Setup ======================
def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Setup logger with console and optional file output"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    
    return logger


# ====================== Domain Library ======================
DOMAIN_LIBRARY = {
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

GENERAL_VOCAB = {
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


# ====================== WantEngine Class ======================
class WantEngine:
    """
    AI-Powered Endogenous Scarcity-Driven Engine
    Simulates human-like psychological states for autonomous AI task generation
    """
    
    def __init__(self, config: Optional[WantEngineConfig] = None):
        self.config = config or WantEngineConfig()
        self.logger = setup_logger(
            "WantEngine",
            self.config.log_level,
            self.config.log_file
        )
        
        # Initialize state
        self._init_state()
        
        # Log initialization
        self.logger.info("WantEngine initialized")
        self.logger.debug(f"Config: {asdict(self.config)}")
    
    def _init_state(self):
        """Initialize core state variables"""
        self.boredom = 0
        self.curiosity = 0
        self.energy = 100
        self.fatigue = 0
        self.execution_history: List[str] = []
        self.is_deep_rest = False
        self.is_force_rest = False
        self.consecutive_low_energy_ticks = 0
        self.tick_count = 0
    
    def check_environment(self) -> Dict[str, Any]:
        """Check Python environment and dependencies"""
        result = {
            "python_version": sys.version,
            "python_compatible": sys.version_info >= (3, 7),
            "subprocess_path": subprocess.__file__,
            "openclaw_available": self._check_openclaw()
        }
        
        self.logger.info(f"Environment check: Python {sys.version_info.major}.{sys.version_info.minor}")
        
        if not result["python_compatible"]:
            self.logger.warning("Python version < 3.7, some features may not work")
        
        return result
    
    def _check_openclaw(self) -> bool:
        """Check if OpenClaw CLI is available"""
        try:
            result = subprocess.run(
                [self.config.openclaw_cli_path, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"OpenClaw check failed: {e}")
            return False
    
    def update_state(self) -> Dict[str, Any]:
        """Update psychological state (boredom, curiosity, fatigue)"""
        self.tick_count += 1
        
        # Update boredom
        if not self.is_deep_rest and not self.is_force_rest:
            self.boredom = min(100, self.boredom + 1)
        
        # Update curiosity
        if not self.is_deep_rest:
            self.curiosity = min(100, self.curiosity + 1)
        
        # Update fatigue
        if not self.is_deep_rest:
            self.fatigue += self.config.fatigue_growth_per_tick
        
        # Check energy status
        if self.energy < self.config.energy_warning_line:
            self.consecutive_low_energy_ticks += 1
        else:
            self.consecutive_low_energy_ticks = 0
        
        # Force rest if needed
        if self.consecutive_low_energy_ticks >= self.config.consecutive_low_energy_limit:
            self.is_force_rest = True
            self.logger.warning("Entering forced rest mode due to low energy")
        
        state = {
            "tick": self.tick_count,
            "boredom": self.boredom,
            "curiosity": self.curiosity,
            "energy": self.energy,
            "fatigue": self.fatigue,
            "is_deep_rest": self.is_deep_rest,
            "is_force_rest": self.is_force_rest
        }
        
        self.logger.debug(f"State update: {state}")
        return state
    
    def generate_task(self) -> Optional[Dict[str, str]]:
        """Generate a task based on current psychological state"""
        # Check if we should rest
        if self.is_force_rest or self.is_deep_rest:
            self.logger.info("In rest mode, skipping task generation")
            return None
        
        # Check energy
        if self.energy < self.config.energy_warning_line:
            self.logger.warning("Low energy, suggesting rest")
            return {"type": "rest", "description": "Take a break to recover energy"}
        
        # Select domain based on state
        domain = self._select_domain()
        task_type = self._select_task_type()
        
        # Generate task description
        task = self._create_task_description(domain, task_type)
        
        # Add to history
        self.execution_history.append(task["description"])
        if len(self.execution_history) > self.config.max_history:
            self.execution_history.pop(0)
        
        self.logger.info(f"Generated task: {task}")
        return task
    
    def _select_domain(self) -> str:
        """Select a domain based on current state"""
        domains = list(DOMAIN_LIBRARY.keys())
        
        # If curious, prefer exploration
        if self.curiosity > self.config.curiosity_threshold:
            return random.choice(domains)
        
        # If bored, prefer variety
        if self.boredom > self.config.boredom_threshold:
            recent_domains = self._extract_recent_domains()
            available = [d for d in domains if d not in recent_domains]
            if available:
                return random.choice(available)
        
        return random.choice(domains)
    
    def _extract_recent_domains(self) -> List[str]:
        """Extract domains from recent task history"""
        domains = []
        for task in self.execution_history:
            for domain in DOMAIN_LIBRARY.keys():
                if domain in task.lower():
                    domains.append(domain)
        return domains
    
    def _select_task_type(self) -> str:
        """Select task type based on state"""
        types = ["hobby", "skill", "knowledge", "content", "project"]
        
        if random.random() < self.config.exploration_chance:
            return random.choice(types)
        
        # Prefer skill/knowledge when energy is high
        if self.energy > self.config.energy_healthy_line:
            return random.choice(["skill", "knowledge"])
        
        # Prefer hobby/content when energy is moderate
        return random.choice(["hobby", "content"])
    
    def _create_task_description(self, domain: str, task_type: str) -> Dict[str, str]:
        """Create a task description"""
        domain_data = DOMAIN_LIBRARY.get(domain, {})
        
        if task_type in domain_data:
            items = domain_data[task_type]
        else:
            items = GENERAL_VOCAB.get(task_type, ["explore"])
        
        item = random.choice(items)
        
        # Create task description
        templates = [
            f"Explore {item} in {domain}",
            f"Learn about {item} related to {domain}",
            f"Practice {item} for {domain}",
            f"Research {item} in the field of {domain}",
            f"Create content about {item} for {domain}"
        ]
        
        description = random.choice(templates)
        
        return {
            "type": task_type,
            "domain": domain,
            "item": item,
            "description": description
        }
    
    def execute_task(self, task: Dict[str, str]) -> bool:
        """Execute a task via OpenClaw CLI"""
        if not self.config.enable_openclaw_call:
            self.logger.info(f"OpenClaw disabled, would execute: {task['description']}")
            return False
        
        try:
            # Prepare OpenClaw command
            cmd = [
                self.config.openclaw_cli_path,
                "task",
                task["description"]
            ]
            
            self.logger.info(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info("Task executed successfully")
                # Consume energy
                self.energy = max(0, self.energy - 10)
                return True
            else:
                self.logger.error(f"Task failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Task execution timed out")
            return False
        except Exception as e:
            self.logger.error(f"Task execution error: {e}")
            return False
    
    def rest(self, deep: bool = False):
        """Enter rest mode to recover energy"""
        self.is_deep_rest = deep
        
        if deep:
            self.energy = min(100, self.energy + 20)
            self.fatigue = max(0, self.fatigue - 10)
            self.boredom = max(0, self.boredom - 15)
            self.logger.info("Deep rest: energy +20, fatigue -10, boredom -15")
        else:
            self.energy = min(100, self.energy + 10)
            self.fatigue = max(0, self.fatigue - 5)
            self.logger.info("Light rest: energy +10, fatigue -5")
        
        # Check if we can exit force rest
        if self.is_force_rest and self.energy >= self.config.force_rest_recovery_line:
            self.is_force_rest = False
            self.logger.info("Exiting forced rest mode")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            "tick_count": self.tick_count,
            "state": {
                "boredom": self.boredom,
                "curiosity": self.curiosity,
                "energy": self.energy,
                "fatigue": self.fatigue
            },
            "modes": {
                "deep_rest": self.is_deep_rest,
                "force_rest": self.is_force_rest
            },
            "history_count": len(self.execution_history),
            "openclaw_enabled": self.config.enable_openclaw_call,
            "openclaw_available": self._check_openclaw()
        }
    
    def run_cycle(self) -> Optional[Dict[str, Any]]:
        """Run one complete cycle: update state, generate task, execute"""
        # Update state
        state = self.update_state()
        
        # Generate task
        task = self.generate_task()
        
        if task is None:
            return {"state": state, "task": None, "executed": False}
        
        # Execute task
        executed = False
        if task.get("type") != "rest":
            executed = self.execute_task(task)
        
        return {
            "state": state,
            "task": task,
            "executed": executed
        }


# ====================== Main Entry ======================
def main():
    """Main entry point"""
    # Check environment
    print(f"ℹ️  Python Version: {sys.version}")
    
    # Load configuration
    config_path = os.path.expanduser("~/.wantengine_config.json")
    config = WantEngineConfig.from_file(config_path)
    
    # Create engine
    engine = WantEngine(config)
    
    # Check environment
    env = engine.check_environment()
    print(f"✅ Python compatible: {env['python_compatible']}")
    print(f"✅ OpenClaw available: {env['openclaw_available']}")
    
    # Run demo cycles
    print("\n🚀 Running demo cycles...\n")
    for i in range(5):
        result = engine.run_cycle()
        print(f"Cycle {i+1}:")
        print(f"  State: Energy={result['state']['energy']}, Boredom={result['state']['boredom']}")
        if result['task']:
            print(f"  Task: {result['task']['description']}")
            print(f"  Executed: {result['executed']}")
        else:
            print("  Task: Resting...")
        print()
        time.sleep(1)
    
    # Print final status
    status = engine.get_status()
    print("\n📊 Final Status:")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
