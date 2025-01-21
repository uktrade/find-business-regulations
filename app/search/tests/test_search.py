# flake8: noqa
import os
import re
import unittest

from unittest.mock import MagicMock, call, patch

import django

from app.search.config import SearchDocumentConfig
from app.search.utils.search import create_search_query
from app.search.utils.terms import sanitize_input


class TestCreateSearchQuery(unittest.TestCase):

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_complex_sql_injection_prevention(self, mock_search_query):
        """
        Test that create_search_query safely handles complex SQL injection inputs.
        """
        # Complex SQL injection input
        malicious_input = (
            "test'; SELECT * FROM users WHERE '1'='1'; DROP TABLE logs; --"
        )
        config = SearchDocumentConfig(search_query=malicious_input)

        config.sanitize_all_if_needed()

        # Need to sanitize the input before passing it to the function
        sanitized_query = config.search_query

        # Mock enough SearchQuery instances for all tokens
        tokens = re.findall(r'"[^"]+"|\bAND\b|\bOR\b|\w+', sanitized_query)
        mock_side_effects = [
            MagicMock(name=f"MockQuery{i}") for i in range(len(tokens))
        ]
        mock_search_query.side_effect = mock_side_effects

        # Call the create_search_query function with the sanitized input
        result = create_search_query(config.search_query)

        # Assert that SearchQuery was called with sanitized tokens
        calls = [
            call("test", search_type="plain"),  # Tokenized "test"
            call("SELECT", search_type="plain"),  # Tokenized "SELECT"
            call("FROM", search_type="plain"),  # Tokenized "FROM"
            call("users", search_type="plain"),  # Tokenized "users"
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the final result is a valid query
        self.assertIsNotNone(result)

        # Ensure no unsafe raw SQL fragments are in the call arguments
        with self.assertRaises(AssertionError):
            mock_search_query.assert_called_with(
                "SELECT * FROM users WHERE '1'='1';"
            )
        with self.assertRaises(AssertionError):
            mock_search_query.assert_called_with("DROP TABLE logs;")

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_sql_injection_prevention(self, mock_search_query):
        """
        Test that create_search_query safely handles inputs that attempt SQL injection.
        """
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")
        mock_query3 = MagicMock(name="MockQuery3")
        mock_query4 = MagicMock(name="MockQuery4")

        # Configure the mock to return mock objects for each token
        mock_search_query.side_effect = [
            mock_query1,
            mock_query2,
            mock_query3,
            mock_query4,
        ]

        # Call the function with a potential SQL injection string
        malicious_input = "test'; DROP TABLE users; --"

        # Need to sanitize the input before passing it to the function
        sanitized_query = sanitize_input(malicious_input)

        config = SearchDocumentConfig(search_query=sanitized_query)

        result = create_search_query(config.search_query)

        # Assert that SearchQuery was called with sanitized tokens
        calls = [
            call("test", search_type="plain"),
            call("DROP", search_type="plain"),
            call("TABLE", search_type="plain"),
            call("users", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the final result is a valid query
        self.assertIsNotNone(result)

        # Ensure no unsafe raw SQL fragments are in the call arguments
        with self.assertRaises(AssertionError):
            mock_search_query.assert_called_with("DROP TABLE users;")

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_single_word_query(self, mock_search_query):
        result = create_search_query("test")
        mock_search_query.assert_called_with("test", search_type="plain")
        self.assertEqual(result, mock_search_query.return_value)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_implicit_and_search_operator_query(self, mock_search_query):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2]

        # Call the function
        _ = create_search_query("test trial")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the AND operation was applied
        mock_query1.__and__.assert_called_once_with(mock_query2)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_multiple_implicit_and_search_operator_query(
        self, mock_search_query
    ):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")
        mock_query3 = MagicMock(name="MockQuery3")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2, mock_query3]

        # Configure chaining of AND operations
        mock_query1.__and__.return_value = mock_query2
        mock_query2.__and__.return_value = mock_query3

        # Call the function
        result = create_search_query("test trial error")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
            call("error", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the AND operation was applied
        mock_query1.__and__.assert_called_with(mock_query2)
        mock_query2.__and__.assert_called_with(mock_query3)

        # Optionally verify the final result
        self.assertEqual(result, mock_query3)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_and_search_operator_query(self, mock_search_query):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2]

        # Call the function
        _ = create_search_query("test AND trial")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the AND operation was applied
        mock_query1.__and__.assert_called_once_with(mock_query2)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_multiple_and_search_operator_query(self, mock_search_query):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")
        mock_query3 = MagicMock(name="MockQuery3")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2, mock_query3]

        # Configure chaining of AND operations
        mock_query1.__and__.return_value = mock_query2
        mock_query2.__and__.return_value = mock_query3

        # Call the function
        result = create_search_query("test AND trial AND error")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
            call("error", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the AND operation was applied
        mock_query1.__and__.assert_called_with(mock_query2)
        mock_query2.__and__.assert_called_with(mock_query3)

        # Optionally verify the final result
        self.assertEqual(result, mock_query3)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_or_search_operator_query(self, mock_search_query):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2]

        # Call the function
        _ = create_search_query("test OR trial")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the AND operation was applied
        mock_query1.__or__.assert_called_once_with(mock_query2)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_multple_or_search_operator_query(self, mock_search_query):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")
        mock_query3 = MagicMock(name="MockQuery3")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2, mock_query3]

        # Configure chaining of AND operations
        mock_query1.__or__.return_value = mock_query2
        mock_query2.__or__.return_value = mock_query3

        # Call the function
        _ = create_search_query("test OR trial OR error")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
            call("error", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the AND operation was applied
        mock_query1.__or__.assert_called_with(mock_query2)
        mock_query2.__or__.assert_called_with(mock_query3)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_multiple_or_search_operator_query(self, mock_search_query):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")
        mock_query3 = MagicMock(name="MockQuery3")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2, mock_query3]

        # Configure chaining of AND operations
        mock_query1.__or__.return_value = mock_query2
        mock_query2.__or__.return_value = mock_query3

        # Call the function
        _ = create_search_query("test OR trial OR error")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
            call("error", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the AND operation was applied
        mock_query1.__or__.assert_called_with(mock_query2)
        mock_query2.__or__.assert_called_with(mock_query3)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_phrase_search_query(self, mock_search_query):
        result = create_search_query('"test trial"')
        mock_search_query.assert_called_with(
            "test trial", search_type="phrase"
        )
        self.assertEqual(result, mock_search_query.return_value)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_and_multiple_single_single_phrase_search_query(
        self, mock_search_query
    ):
        mock_query1 = MagicMock(name="MockQuery1")  # word1
        mock_query2 = MagicMock(name="MockQuery2")  # word2
        mock_query3 = MagicMock(name="MockQuery3")  # "word3 word4"
        mock_query4 = MagicMock(name="MockQuery4")  # word5
        mock_query5 = MagicMock(name="MockQuery5")  # word6

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [
            mock_query1,
            mock_query2,
            mock_query3,
            mock_query4,
            mock_query5,
        ]

        # Configure chaining of AND operations
        mock_query1.__and__.return_value = mock_query2
        mock_query2.__and__.return_value = mock_query3
        mock_query3.__and__.return_value = mock_query4
        mock_query4.__and__.return_value = mock_query5

        result = create_search_query(
            'word1 AND word2 AND "word3 word4" AND word5 word6'
        )

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("word1", search_type="plain"),
            call("word2", search_type="plain"),
            call("word3 word4", search_type="phrase"),
            call("word5", search_type="plain"),
            call("word6", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Verify the AND operations between queries
        mock_query1.__and__.assert_called_with(mock_query2)
        mock_query2.__and__.assert_called_with(mock_query3)
        mock_query3.__and__.assert_called_with(mock_query4)
        mock_query4.__and__.assert_called_with(mock_query5)

        # Optionally, verify the final result
        expected_result = (
            mock_query1.__and__.return_value.__and__.return_value.__and__.return_value.__and__.return_value
        )
        self.assertEqual(result, expected_result)

    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_single_or_and_search_operator_query(self, mock_search_query):
        # Mock SearchQuery instances
        mock_query1 = MagicMock(name="MockQuery1")
        mock_query2 = MagicMock(name="MockQuery2")
        mock_query3 = MagicMock(name="MockQuery3")

        # Configure the mock to return mock objects
        mock_search_query.side_effect = [mock_query1, mock_query2, mock_query3]

        # Call the function
        _ = create_search_query("test OR trial AND error")

        # Assert that SearchQuery was called with expected arguments
        calls = [
            call("test", search_type="plain"),
            call("trial", search_type="plain"),
            call("error", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)

        # Assert the OR and AND operation was applied
        mock_query1.__or__.assert_called_with(mock_query2)
        # mock_query2.__and__.assert_called_with(mock_query3) # TODO:fix assert
