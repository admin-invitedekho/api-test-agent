Feature: Todo Management and Task Tracking
  As a productivity app tester
  I want to test todo functionality
  So that I can ensure task management works properly

  Scenario: Create a new todo item
    Given the API endpoint "/todos"
    And the request body is
      """
      {
        "userId": 1,
        "title": "Complete API testing documentation",
        "completed": false
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Complete API testing documentation"
    And the response should contain "completed"
    And the response should contain "userId"

  Scenario: Mark todo as completed
    Given the API endpoint "/todos/1"
    And the request body is
      """
      {
        "userId": 1,
        "title": "Complete API testing documentation",
        "completed": true
      }
      """
    When I send a PUT request
    Then the response status code should be 200
    And the response should contain "completed"

  Scenario: Create multiple todos for workflow testing
    Given the API endpoint "/todos"
    And the request body is
      """
      {
        "userId": 1,
        "title": "Review test results",
        "completed": false
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Review test results"

  Scenario: Create priority todo item
    Given the API endpoint "/todos"
    And the request body is
      """
      {
        "userId": 2,
        "title": "Fix critical bug in payment system",
        "completed": false
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Fix critical bug"
    And the response should contain "payment system"

  Scenario: Retrieve user's todo list
    Given the API endpoint "/users/1/todos"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "userId"
    And the response should contain "title"
    And the response should contain "completed"

  Scenario: Delete completed todo
    Given the API endpoint "/todos/1"
    When I send a DELETE request
    Then the response status code should be 200

  Scenario: Verify todo deletion by attempting retrieval
    Given the API endpoint "/todos/1"
    When I send a GET request
    Then the response status code should be 404
