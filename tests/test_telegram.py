from app.api.routes import split_telegram_message


def test_telegram_message_is_not_split_when_under_limit():
    assert split_telegram_message("سڵاو") == ["سڵاو"]


def test_telegram_message_splits_at_safe_boundaries():
    text = ("کوردی " * 900).strip()
    chunks = split_telegram_message(text, limit=1000)
    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)
    assert "".join(chunks).replace(" ", "") == text.replace(" ", "")
