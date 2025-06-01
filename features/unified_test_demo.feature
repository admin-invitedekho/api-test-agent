Feature: User Profile Verification
  As a user of the InviteDekho platform
  I want to verify my profile information is displayed correctly
  So that I can ensure my account details are accurate

  Scenario: Complete user profile verification workflow
    Given I navigate to "https://stage.invitedekho.com"
    When I click the "Login" button
    And I click the "Sign in with Email" button
    And I enter "admin@invitedekho.com" in the email address field
    And I enter "Test@123456" in the password field
    And I click the "Sign in" button
    And I click the user icon button
    And I click the "Profile" menu item