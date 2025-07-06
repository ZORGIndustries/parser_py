Feature: NLP Parser for Text Adventure Commands
    As a text adventure game developer
    I want to parse natural language commands accurately
    So that players can interact with the game using intuitive language

    Background:
        Given I have a lightweight NLP parser

    Scenario: Parse simple command with direct object
        When I parse the command "take the sword"
        Then the action should be "take"
        And the target should be "sword"
        And the subject should be "player"

    Scenario: Parse command with implicit subject
        When I parse the command "open the door"
        Then the action should be "open"
        And the target should be "door"
        And the subject should be "player"

    Scenario: Parse compound command with pronoun resolution
        When I parse the command "take the ball and kick it at the window"
        Then the action should be "take"
        And the target should be "ball"
        And the modifier should be "window"
        And the verbs should contain "take" and "kick"
        And the prepositions should contain "at"

    Scenario: Parse command with pronoun referring to previous noun
        When I parse the command "pick up the key and use it"
        Then the action should be "pick"
        And the target should be "key"
        And the verbs should contain "pick" and "use"

    Scenario: Parse command with multiple objects
        When I parse the command "put the book on the table"
        Then the action should be "put"
        And the target should be "book"
        And the modifier should be "table"
        And the prepositions should contain "on"

    Scenario: Parse command with location preposition
        When I parse the command "go to the castle"
        Then the action should be "go"
        And the modifier should be "castle"
        And the prepositions should contain "to"

    Scenario: Parse command with complex pronoun resolution
        When I parse the command "grab the rope and tie it around the tree"
        Then the action should be "grab"
        And the target should be "rope"
        And the modifier should be "tree"
        And the verbs should contain "grab" and "tie"
        And the prepositions should contain "around"

    Scenario: Parse command with multiple pronouns
        When I parse the command "take the gem and put it in the box"
        Then the action should be "take"
        And the target should be "gem"
        And the modifier should be "box"
        And the verbs should contain "take" and "put"
        And the prepositions should contain "in"

    Scenario: Parse command with demonstrative pronoun
        When I parse the command "examine the scroll and read that"
        Then the action should be "examine"
        And the target should be "scroll"
        And the verbs should contain "examine" and "read"

    Scenario: Parse command with no explicit target
        When I parse the command "look around"
        Then the action should be "look"
        And the prepositions should contain "around"

    Scenario: Parse command with entity recognition
        When I parse the command "talk to John about the quest"
        Then the action should be "talk"
        And the modifier should be "John"
        And the prepositions should contain "to"
        And the prepositions should contain "about"
        And the entities should contain a person named "John"

    Scenario: Parse command with conversational wrapper
        When I parse the command "I want to look at the ball"
        Then the action should be "look"
        And the target should be "ball"
        And the prepositions should contain "at"
