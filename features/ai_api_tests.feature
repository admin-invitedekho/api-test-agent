Feature: AI-Driven API Testing
  As a tester
  I want to use natural language to test APIs
  So that I can write more intuitive and flexible test scenarios

  Scenario: Simple user retrieval test
    Given I want to test the JSONPlaceholder API
    When I get user information for user ID 1
    Then the response should contain the user's name and email
    And the status code should be 200

  Scenario: Create and validate a post
    Given I have a valid user in the system
    When I create a new blog post with title "AI Testing is Amazing"
    Then the post should be created successfully
    And the response should include an ID for the new post
