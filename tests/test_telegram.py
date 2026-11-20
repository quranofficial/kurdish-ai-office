from app.api.routes import split_telegram_message, telegram_command_response


def test_telegram_message_is_not_split_when_under_limit():
    assert split_telegram_message("سڵاو") == ["سڵاو"]


def test_telegram_message_splits_at_safe_boundaries():
    text = ("کوردی " * 900).strip()
    chunks = split_telegram_message(text, limit=1000)
    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)
    assert "".join(chunks).replace(" ", "") == text.replace(" ", "")


def test_start_command_returns_kurdish_welcome():
    reply = telegram_command_response("/start", "")
    assert reply is not None
    assert "بەخێربێیت" in reply


def test_agents_command_lists_all_sixteen_agents():
    reply = telegram_command_response("/agents", "")
    assert reply is not None
    assert "AI CEO" in reply
    assert "Automation Agent" in reply
    assert len(reply.splitlines()) == 17


def test_help_command_includes_dashboard_only_when_https_url_is_configured():
    reply = telegram_command_response("/help", "https://office.example")
    assert reply is not None
    assert "https://office.example" in reply
    assert "/agents" in reply


def test_unknown_command_is_passed_to_ai():
    assert telegram_command_response("/unknown", "") is None


def test_projects_command_explains_current_setup_status():
    reply = telegram_command_response("/projects", "")
    assert reply is not None
    assert "Supabase" in reply


def test_report_command_is_transparent_about_unfinished_modules():
    reply = telegram_command_response("/report", "")
    assert reply is not None
    assert "١٦ ئەجێنت" in reply
    assert "چالاک نەکراون" in reply


def test_help_lists_projects_and_report_commands():
    reply = telegram_command_response("/help", "")
    assert reply is not None
    assert "/projects" in reply
    assert "/report" in reply
    assert "/tasks" in reply
    assert "/approve ID" in reply
