Feature: QA-1002 - Product Search

  Background:
    * url baseUrl
    * path '/search'

  @TC-001
  Scenario: Search with a valid product name
    Given request { keyword: 'laptop' }
    When method post
    Then status 200

  @TC-002
  Scenario: Search with an unknown product
    Given request { keyword: 'unknownproduct123' }
    When method post
    Then status 404

  @TC-003
  Scenario: Search with an empty keyword
    Given request { keyword: '' }
    When method post
    Then status 400
