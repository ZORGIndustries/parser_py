#!/usr/bin/env python3
"""
BDD Step definitions for NLP Parser tests
"""

from parser import LightweightNLPParser, ParsedCommand
import sys
import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Add parent directory to path to import parser module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Load scenarios from the feature file
scenarios('../features/parser.feature')


@pytest.fixture
def parser_context():
    """Context to store parser and results between steps"""
    return {
        'parser': None,
        'result': None,
        'command': None
    }


@given("I have a lightweight NLP parser")
def given_parser(parser_context):
    """Initialize the NLP parser"""
    parser_context['parser'] = LightweightNLPParser(use_spacy=True,
                                                    model_size="small")
    parser_context['parser'].load_models()
    assert parser_context['parser'].models_loaded


@when(parsers.parse('I parse the command "{command}"'))
def when_parse_command(parser_context, command):
    """Parse the given command"""
    parser_context['command'] = command
    parser_context['result'] = parser_context['parser'].parse(command)
    assert parser_context['result'] is not None


@then(parsers.parse('the action should be "{expected_action}"'))
def then_action_should_be(parser_context, expected_action):
    """Check that the primary action matches expected"""
    result = parser_context['result']
    actual_action = result.verbs[0] if result.verbs else None
    assert actual_action == expected_action, \
        f"Expected action '{expected_action}', got '{actual_action}'"


@then(parsers.parse('the target should be "{expected_target}"'))
def then_target_should_be(parser_context, expected_target):
    """Check that the target object matches expected"""
    result = parser_context['result']
    assert result.direct_object == expected_target, \
        f"Expected target '{expected_target}', got '{result.direct_object}'"


@then(parsers.parse('the subject should be "{expected_subject}"'))
def then_subject_should_be(parser_context, expected_subject):
    """Check that the subject matches expected"""
    result = parser_context['result']
    # Handle implicit subjects
    actual_subject = result.subject if result.subject else "player"
    assert actual_subject == expected_subject, \
        f"Expected subject '{expected_subject}', got '{actual_subject}'"


@then(parsers.parse('the modifier should be "{expected_modifier}"'))
def then_modifier_should_be(parser_context, expected_modifier):
    """Check that the modifier (indirect object) matches expected"""
    result = parser_context['result']
    assert result.indirect_object == expected_modifier, \
        f"Expected modifier '{expected_modifier}', got '{result.indirect_object}'"


@then(parsers.parse('the verbs should contain "{verb1}" and "{verb2}"'))
def then_verbs_should_contain_two(parser_context, verb1, verb2):
    """Check that verbs list contains both specified verbs"""
    result = parser_context['result']
    assert verb1 in result.verbs, f"Expected verb '{verb1}' not found in {result.verbs}"
    assert verb2 in result.verbs, f"Expected verb '{verb2}' not found in {result.verbs}"


@then(parsers.parse(
    'the verbs should contain "{verb1}", "{verb2}" and "{verb3}"'))
def then_verbs_should_contain_three(parser_context, verb1, verb2, verb3):
    """Check that verbs list contains all three specified verbs"""
    result = parser_context['result']
    assert verb1 in result.verbs, f"Expected verb '{verb1}' not found in {result.verbs}"
    assert verb2 in result.verbs, f"Expected verb '{verb2}' not found in {result.verbs}"
    assert verb3 in result.verbs, f"Expected verb '{verb3}' not found in {result.verbs}"


@then('the prepositions should contain "to" and "about"')
def then_prepositions_should_contain_to_and_about(parser_context):
    """Check that prepositions list contains both 'to' and 'about'"""
    result = parser_context['result']
    assert "to" in result.prepositions, \
        f"Expected preposition 'to' not found in {result.prepositions}"
    assert "about" in result.prepositions, \
        f"Expected preposition 'about' not found in {result.prepositions}"


@then(parsers.parse('the prepositions should contain "{prep1}" and "{prep2}"'))
def then_prepositions_should_contain_two(parser_context, prep1, prep2):
    """Check that prepositions list contains both specified prepositions"""
    result = parser_context['result']
    assert prep1 in result.prepositions, \
        f"Expected preposition '{prep1}' not found in {result.prepositions}"
    assert prep2 in result.prepositions, \
        f"Expected preposition '{prep2}' not found in {result.prepositions}"


@then(parsers.parse('the prepositions should contain "{prep}"'))
def then_prepositions_should_contain_one(parser_context, prep):
    """Check that prepositions list contains the specified preposition"""
    result = parser_context['result']
    assert prep in result.prepositions, \
        f"Expected preposition '{prep}' not found in {result.prepositions}"


@then(parsers.parse('the entities should contain a person named "{name}"'))
def then_entities_should_contain_person(parser_context, name):
    """Check that entities list contains a person with the specified name"""
    result = parser_context['result']
    person_entities = [e for e in result.entities if e.label ==
                       "PERSON" and name.lower() in e.text.lower()]
    assert len(person_entities) > 0, \
        f"Expected person entity '{name}' not found in {[e.text for e in result.entities]}"

# Additional helper step definitions for debugging


@then("I should see the parsed result")
def then_show_result(parser_context):
    """Debug step to show the parsed result"""
    result = parser_context['result']
    print(f"\nParsed result for '{parser_context['command']}':")
    print(f"  Subject: {result.subject}")
    print(f"  Verbs: {result.verbs}")
    print(f"  Direct Object: {result.direct_object}")
    print(f"  Indirect Object: {result.indirect_object}")
    print(f"  Prepositions: {result.prepositions}")
    print(f"  Entities: {[(e.text, e.label) for e in result.entities]}")


@then("the parser should be loaded")
def then_parser_loaded(parser_context):
    """Check that the parser is properly loaded"""
    assert parser_context['parser'] is not None
    assert parser_context['parser'].models_loaded is True
