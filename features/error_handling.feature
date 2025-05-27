Feature: Error Handling and Edge Cases
  As a robustness tester
  I want to test error scenarios
  So that I can ensure the API handles edge cases properly

  Scenario: Attempt to create user with invalid data
    Given the API endpoint "/users"
    And the request body is
      """
      {
        "name": "",
        "email": "invalid-email"
      }
      """
    When I send a POST request
    Then the response status code should be 201

  Scenario: Attempt to update non-existent user
    Given the API endpoint "/users/99999"
    And the request body is
      """
      {
        "name": "Non-existent User",
        "email": "nonexistent@test.com"
      }
      """
    When I send a PUT request
    Then the response status code should be 500

  Scenario: Create post with missing required fields
    Given the API endpoint "/posts"
    And the request body is
      """
      {
        "title": "Post without user ID"
      }
      """
    When I send a POST request
    Then the response status code should be 201

  Scenario: Attempt to delete non-existent resource
    Given the API endpoint "/posts/99999"
    When I send a DELETE request
    Then the response status code should be 200

  Scenario: Test with malformed JSON structure
    Given the API endpoint "/comments"
    And the request body is
      """
      {
        "postId": "not-a-number",
        "name": "Test User",
        "email": "test@example.com",
        "body": "Testing with invalid postId type"
      }
      """
    When I send a POST request
    Then the response status code should be 201

  Scenario: Create resource with extra unexpected fields
    Given the API endpoint "/todos"
    And the request body is
      """
      {
        "userId": 1,
        "title": "Todo with extra fields",
        "completed": false,
        "extraField": "This should be ignored",
        "anotherField": 12345
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Todo with extra fields"

  Scenario: Test boundary values and limits
    Given the API endpoint "/albums"
    And the request body is
      """
      {
        "userId": 999999,
        "title": "Album with very long title that might exceed normal character limits and cause potential issues in the system"
      }
      """
    When I send a POST request
    Then the response status code should be 201
