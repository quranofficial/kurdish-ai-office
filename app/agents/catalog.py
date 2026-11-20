from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class Agent:
    key: str
    name: str
    department: str
    description: str
    capabilities: tuple[str, ...]
    keywords: tuple[str, ...]

AGENTS: tuple[Agent, ...] = (
    Agent("ceo", "AI CEO", "Leadership", "Sets office goals, priorities, and cross-team direction.", ("strategy", "prioritization", "executive_summary"), ("strategy", "goal", "direction", "company")),
    Agent("manager", "AI Manager", "Leadership", "Breaks requests into tasks and coordinates specialist agents.", ("planning", "delegation", "coordination"), ("plan", "coordinate", "manage", "delegate")),
    Agent("supervisor", "AI Supervisor", "Leadership", "Monitors task progress, blockers, and delivery quality.", ("monitoring", "escalation", "progress_review"), ("status", "progress", "blocker", "supervise")),
    Agent("research", "Research Agent", "Research", "Finds and organizes evidence and source material.", ("research", "source_gathering", "summarization"), ("research", "find", "sources", "investigate")),
    Agent("analyst", "Analyst Agent", "Research", "Analyzes structured information, trends, and options.", ("analysis", "metrics", "insights"), ("analyze", "analysis", "data", "metrics")),
    Agent("fact_checker", "Fact Checker", "Quality", "Checks factual claims, consistency, and evidence quality.", ("verification", "fact_checking", "citation_review"), ("verify", "fact", "accuracy", "check")),
    Agent("writer", "Writer Agent", "Content", "Drafts clear documents, posts, and business communications.", ("writing", "editing", "copywriting"), ("write", "draft", "article", "content", "document")),
    Agent("translator", "Translator Agent", "Content", "Translates and localizes text while preserving meaning.", ("translation", "localization", "proofreading"), ("translate", "translation", "localize", "language")),
    Agent("secretary", "Secretary Agent", "Operations", "Organizes notes, agendas, minutes, and administrative records.", ("summaries", "meeting_notes", "organization"), ("meeting", "agenda", "minutes", "schedule", "secretary")),
    Agent("sales", "Sales Agent", "Growth", "Prepares sales research, outreach drafts, and lead follow-up plans.", ("sales_research", "lead_qualification", "outreach_drafts"), ("sales", "lead", "customer prospect", "outreach")),
    Agent("support", "Customer Support Agent", "Growth", "Drafts customer responses and support knowledge articles.", ("customer_support", "response_drafting", "triage"), ("support", "customer", "complaint", "help")),
    Agent("marketing", "Marketing Agent", "Growth", "Plans campaigns, audiences, and marketing content.", ("campaigns", "social_content", "positioning"), ("marketing", "campaign", "advertise", "social media")),
    Agent("finance", "Finance Agent", "Business", "Organizes budgets, expense analysis, and financial summaries.", ("budgeting", "expense_analysis", "financial_reporting"), ("finance", "budget", "expense", "invoice", "financial")),
    Agent("developer", "Developer Agent", "Engineering", "Plans and implements software changes and integrations.", ("software_design", "coding", "debugging"), ("code", "developer", "bug", "api", "software", "program")),
    Agent("qa", "QA Agent", "Engineering", "Creates test plans and checks software or process quality.", ("testing", "quality_assurance", "test_planning"), ("test", "qa", "quality", "review", "testing")),
    Agent("automation", "Automation Agent", "Engineering", "Designs repeatable workflows and safe automations.", ("workflow_design", "automation", "scheduling"), ("automation", "workflow", "automate", "github actions")),
)

def list_agents() -> list[dict]:
    return [
        {**asdict(agent), "capabilities": list(agent.capabilities), "keywords": list(agent.keywords)}
        for agent in AGENTS
    ]

def get_agent(agent_key: str) -> Agent | None:
    return next((agent for agent in AGENTS if agent.key == agent_key), None)
