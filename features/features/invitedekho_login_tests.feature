Feature: InviteDeKho Login API Testing
  As a QA engineer
  I want to test the InviteDeKho authentication system
  So that I can ensure secure and reliable user login functionality

  @api
  Scenario: Successful login with valid credentials
    When I login to InviteDeKho with email "admin@invitedekho.com" and password "Test@123456"
    Then I should receive a successful authentication response
    And the response should contain a valid JWT token
    And the token should be properly formatted and not empty
    When I verify the JWT token structure
    Then the token should have the correct JWT format with header, payload, and signature

  @api
  Scenario: Login failure with invalid email
    When I try to login with invalid email "wrong@email.com" and password "Test@123456"
    Then I should receive an authentication error response
    And the error should indicate invalid credentials

  @api
  Scenario: Login failure with wrong password
    When I try to login with correct email "admin@invitedekho.com" but wrong password "WrongPassword"
    Then I should receive an authentication error response
    And the error should indicate invalid credentials

  @api
  Scenario: Login validation with empty credentials
    When I try to login with empty email and password fields
    Then I should receive a validation error response
    And the error should indicate missing required fields

  @api
  Scenario: Login validation with malformed email
    When I try to login with malformed email "not-an-email" and password "Test@123456"
    Then I should receive an email format validation error
    And the error should indicate invalid email format

  @api
  Scenario: Security testing with SQL injection attempt
    When I attempt to login with SQL injection in email field "admin@invitedekho.com'; DROP TABLE users; --"
    Then the system should safely handle the malicious input without errors
    And the response should indicate authentication failure not system error

  @api
  Scenario: Input length validation testing
    When I try to login with extremely long password over 1000 characters
    Then the system should handle the oversized input appropriately
    And the response should indicate validation error or truncation

  @api
  Scenario: JWT token validation and decoding
    When I successfully login with valid credentials "admin@invitedekho.com" and "Test@123456"
    And I extract the JWT token from the response
    Then I should be able to decode the token payload
    And the token should contain user identification information
    And the token should have proper expiration time

  @api
  Scenario: API endpoint failure testing
    Given the API is available at https://api.stage.invitedekho.com
    When I make a POST request to "https://api.stage.invitedekho.com/api/v999/nonexistent/login" with data {"email": "test@example.com", "password": "testpass"}
    Then the system should return a 404 not found error
    And the error response should be properly formatted
    And the logs should show the failed API call attempt
