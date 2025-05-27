Feature: Photo Albums and Media Management
  As a media platform tester
  I want to test album and photo functionality
  So that I can ensure proper media organization

  Scenario: Create a new photo album
    Given the API endpoint "/albums"
    And the request body is
      """
      {
        "userId": 1,
        "title": "My Vacation Photos"
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "My Vacation Photos"
    And the response should contain "userId"

  Scenario: Add photos to an album
    Given the API endpoint "/photos"
    And the request body is
      """
      {
        "albumId": 1,
        "title": "Beach Sunset",
        "url": "https://example.com/photos/beach-sunset.jpg",
        "thumbnailUrl": "https://example.com/thumbs/beach-sunset-thumb.jpg"
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Beach Sunset"
    And the response should contain "albumId"
    And the response should contain "url"

  Scenario: Retrieve all photos in an album
    Given the API endpoint "/albums/1/photos"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "albumId"
    And the response should contain "title"

  Scenario: Update photo metadata
    Given the API endpoint "/photos/1"
    And the request body is
      """
      {
        "albumId": 1,
        "title": "Amazing Beach Sunset - Updated",
        "url": "https://example.com/photos/amazing-beach-sunset.jpg",
        "thumbnailUrl": "https://example.com/thumbs/amazing-beach-sunset-thumb.jpg"
      }
      """
    When I send a PUT request
    Then the response status code should be 200
    And the response should contain "Amazing Beach Sunset - Updated"

  Scenario: Create second album with different user
    Given the API endpoint "/albums"
    And the request body is
      """
      {
        "userId": 2,
        "title": "Work Conference Pictures"
      }
      """
    When I send a POST request
    Then the response status code should be 201
    And the response should contain "Work Conference Pictures"
    And the response should contain "userId"

  Scenario: Verify user-specific albums
    Given the API endpoint "/users/1/albums"
    When I send a GET request
    Then the response status code should be 200
    And the response should contain "userId"
    And the response should contain "title"
