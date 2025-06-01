Feature: User Profile Verification
  As a user of the InviteDekho platform
  I want to verify my profile information is displayed correctly
  So that I can ensure my account details are accurate

  Background:
    Given I navigate to "https://stage.invitedekho.com"
    And I wait for 3 seconds

  Scenario: Complete user profile verification workflow
    When I click the "Login" button
    And I wait for 3 seconds
    And I click the "Sign in with Email" button
    And I wait for 3 seconds
    And I enter "admin@invitedekho.com" in the email address field
    And I wait for 2 seconds
    And I enter "Test@123456" in the password field
    And I wait for 2 seconds
    And I click the "Sign in" button
    And I wait for 5 seconds for login to complete
    And I click the user icon button
    And I wait for 2 seconds
    And I click the "Profile" menu item
    And I wait for 3 seconds 