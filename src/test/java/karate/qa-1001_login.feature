Feature: QA-1001 - Login

  Background:
    * url baseUrl
    * path '/login'

  @TC-001
  Scenario: Valid username and password
    Given request { username: 'testuser', password: 'password123' }
    When method post
    Then status 200

  @TC-002
  Scenario: Invalid password
    Given request { username: 'testuser', password: 'wrongpassword' }
    When method post
    Then status 401

  @TC-003
  Scenario: Empty username
    Given request { username: '', password: 'password123' }
    When method post
    Then status 400
