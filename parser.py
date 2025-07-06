#!/usr/bin/env python3
"""
Lightweight Text Adventure NLP Parser
Uses small, efficient models suitable for client-side deployment
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

# import torch
from transformers import pipeline
import spacy
# from spacy import displacy
import warnings
warnings.filterwarnings("ignore")


@dataclass
class Entity:
    text: str
    label: str
    confidence: float
    start: int
    end: int


@dataclass
class Dependency:
    token: str
    pos: str
    dependency: str
    head: int


@dataclass
class ParsedCommand:
    subject: Optional[str]
    verbs: List[str]
    direct_object: Optional[str]
    indirect_object: Optional[str]
    prepositions: List[str]
    entities: List[Entity]
    dependencies: List[Dependency]
    original_text: str

    def to_contract_format(self) -> Dict[str, Any]:
        """Convert to format suitable for blockchain contracts"""
        return {
            "action": self.verbs[0] if self.verbs else "unknown",
            "subject": self.subject or "player",
            "target": self.direct_object,
            "modifier": self.indirect_object,
            "context": {
                "prepositions": self.prepositions,
                "entities": [{"text": e.text, "type": e.label}
                             for e in self.entities],
                "confidence": (min([e.confidence for e in self.entities])
                               if self.entities else 1.0)
            }
        }


class LightweightNLPParser:
    def __init__(self, use_spacy: bool = True, model_size: str = "small"):
        self.use_spacy = use_spacy
        self.model_size = model_size
        self.nlp = None
        self.ner_pipeline = None
        self.models_loaded = False

        print(f"Initializing lightweight parser "
              f"(use_spacy={use_spacy}, size={model_size})")

    def load_models(self) -> None:
        """Load lightweight models"""
        print("Loading lightweight NLP models...")

        if self.use_spacy:
            self._load_spacy_models()
        else:
            self._load_transformers_models()

        self.models_loaded = True
        print("Models loaded successfully!")

    def _load_spacy_models(self) -> None:
        """Load spaCy models - much smaller and faster"""
        try:
            # Try to load small English model (~15MB)
            model_name = "en_core_web_sm"
            if self.model_size == "tiny":
                # Even smaller if available
                model_name = "en_core_web_sm"  # Already the smallest

            print(f"  Loading spaCy model: {model_name}")
            self.nlp = spacy.load(model_name)

        except OSError:
            print("spaCy model not found. Install with:")
            print("python -m spacy download en_core_web_sm")
            print("Falling back to transformers...")
            self._load_transformers_models()

    def _load_transformers_models(self) -> None:
        """Load small transformer models as fallback"""
        try:
            # Use DistilBERT - much smaller than BERT (~250MB vs 1.3GB)
            print("  Loading DistilBERT NER model...")
            self.ner_pipeline = pipeline(
                "ner",
                model="distilbert-base-cased",  # ~250MB
                tokenizer="distilbert-base-cased",
                aggregation_strategy="simple",
                device=-1  # Force CPU to avoid GPU memory issues
            )

        except Exception as e:
            print(f"Failed to load transformer models: {e}")
            print("Using rule-based parsing only...")

    def extract_entities_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy"""
        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entity = Entity(
                text=ent.text,
                label=ent.label_,
                confidence=1.0,  # spaCy doesn't provide confidence by default
                start=ent.start_char,
                end=ent.end_char
            )
            entities.append(entity)

        return entities

    def extract_dependencies_spacy(self, text: str) -> List[Dependency]:
        """Extract dependencies using spaCy"""
        doc = self.nlp(text)
        dependencies = []

        for token in doc:
            dep = Dependency(
                token=token.text,
                pos=token.pos_,
                dependency=token.dep_,
                head=token.head.i if token.head != token else -1
            )
            dependencies.append(dep)

        return dependencies

    def extract_entities_transformers(self, text: str) -> List[Entity]:
        """Extract entities using transformers (fallback)"""
        if not self.ner_pipeline:
            return []

        try:
            results = self.ner_pipeline(text)
            entities = []

            for result in results:
                entity = Entity(
                    text=result['word'],
                    label=result['entity_group'],
                    confidence=result['score'],
                    start=result['start'],
                    end=result['end']
                )
                entities.append(entity)

            return entities

        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return []


    def _extract_grammatical_components_spacy(self, doc) -> Dict[str, Any]:
        """Extract grammatical components from spaCy doc"""
        subject = None
        verbs = []
        direct_objects = []
        indirect_object = None
        prepositions = []

        # Track nouns for pronoun resolution
        nouns = []

        for token in doc:
            if token.dep_ == "nsubj":
                subject = token.text
            elif token.pos_ == "VERB":
                verbs.append(token.text)
            elif token.dep_ == "dobj":
                if token.text.lower() in ["it", "this", "that", "them"]:
                    # Try to resolve pronoun
                    if nouns:
                        direct_objects.append(nouns[-1])  # Most recent
                    else:
                        direct_objects.append(token.text)
                else:
                    direct_objects.append(token.text)
            elif token.dep_ == "pobj":
                # For commands like "talk to John about the quest",
                # prioritize the first prepositional object
                if indirect_object is None:
                    indirect_object = token.text
            elif token.pos_ == "ADP":
                prepositions.append(token.text)
            elif token.pos_ == "ADV" and token.dep_ == "advmod":
                # Handle adverbial particles like "around" in "look around"
                prepositions.append(token.text)
            elif token.pos_ == "NOUN":
                nouns.append(token.text)

        # For compound commands, use the resolved object
        primary_object = direct_objects[0] if direct_objects else None
        if len(direct_objects) > 1:
            # If we have multiple objects and one is resolved from pronoun
            for obj in direct_objects:
                if obj in nouns:
                    primary_object = obj
                    break

        # Handle conversational wrappers - prioritize action over intent verbs
        conversational_verbs = {"want", "need", "would", "like", "try",
                                "going", "gonna"}
        action_verbs = [v for v in verbs
                        if v.lower() not in conversational_verbs]

        if action_verbs and len(verbs) > 1:
            # If we have both conversational and action verbs, prioritize
            verbs = action_verbs
            # For "I want to look at the ball", move indirect to direct
            if primary_object is None and indirect_object:
                primary_object = indirect_object
                indirect_object = None

        return {
            'subject': subject,
            'verbs': verbs,
            'direct_object': primary_object,
            'indirect_object': indirect_object,
            'prepositions': prepositions
        }

    def _extract_grammatical_components_fallback(self,
                                                 dependencies: List[Dependency]
                                                 ) -> Dict[str, Any]:
        """Extract components from dependency list (fallback)"""
        subject = next((d.token for d in dependencies
                       if d.dependency == 'nsubj'), None)
        verbs = [d.token for d in dependencies if d.pos == 'VERB']
        direct_object = next((d.token for d in dependencies
                             if d.dependency == 'dobj'), None)
        indirect_object = next((d.token for d in dependencies
                               if d.dependency == 'pobj'), None)
        prepositions = [d.token for d in dependencies if d.pos == 'ADP']

        return {
            'subject': subject,
            'verbs': verbs,
            'direct_object': direct_object,
            'indirect_object': indirect_object,
            'prepositions': prepositions
        }

    def parse(self, text: str) -> ParsedCommand:
        """Main parsing method"""
        if not text.strip():
            return ParsedCommand(
                subject=None, verbs=[], direct_object=None,
                indirect_object=None, prepositions=[], entities=[],
                dependencies=[], original_text=text
            )

        if not self.models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        if self.use_spacy and self.nlp:
            # Use spaCy - faster and more efficient
            doc = self.nlp(text)
            entities = self.extract_entities_spacy(text)
            dependencies = self.extract_dependencies_spacy(text)
            components = self._extract_grammatical_components_spacy(doc)

        else:
            # Use transformers fallback
            entities = self.extract_entities_transformers(text)
            dependencies = []  # Would need POS pipeline for this
            components = self._extract_grammatical_components_fallback(
                dependencies)

        return ParsedCommand(
            subject=components['subject'],
            verbs=components['verbs'],
            direct_object=components['direct_object'],
            indirect_object=components['indirect_object'],
            prepositions=components['prepositions'],
            entities=entities,
            dependencies=dependencies,
            original_text=text
        )

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        info = {
            "using_spacy": self.use_spacy and self.nlp is not None,
            "models_loaded": self.models_loaded
        }

        if self.use_spacy and self.nlp:
            info["spacy_model"] = self.nlp.meta["name"]
            info["spacy_version"] = self.nlp.meta["version"]
            info["estimated_size"] = "~15MB"
        elif self.ner_pipeline:
            info["transformer_model"] = "distilbert-base-cased"
            info["estimated_size"] = "~250MB"

        return info


