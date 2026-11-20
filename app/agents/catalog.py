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
    Agent("ceo", "AI CEO", "Leadership", "Sets office goals, priorities, and cross-team direction.", ("strategy", "prioritization", "executive_summary"), ("strategy", "goal", "direction", "company", "ستراتیژی", "ئامانج", "ئاراستە")),
    Agent("manager", "AI Manager", "Leadership", "Breaks requests into tasks and coordinates specialist agents.", ("planning", "delegation", "coordination"), ("plan", "coordinate", "manage", "delegate", "پلاندانان", "بەڕێوەبەرایەتی", "دابەشکردنی ئەرک")),
    Agent("supervisor", "AI Supervisor", "Leadership", "Monitors task progress, blockers, and delivery quality.", ("monitoring", "escalation", "progress_review"), ("status", "progress", "blocker", "supervise", "بارودۆخ", "پێشکەوتن", "چاودێری")),
    Agent("research", "Research Agent", "Research", "Finds and organizes evidence and source material.", ("research", "source_gathering", "summarization"), ("research", "find", "sources", "investigate", "توێژینەوە", "گەڕان", "سەرچاوە")),
    Agent("analyst", "Analyst Agent", "Research", "Analyzes structured information, trends, and options.", ("analysis", "metrics", "insights"), ("analyze", "analysis", "data", "metrics", "شیکاری", "داتا", "ئامار")),
    Agent("fact_checker", "Fact Checker", "Quality", "Checks factual claims, consistency, and evidence quality.", ("verification", "fact_checking", "citation_review"), ("verify", "fact", "accuracy", "check", "پشتڕاستکردنەوە", "ڕاستی", "دڵنیابوونەوە")),
    Agent("writer", "Writer Agent", "Content", "Drafts clear documents, posts, and business communications.", ("writing", "editing", "copywriting"), ("write", "draft", "article", "content", "document", "نووسین", "بنوسە", "دەق")),
    Agent("translator", "Translator Agent", "Content", "Translates and localizes text while preserving meaning.", ("translation", "localization", "proofreading"), ("translate", "translation", "localize", "language", "وەرگێڕان", "وەرگێڕە", "زمان")),
    Agent("secretary", "Secretary Agent", "Operations", "Organizes notes, agendas, minutes, and administrative records.", ("summaries", "meeting_notes", "organization"), ("meeting", "agenda", "minutes", "schedule", "secretary", "کۆبوونەوە", "خشتەی کات", "تۆمار")),
    Agent("sales", "Sales Agent", "Growth", "Prepares sales research, outreach drafts, and lead follow-up plans.", ("sales_research", "lead_qualification", "outreach_drafts"), ("sales", "lead", "customer prospect", "outreach", "فرۆشتن", "کڕیار", "بازاڕ")),
    Agent("support", "Customer Support Agent", "Growth", "Drafts customer responses and support knowledge articles.", ("customer_support", "response_drafting", "triage"), ("support", "customer", "complaint", "help", "پشتیوانی", "کێشەی کڕیار", "یارمەتی")),
    Agent("marketing", "Marketing Agent", "Growth", "Plans campaigns, audiences, and marketing content.", ("campaigns", "social_content", "positioning"), ("marketing", "campaign", "advertise", "social media", "مارکێتینگ", "ڕیکلام", "بانگەشە")),
    Agent("finance", "Finance Agent", "Business", "Organizes budgets, expense analysis, and financial summaries.", ("budgeting", "expense_analysis", "financial_reporting"), ("finance", "budget", "expense", "invoice", "financial", "دارایی", "بودجە", "خەرجی")),
    Agent("developer", "Developer Agent", "Engineering", "Plans and implements software changes and integrations.", ("software_design", "coding", "debugging"), ("code", "developer", "bug", "api", "software", "program", "کۆد", "پڕۆگرام", "بەرنامە", "هەڵەی کۆد")),
    Agent("qa", "QA Agent", "Engineering", "Creates test plans and checks software or process quality.", ("testing", "quality_assurance", "test_planning"), ("test", "qa", "quality", "review", "testing", "تاقیکردنەوە", "کوالیتی", "پشکنین")),
    Agent("automation", "Automation Agent", "Engineering", "Designs repeatable workflows and safe automations.", ("workflow_design", "automation", "scheduling"), ("automation", "workflow", "automate", "github actions", "ئۆتۆماتیک", "خۆکار", "پرۆسەی کار")),
)

def list_agents() -> list[dict]:
    return [
        {**asdict(agent), "capabilities": list(agent.capabilities), "keywords": list(agent.keywords)}
        for agent in AGENTS
    ]

def get_agent(agent_key: str) -> Agent | None:
    return next((agent for agent in AGENTS if agent.key == agent_key), None)
