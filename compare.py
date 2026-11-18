"""Compare NLTK and spaCy on a short Spanish text.

Runs tokenization, stemming, lemmatization, POS tagging, a rule-based money
extractor, named entity recognition and an ambiguous-word check.
"""

import argparse

import nltk
import spacy
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import TweetTokenizer, WordPunctTokenizer


DEFAULT_TEXT = (
    "Iberia devolvió 1.800 € a Lucía Fernández tras cancelar 3 vuelos en Bilbao. "
    "La cola llegaba hasta la puerta de embarque. "
    "Lo contó en https://www.aena.es con #VuelosCancelados."
)

AMBIGUOUS_WORD = "cola"
SECOND_SENTENCE = "El perro movía la cola."

STEM_VS_LEMMA_WORDS = ["devolvió", "vuelos", "cola", "llegaba", "puerta", "embarque", "contó"]

# Same amount with the currency symbol first, which the rule misses.
VARIANT_SENTENCE = "Iberia devolvió € 1.800 a Lucía."

MONEY_PATTERN = "MONEY: {<NUM><NOUN>}"


def header(title):
    print()
    print(title)
    print("-" * len(title))


def tokenization(text):
    header("A. Tokenization")
    print("WordPunctTokenizer:")
    print(WordPunctTokenizer().tokenize(text))
    print("TweetTokenizer:")
    print(TweetTokenizer().tokenize(text))


def stemming(text, stemmer):
    header("B. Stemming (NLTK Snowball)")
    print(f"{'WORD':<16} STEM")
    for word in TweetTokenizer().tokenize(text):
        if word.isalpha():
            print(f"{word:<16} {stemmer.stem(word)}")


def spacy_analysis(doc):
    header("C. Lemmas and POS tags (spaCy)")
    print(f"{'TOKEN':<24} {'LEMMA':<24} POS")
    for t in doc:
        print(f"{t.text:<24} {t.lemma_:<24} {t.pos_}")


def stem_vs_lemma(doc, stemmer, words):
    header("D. Stem vs. lemma")
    print(f"{'WORD':<16} {'STEM':<16} LEMMA")
    for t in doc:
        if t.text.lower() in words:
            print(f"{t.text:<16} {stemmer.stem(t.text):<16} {t.lemma_}")


def rule_extraction(nlp, sentences):
    header("E. Rule-based extraction (RegexpParser)")
    rule = nltk.RegexpParser(MONEY_PATTERN)
    print("Rule:", MONEY_PATTERN)

    for sentence in sentences:
        tagged = [(t.text, t.pos_) for t in nlp(sentence)]
        print()
        print("Sentence:", sentence)
        print("Tags:", tagged)
        print("Matches:")
        for chunk in rule.parse(tagged).subtrees():
            if chunk.label() == "MONEY":
                print(" ", chunk)


def named_entities(doc):
    header("F. Named entities (spaCy)")
    for ent in doc.ents:
        print(f"{ent.text:<36} {ent.label_}")


def ambiguous_word(nlp, sentences, word):
    header(f"G. Ambiguous word: '{word}'")
    for sentence in sentences:
        print("Sentence:", sentence)
        for t in nlp(sentence):
            if t.text.lower() == word:
                print(f"  {t.text}: lemma = {t.lemma_}, POS = {t.pos_}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Spanish text to analyse")
    args = parser.parse_args()
    text = args.text

    nlp = spacy.load("es_core_news_sm")
    stemmer = SnowballStemmer("spanish")
    doc = nlp(text)

    print("TEXT:", text)

    tokenization(text)
    stemming(text, stemmer)
    spacy_analysis(doc)
    stem_vs_lemma(doc, stemmer, STEM_VS_LEMMA_WORDS)
    rule_extraction(nlp, [text, VARIANT_SENTENCE])
    named_entities(doc)
    ambiguous_word(nlp, [text, SECOND_SENTENCE], AMBIGUOUS_WORD)


if __name__ == "__main__":
    main()
