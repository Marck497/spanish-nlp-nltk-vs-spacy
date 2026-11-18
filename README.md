# spanish-nlp-nltk-vs-spacy

A side-by-side comparison of **NLTK** and **spaCy** on a short Spanish text: tokenization, stemming, lemmatization, part-of-speech tagging, rule-based extraction and named entity recognition. The aim is to see where each library does well and where it fails on real-looking input with a URL, a hashtag, a money amount and an ambiguous word.

The test text:

> Iberia devolvió 1.800 € a Lucía Fernández tras cancelar 3 vuelos en Bilbao. La cola llegaba hasta la puerta de embarque. Lo contó en https://www.aena.es con #VuelosCancelados.

*(Iberia refunded €1,800 to Lucía Fernández after cancelling 3 flights in Bilbao. The queue stretched to the boarding gate. She posted about it on https://www.aena.es with #VuelosCancelados.)*

## Usage

```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm

python compare.py                          # analyse the default text
python compare.py --text "Tu texto aquí"   # analyse your own Spanish text
```

The full output for the default text is in [`sample_output.txt`](sample_output.txt).

## Findings

### Tokenization

`WordPunctTokenizer` splits on every punctuation mark: `1.800` becomes `1`, `.`, `800`, the URL is broken into pieces and `#` is separated from the hashtag. `TweetTokenizer` keeps `1.800`, `https://www.aena.es` and `#VuelosCancelados` as single tokens, so it is the better choice for web or social media text.

### Stemming vs. lemmatization

The Snowball stemmer cuts suffixes using fixed rules, without a dictionary, so many stems aren't real words. spaCy's lemmatizer returns the dictionary form instead:

| Word | Stem (NLTK) | Lemma (spaCy) |
|---|---|---|
| devolvió | devolv | devolver |
| vuelos | vuel | vuelo |
| cola | col | cola |
| llegaba | lleg | llegar |
| puerta | puert | puerta |
| embarque | embarqu | embarque |
| contó | cont | contar |

The stem and the lemma differ in all seven words. The gap is largest for verbs, where spaCy recovers the infinitive and the stemmer only trims. Stemming can also land on a different, unrelated word: *cola* (queue/tail) becomes *col* (cabbage).

spaCy's lemmas are valid words except for the URL (`https://www.aena.`, truncated and tagged `NOUN`) and the hashtag, which it splits into `#` and a lowercase `vueloscancelados`.

### Rule-based extraction

A simple chunking rule with NLTK's `RegexpParser` over spaCy's POS tags:

```text
MONEY: {<NUM><NOUN>}
```

- **Hit:** `1.800 €`, because spaCy tags `1.800` as `NUM` and `€` as `NOUN`.
- **False positive:** `3 vuelos` (3 flights). The rule only sees tags, so any number followed by a noun matches.
- **False negative:** in `Iberia devolvió € 1.800 a Lucía` nothing is found, because the symbol comes first and spaCy tags `€` as `ADP` there.

A rule is fully transparent (you know exactly why it matched), but small changes in the text or in the tagger's output are enough to break it.

### Named entities

| Entity | Label | Verdict |
|---|---|---|
| Iberia | LOC | Wrong: it's an airline, not a place |
| Lucía Fernández | PER | Correct |
| Bilbao | LOC | Correct |
| La cola | MISC | Unexpected: a common noun |
| Lo contó en https://www.aena.es | MISC | Unexpected: grabs part of the sentence |
| VuelosCancelados | MISC | Treats the hashtag content as a miscellaneous entity |

spaCy misses `1.800 €` entirely (only the rule finds it), doesn't recognise Aena as an organisation, and often gets entity boundaries wrong.

### Ambiguous word

*Cola* means "queue" in *La cola llegaba hasta la puerta de embarque* and "tail" in *El perro movía la cola* (the dog wagged its tail). spaCy gives the same lemma (`cola`) and tag (`NOUN`) in both, so the part of speech is preserved but the meaning isn't distinguished. Only the surrounding context separates the two senses.

## Takeaways

- **NLTK** is simpler for tokenization, stemming and hand-written rules: small, independent tools that are easy to combine.
- **spaCy** is better for lemmas, POS tags and entities out of the box, but its model makes mistakes even on simple sentences and its output needs checking.
- For a news-processing pipeline, spaCy would be the main tool, with hand-written rules on top for well-known formats such as money amounts, which the model misses.

## Author

Juan Marcos Pairola. Originally developed for the *Language Processors* course.

## License

[MIT](LICENSE)
