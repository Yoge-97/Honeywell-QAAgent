Feature: QA-1234 - Submit Booking Form

  Background:
    * url baseUrl
    * path '/booking'

  Scenario: TC-001 - Fill all mandatory fields and submit the booking form
    Given request { name: 'John Doe', number: '1234567890' }
    When method post
    Then status 200
    And match response contains { message: 'Success' }

  Scenario: TC-002 - Leave the Name field empty and submit the booking form
    Given request { name: '', number: '1234567890' }
    When method post
    Then match response !contains { message: 'Success' }

  Scenario: TC-003 - Leave the Number field empty and submit the booking form
    Given request { name: 'John Doe', number: '' }
    When method post
    Then match response !contains { message: 'Success' }