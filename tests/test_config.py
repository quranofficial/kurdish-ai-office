from app.config import Settings


def test_telegram_admin_ids_parse_comma_separated_numeric_values():
    settings = Settings(office_admin_telegram_ids="12345, 67890, invalid,")
    assert settings.office_admin_telegram_id_list == {12345, 67890}


def test_default_gemini_model_is_configured():
    settings = Settings(_env_file=None)
    assert settings.gemini_model == "gemini-3.8-flash"
