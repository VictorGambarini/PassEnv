from unittest.mock import Mock, patch

from passenv.completion import complete_pass_entries


class TestCompletion:
    def test_complete_pass_entries_success(self):
        with patch("passenv.completion.PassClient") as mock_client:
            mock_instance = Mock()
            mock_instance.list_entries.return_value = [
                "database/staging",
                "database/production",
                "api/keys",
            ]
            mock_client.return_value = mock_instance

            result = complete_pass_entries("database/")

            assert result == ["database/staging", "database/production"]

    def test_complete_pass_entries_error(self):
        with patch("passenv.completion.PassClient") as mock_client:
            mock_client.side_effect = Exception("Test error")

            result = complete_pass_entries("database/")

            assert result == []
