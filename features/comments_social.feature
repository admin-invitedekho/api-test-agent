Feature: Comments and Social Interactions
  As a social platform tester
  I want to test comment functionality
  So that I can ensure proper user interactions

  Scenario: Add comment to a blog post
    Given the API endpoint "/comments"
    And the request body is
      """
      {
        "postId": 1,
        "name": "John Commenter",
        "email": "john.commenter@example.com",
        "body": "This is a great blog post! Thanks for sharing this valuable information."
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "John Commenter"
    And the response should contain "great blog post"
    And the response should contain "postId"

  Scenario: Retrieve comments for a specific post
    Given the API endpoint "/posts/1/comments"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "postId"
    And the response should contain "email"

  Scenario: Create comment with validation data
    Given the API endpoint "/comments"
    And the request body is
      """
      {
        "postId": 2,
        "name": "Jane Reviewer",
        "email": "jane.reviewer@test.com",
        "body": "Excellent content! I particularly liked the section about error handling."
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Jane Reviewer"
    And the response should contain "error handling"

  Scenario: Update comment content
    Given the API endpoint "/comments/1"
    And the request body is
      """
      {
        "postId": 1,
        "name": "John Commenter Updated",
        "email": "john.updated@example.com",
        "body": "Updated comment: This is an even better blog post after reading it again!"
      }
      """
    When I send a PUT request
    Then the response status code should be 200
    And the response should contain "Updated comment"
    And the response should contain "john.updated@example.com"

  Scenario: Delete inappropriate comment
    Given the API endpoint "/comments/1"
    When I send a DELETE request
    Then the response status code should be 200
