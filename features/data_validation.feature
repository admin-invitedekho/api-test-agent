Feature: Data Validation and Cross-Entity Relationships
  As a data integrity tester
  I want to test complex data relationships
  So that I can ensure data consistency across the system

  Scenario: Create user and verify in user list
    Given the API endpoint "/users"
    And the request body is
      """
      {
        "name": "Integration Test User",
        "username": "integration_user",
        "email": "integration@test.com",
        "phone": "555-INTEGRATION",
        "website": "integration-test.com"
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Integration Test User"
    And the response should contain "integration@test.com"

  Scenario: Verify user appears in global user list
    Given the API endpoint "/users"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "Integration Test User"

  Scenario: Create post linked to test user
    Given the API endpoint "/posts"
    And the request body is
      """
      {
        "title": "Data Validation Test Post",
        "body": "This post is created to test data relationships and validation between users and posts.",
        "userId": 11
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Data Validation Test Post"
    And the response should contain "userId"

  Scenario: Verify post-user relationship
    Given the API endpoint "/posts"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "Data Validation Test Post"
    And the response should contain "userId"

  Scenario: Add comment linking to the test post
    Given the API endpoint "/comments"
    And the request body is
      """
      {
        "postId": 101,
        "name": "Validation Tester",
        "email": "validator@test.com",
        "body": "This comment validates the relationship between posts and comments."
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Validation Tester"
    And the response should contain "postId"

  Scenario: Create album for test user
    Given the API endpoint "/albums"
    And the request body is
      """
      {
        "userId": 11,
        "title": "Integration Test Album"
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Integration Test Album"
    And the response should contain "userId"

  Scenario: Add multiple todos for workflow validation
    Given the API endpoint "/todos"
    And the request body is
      """
      {
        "userId": 11,
        "title": "Validate data integrity",
        "completed": false
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Validate data integrity"

  Scenario: Verify all user-related data exists
    Given the API endpoint "/users/11/posts"
    When I send a GET request
    Then the response status code should be 200
