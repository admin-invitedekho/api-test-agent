Feature: Complex Integration Testing with Multi-Step Data Validation
  As a developer
  I want to test complex scenarios with data validation between steps
  So that I can ensure the API maintains data integrity across operations

  Background:
    Given the API base URL is "https://jsonplaceholder.typicode.com"

  @complex @integration
  Scenario: Complete User Journey with Post and Comment Creation
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/1"
      }
      """
    Then the response status should be 200
    And the response should contain:
      """
      {
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz"
      }
      """
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/posts",
        "data": {
          "title": "My Complex Journey Post",
          "body": "This post is created by user ${response.id} named ${response.name}",
          "userId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    And the response should contain field "id" with numeric value
    And the response field "userId" should equal the previous response field "id"
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/comments",
        "data": {
          "name": "First Comment on Complex Post",
          "email": "commenter@example.com",
          "body": "This is a comment on post ${response.id}",
          "postId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    And the response field "postId" should equal the previous response field "id"

  @complex @data-flow
  Scenario: Album Creation with Photo Upload and User Validation
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/2"
      }
      """
    Then the response status should be 200
    And the response should contain field "address.geo.lat"
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/albums",
        "data": {
          "title": "Vacation Photos for ${response.name}",
          "userId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    And the response field "userId" should equal the previous response field "id"
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/photos",
        "data": {
          "title": "Beach Photo from Album ${response.id}",
          "url": "https://via.placeholder.com/600/771796",
          "thumbnailUrl": "https://via.placeholder.com/150/771796",
          "albumId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    And the response field "albumId" should equal the previous response field "id"
    And the response should contain field "url" with value "https://via.placeholder.com/600/771796"

  @complex @crud-chain
  Scenario: Todo Management with User Profile Updates
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/3"
      }
      """
    Then the response status should be 200
    And the response should contain field "company.name"
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/todos",
        "data": {
          "title": "Complete project for ${response.company.name}",
          "completed": false,
          "userId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    And the response field "completed" should be false
    When I execute API request "put_api" with parameters:
      """
      {
        "endpoint": "/todos/${response.id}",
        "data": {
          "title": "Complete project for company",
          "completed": true,
          "userId": "${response.userId}"
        }
      }
      """
    Then the response status should be 200
    And the response should contain field "id" with numeric value
    And the response should contain field "userId" with numeric value

  @complex @relationship-validation
  Scenario: Multi-Entity Relationship Validation Chain
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/4"
      }
      """
    Then the response status should be 200
    When I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/posts?userId=${response.id}"
      }
      """
    Then the response status should be 200
    And the response should be an array with length greater than 0
    When I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/comments?postId=${response[0].id}"
      }
      """
    Then the response status should be 200
    And the response should be an array
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/comments",
        "data": {
          "name": "Analysis Comment",
          "email": "analyst@example.com",
          "body": "This post by user has ${array_length(previous_response)} existing comments",
          "postId": "${second_to_last_response[0].id}"
        }
      }
      """
    Then the response status should be 201
    And the response should contain field "id" with numeric value

  @complex @error-recovery
  Scenario: Error Handling and Recovery with Data Validation
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/999"
      }
      """
    Then the response status should be 404
    When I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/5"
      }
      """
    Then the response status should be 200
    And the response should contain field "name"
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/posts",
        "data": {
          "title": "Recovery Post for ${response.name}",
          "body": "This post was created after handling user 999 error",
          "userId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    And the response field "title" should contain "Recovery Post for"
    And the response field "userId" should equal the previous response field "id"

  @complex @data-transformation
  Scenario: Data Transformation and Aggregation Workflow
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/6"
      }
      """
    Then the response status should be 200
    When I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/albums?userId=${response.id}"
      }
      """
    Then the response status should be 200
    And the response should be an array
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/posts",
        "data": {
          "title": "User ${previous_response[0].userId} has ${array_length(response)} albums",
          "body": "Statistics post with album count",
          "userId": "${previous_response[0].userId}"
        }
      }
      """
    Then the response status should be 201
    And the response field "title" should contain "has"
    And the response field "title" should contain "albums"

  @complex @nested-updates
  Scenario: Nested Entity Updates with Validation
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/posts/1"
      }
      """
    Then the response status should be 200
    And the response should contain field "userId"
    When I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/${response.userId}"
      }
      """
    Then the response status should be 200
    When I execute API request "put_api" with parameters:
      """
      {
        "endpoint": "/posts/${previous_response.id}",
        "data": {
          "title": "Updated by ${response.name}",
          "body": "This post was updated by user from ${response.address.city}",
          "userId": "${response.id}"
        }
      }
      """
    Then the response status should be 200
    And the response field "title" should contain "Updated by"
    And the response field "userId" should equal the previous response field "id"

  @complex @parallel-operations
  Scenario: Parallel Operation Validation
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/7"
      }
      """
    Then the response status should be 200
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/posts",
        "data": {
          "title": "First Parallel Post by ${response.name}",
          "body": "First post content",
          "userId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/posts",
        "data": {
          "title": "Second Parallel Post by same user",
          "body": "Second post content",
          "userId": "${previous_response.userId}"
        }
      }
      """
    Then the response status should be 201
    And the response should contain field "id" with numeric value
    When I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/posts?userId=${response.userId}"
      }
      """
    Then the response status should be 200
    And the response should be an array with length greater than 1

  @complex @conditional-logic
  Scenario: Conditional Logic Based on Response Data
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/8"
      }
      """
    Then the response status should be 200
    When I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/todos?userId=${response.id}&completed=false"
      }
      """
    Then the response status should be 200
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/todos",
        "data": {
          "title": "Conditional todo based on incomplete count: ${array_length(response)}",
          "completed": false,
          "userId": "${previous_response.id}"
        }
      }
      """
    Then the response status should be 201
    And the response field "title" should contain "Conditional todo based on incomplete count:"
    And the response field "userId" should equal the second-to-last response field "id"

  @complex @full-lifecycle
  Scenario: Complete Entity Lifecycle with Cross-References
    Given I execute API request "get_api" with parameters:
      """
      {
        "endpoint": "/users/9"
      }
      """
    Then the response status should be 200
    And the response should contain field "website"
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/albums",
        "data": {
          "title": "Portfolio for ${response.name} - ${response.website}",
          "userId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/photos",
        "data": {
          "title": "Profile Photo",
          "url": "https://via.placeholder.com/600/portfolio",
          "thumbnailUrl": "https://via.placeholder.com/150/portfolio",
          "albumId": "${response.id}"
        }
      }
      """
    Then the response status should be 201
    When I execute API request "post_api" with parameters:
      """
      {
        "endpoint": "/posts",
        "data": {
          "title": "Portfolio Announcement",
          "body": "Check out my new portfolio album ${previous_response.albumId} with photo ${response.id}",
          "userId": "${second_to_last_response.userId}"
        }
      }
      """
    Then the response status should be 201
    And the response field "body" should contain "portfolio album"
    And the response field "userId" should equal the third-to-last response field "userId"
    When I execute API request "delete_api" with parameters:
      """
      {
        "endpoint": "/photos/${second_to_last_response.id}"
      }
      """
    Then the response status should be 200
