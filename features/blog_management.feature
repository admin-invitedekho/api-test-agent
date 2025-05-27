Feature: Blog Post Management with User Relationships
  As a blog system tester
  I want to test post creation and management
  So that I can ensure posts are properly linked to users

  Scenario: Create a blog post for an existing user
    Given the API endpoint "/posts"
    And the request body is
      """
      {
        "title": "My First Blog Post",
        "body": "This is the content of my first blog post. It contains useful information about API testing.",
        "userId": 1
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "My First Blog Post"
    And the response should contain "userId"
    And the response should contain "id"

  Scenario: Retrieve user's posts and validate relationship
    Given the API endpoint "/users/1/posts"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "userId"

  Scenario: Update blog post content
    Given the API endpoint "/posts/1"
    And the request body is
      """
      {
        "title": "Updated Blog Post Title",
        "body": "This is the updated content with more detailed information about advanced API testing techniques.",
        "userId": 1
      }
      """
    When I send a PUT request
    Then the response status code should be 200
    And the response should contain "Updated Blog Post Title"
    And the response should contain "advanced API testing"

  Scenario: Create multiple posts for data validation
    Given the API endpoint "/posts"
    And the request body is
      """
      {
        "title": "Second Post",
        "body": "Content for the second post",
        "userId": 2
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Second Post"

  Scenario: Retrieve all posts and validate multiple entries
    Given the API endpoint "/posts"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "title"
    And the response should contain "body"
    And the response should contain "userId"
