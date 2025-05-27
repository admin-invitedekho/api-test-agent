Feature: Example API Interaction

  Scenario: Retrieve user data
    Given the API endpoint "/users/1"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "name"

  Scenario: Create a new user
    Given the API endpoint "/users"
    And the request body is
      """
      {
        "name": "John Doe",
        "email": "john.doe@example.com"
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "id"
