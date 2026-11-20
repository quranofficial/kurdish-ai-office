from dataclasses import dataclass

from app.agents.catalog import AGENTS, Agent


@dataclass(frozen=True)
class AgentMatch:
    agent: Agent
    score: int
    reason: str


def route_task(title: str, description: str = "") -> AgentMatch:
    text = f"{title} {description}".casefold()
    scored: list[tuple[int, Agent]] = []
    for agent in AGENTS:
        score = sum((3 if agent.key == "translator" else 2) if keyword in title.casefold() else 1 for keyword in agent.keywords if keyword in text)
        scored.append((score, agent))
    score, agent = max(scored, key=lambda item: (item[0], item[1].key == "manager"))
    if score == 0:
        agent = next(a for a in AGENTS if a.key == "manager")
        return AgentMatch(agent, 0, "No specialist keyword matched; routed to AI Manager for triage.")
    return AgentMatch(agent, score, f"Matched {score} routing points from the task title and description.")


def requires_human_approval(title: str, description: str = "") -> bool:
    text = f"{title} {description}".casefold()
    sensitive_actions = (
        "send email", "send message", "publish", "post publicly", "payment",
        "pay ", "transfer money", "delete", "remove account", "purchase",
        "buy ", "refund", "change password", "invite user",
        "ناردن", "بنێرە", "پەیام بنێرە", "ئیمەیڵ بنێرە",
        "بڵاوکردنەوە", "بڵاوبکەرەوە", "پۆستکردن", "ڕیکلامکردن",
        "پارەدان", "پارە بدە", "گواستنەوەی پارە", "پاره‌دان",
        "سڕینەوە", "بسڕەوە", "هەژمار بسڕەوە",
        "کڕین", "بیکڕە", "داواکردنی کڕین",
        "گەڕاندنەوەی پارە", "وشەی نهێنی بگۆڕە",
        "بەکارهێنەر زیاد بکە", "بانگهێشتکردنی بەکارهێنەر",
    )
    return any(term in text for term in sensitive_actions)
