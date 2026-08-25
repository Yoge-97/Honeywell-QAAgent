Feature: QA-1234 Booking Form Submission
  As a guest, I want to submit the booking form so that I can complete my booking.

  Background:
    * url baseUrl
    * path '/booking'

  Scenario: TC-001 Fill all mandatory fields and submit the booking form
    Given request { name: 'John Doe', number: '1234567890' }
    When method post
    Then status 200
    And match response.successMessage == '#present'

  Scenario: TC-002 Leave the Name field empty and submit the booking form
    Given request { name: '', number: '1234567890' }
    When method post
    Then status 400
    And match response.successMessage != '#present'

  Scenario: TC-003 Leave the Number field empty and submit the booking form
    Given request { name: 'John Doe', number: '' }
    When method post
    Then status 400
    And match response.successMessage != '#present'