def main():
    parser = argparse.ArgumentParser(
        description="Lightweight NLP Parser for Text Adventure Commands")
    parser.add_argument("text", nargs="?", help="Text to parse")
    parser.add_argument("--no-spacy", action="store_true",
                        help="Don't use spaCy (use transformers)")
    parser.add_argument("--model-size", choices=["small", "tiny"],
                        default="small", help="Model size preference")
    parser.add_argument("--output", choices=["human", "json", "contract"],
                        default="human", help="Output format")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode")
    parser.add_argument("--model-info", action="store_true",
                        help="Show model information")

    args = parser.parse_args()

    # Initialize parser
    nlp_parser = LightweightNLPParser(
        use_spacy=not args.no_spacy,
        model_size=args.model_size
    )

    try:
        nlp_parser.load_models()
    except KeyboardInterrupt:
        print("\nInterrupted during model loading")
        sys.exit(1)

    if args.model_info:
        print("\nModel Information:")
        info = nlp_parser.get_model_info()
        print(json.dumps(info, indent=2))
        return

    def process_text(text: str) -> None:
        """Process and display results"""
        if not text.strip():
            return

        try:
            result = nlp_parser.parse(text)

            if args.output == "json":
                print(json.dumps(asdict(result), indent=2))
            elif args.output == "contract":
                print(json.dumps(result.to_contract_format(), indent=2))
            else:  # human
                print(f"\nInput: '{result.original_text}'")
                print(f"Subject: {result.subject or 'implicit (you)'}")
                print(f"Verbs: {', '.join(result.verbs) or 'none'}")
                print(f"Direct Object: {result.direct_object or 'none'}")
                print(f"Indirect Object: {result.indirect_object or 'none'}")
                print(f"Prepositions: "
                      f"{', '.join(result.prepositions) or 'none'}")

                if result.entities:
                    print("\nEntities:")
                    for entity in result.entities:
                        print(f"  {entity.text} ({entity.label}) - "
                              f"confidence: {entity.confidence:.3f}")

                print(f"\nContract format:")
                print(json.dumps(result.to_contract_format(), indent=2))

        except Exception as e:
            print(f"Error processing '{text}': {e}")

    # Handle input
    if args.interactive:
        print("Interactive mode. Type 'quit' to exit.")
        try:
            while True:
                text = input("\n> ").strip()
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                process_text(text)
        except KeyboardInterrupt:
            print("\nGoodbye!")

    elif args.text:
        process_text(args.text)

    else:
        if sys.stdin.isatty():
            text = input("Enter command to parse: ").strip()
        else:
            text = sys.stdin.read().strip()
        process_text(text)


if __name__ == "__main__":
    main()
