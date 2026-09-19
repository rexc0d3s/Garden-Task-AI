"""
Core game-design math for AI Garden: XP values, leveling curve, and
plant growth-stage thresholds. Kept in one module so game balance can be
tuned without touching route/business logic.
"""

DIFFICULTY_XP = {
    "easy": 20,
    "medium": 40,
    "hard": 75,
    "expert": 150,
}

# Growth stages, in order, keyed to the per-skill XP required to reach them.
GROWTH_STAGES = [
    ("seed", 0),
    ("sprout", 50),
    ("plant", 150),
    ("flower", 300),
    ("mature_plant", 500),
    ("tree", 800),
]

# XP required to go from level N to level N+1 grows linearly.
BASE_LEVEL_XP = 100
LEVEL_XP_STEP = 50


def xp_for_level(level: int) -> int:
    """XP required to advance FROM `level` TO `level + 1`."""
    return BASE_LEVEL_XP + (level - 1) * LEVEL_XP_STEP


def compute_level(total_xp: int) -> dict:
    """
    Given lifetime total XP, compute current level, XP into the current
    level, and XP required for the next level.
    """
    level = 1
    remaining = total_xp
    while remaining >= xp_for_level(level):
        remaining -= xp_for_level(level)
        level += 1
    return {
        "level": level,
        "xp_into_level": remaining,
        "xp_for_next_level": xp_for_level(level),
    }


def growth_stage_for_xp(skill_xp: int) -> str:
    """Return the growth-stage key for a given amount of skill XP."""
    stage = GROWTH_STAGES[0][0]
    for key, threshold in GROWTH_STAGES:
        if skill_xp >= threshold:
            stage = key
        else:
            break
    return stage


def growth_progress(skill_xp: int) -> dict:
    """
    Return stage info plus progress (0-1) toward the NEXT stage, so the
    frontend can animate a partial-growth state within a stage.
    """
    stages = GROWTH_STAGES
    current_index = 0
    for i, (key, threshold) in enumerate(stages):
        if skill_xp >= threshold:
            current_index = i
    current_key, current_threshold = stages[current_index]
    if current_index + 1 < len(stages):
        next_key, next_threshold = stages[current_index + 1]
        span = next_threshold - current_threshold
        progress = (skill_xp - current_threshold) / span if span else 1.0
    else:
        next_key = None
        progress = 1.0
    return {
        "stage": current_key,
        "next_stage": next_key,
        "progress_to_next": round(min(max(progress, 0.0), 1.0), 3),
        "xp": skill_xp,
    }
