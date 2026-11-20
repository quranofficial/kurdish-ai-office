from app.config import Settings


def test_telegram_admin_ids_parse_comma_separated_numeric_values():
    settings = Settings(office_admin_telegram_ids="12345, 67890, invalid,")
    assert settings.office_admin_telegram_id_list == {12345, 67890}


def test_default_openai_model_is_a_documented_api_model():
    settings = Settings(_env_file=None)
    assert settings.openai_model == "gpt-6.1-sol"
