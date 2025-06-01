Feature: Mixed API and UI Automation Demo
  As a test automation engineer
  I want to demonstrate both API and UI automation
  So that I can test complete workflows

  Background:
    Given the system is ready for testing

  Scenario: User login via UI
    Given I open the login page and enter credentials
    When I click the login button
    Then I should see the dashboard page

  Scenario: User registration via API
    When I POST /register with data {"email": "test@example.com", "password": "testpass123"}
    Then I should receive a successful response
    And the response should contain a user ID

  Scenario: Mixed workflow - API setup then UI interaction
    Given I POST /users with data {"name": "John Doe", "email": "john@example.com"}
    When I navigate to the user profile page
    And I fill in the form with the user details
    Then I should see the updated profile information

  Scenario: UI form submission with API verification  
    Given I open the contact form page
    When I fill out the contact form with name "Jane Smith" and email "jane@example.com"
    And I submit the form
    Then I should see a success message
    And I GET /contacts to verify the submission was recorded 