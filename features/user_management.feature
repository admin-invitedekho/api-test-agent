Feature: User Management API Testing
  As an API tester
  I want to test user CRUD operations
  So that I can ensure the user management system works correctly

  Scenario: Create and retrieve a new user
    Given the API endpoint "/users"
    And the request body is
      """
      {
        "name": "Alice Johnson",
        "username": "alice_j",
        "email": "alice.johnson@example.com",
        "phone": "555-0123",
        "website": "alice-portfolio.com"
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Alice Johnson"
    And the response should contain "alice.johnson@example.com"
    And the response should contain "id"

  Scenario: Update user information and verify changes
    Given the API endpoint "/users/1"
    And the request body is
      """
      {
        "name": "Updated User Name",
        "email": "updated.email@example.com",
        "phone": "555-9999"
      }
      """
    When I send a PUT request
    Then the response status code should be 200
    And the response should contain "Updated User Name"
    And the response should contain "updated.email@example.com"

  Scenario: Attempt to retrieve non-existent user
    Given the API endpoint "/users/9999"
    When I send a GET request
    Then the response status code should be 404

  Scenario: Delete user and verify removal
    Given the API endpoint "/users/1"
    When I send a DELETE request
    Then the response status code should be 200
