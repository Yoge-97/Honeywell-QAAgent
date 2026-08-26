Feature: QA-1234 Submit Booking Form

  Background:
    * url baseUrl
    * path '/booking'

  @TC-001
  Scenario: TC-001 - Fill all mandatory fields and submit the booking form
    Given request { name: 'John Doe', number: '1234567890' }
    When method post
    Then status 200
    And match response.success == true
    And match response.message == '#present'

  @TC-002
  Scenario: TC-002 - Leave the Name field empty and submit the booking form
    Given request { name: '', number: '1234567890' }
    When method post
    Then status 400
    And match response.success != true

  @TC-003
  Scenario: TC-003 - Leave the Number field empty and submit the booking form
    Given request { name: 'John Doe', number: '' }
    When method post
    Then status 400
    And match response.success != true