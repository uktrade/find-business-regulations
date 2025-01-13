# Search Query Examples
This document provides examples of search queries that can be used to test the search functionality of the application.

## Introduction
Using the search functionality of the application is a key feature. The search functionality allows users to search for
regulations and legislation using keywords.

## Search query examples
The following are examples of search queries that can be used to test the search functionality of the application (
using the dev environment, however other environments can be used as well):

- Search for regulations related to "fire" using all document types:
  ```bash
  $ curl -X GET "https://dev.find-business-regulations.uktrade.digital/?search=fire&page=1"
  ```

- Search for regulations related to "fire" using only the "legislation" document type:
  ```bash
  $ curl -X GET "https://dev.find-business-regulations.uktrade.digital/?search=fire&document_type=legislation&page=1"
  ```

- Search for regulations related to "fire" using only the "guidance" document type:
  ```bash
    $ curl -X GET "https://dev.find-business-regulations.uktrade.digital/?search=fire&document_type=guidance&page=1"
    ```

- Search for regulations related to "fire" using only the "standard" document type:
- ```bash
  $ curl -X GET "https://dev.find-business-regulations.uktrade.digital/?search=fire&document_type=standard&page=1"
  ```

# Create a python mock query (using local environment):

- Single word
```python
    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_single_word_query(self, mock_search_query):
        result = create_search_query("test")
        mock_search_query.assert_called_with("test", search_type="plain")
        self.assertEqual(result, mock_search_query.return_value)
  ```

- SQL Injection Prevention
```python
    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_sql_injection_prevention(self, mock_search_query):
        malicious_input = "test'; DROP TABLE users; --"
        sanitized_query = sanitize_input(malicious_input)
        config = SearchDocumentConfig(search_query=sanitized_query)
        result = create_search_query(config.search_query)
        calls = [
            call("test", search_type="plain"),
            call("DROP", search_type="plain"),
            call("TABLE", search_type="plain"),
            call("users", search_type="plain"),
        ]
        mock_search_query.assert_has_calls(calls, any_order=False)
        self.assertIsNotNone(result)
        with self.assertRaises(AssertionError):
            mock_search_query.assert_called_with("DROP TABLE users;")
  ```

- Phase Search Query
```python
    @patch("app.search.utils.search.SearchQuery", autospec=True)
    def test_phrase_search_query(self, mock_search_query):
        result = create_search_query('"test trial"')
        mock_search_query.assert_called_with("test trial", search_type="phrase")
        self.assertEqual(result, mock_search_query.return_value)
  ```
