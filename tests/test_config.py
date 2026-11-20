from app.config import Settings


def test_telegram_admin_ids_parse_comma_separated_numeric_values():
    settings = Settings(office_admin_telegram_ids="12345, 67890, invalid,")
    assert settings.office_admin_telegram_id_list == {12345, 67890}
