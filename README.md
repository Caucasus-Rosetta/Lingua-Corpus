### For data scientists, developers and whom it may concern: 
##### Some of the text materials are copyrighted, check out the multilingual sources section that links to the source, please be sure to obide the authors restrictions and limitaions. 
### For copyright owners:
##### The text materials here are used for research, if there are any concerns regarding having your text material on this repo, please contact us via email(s): daniel.abzakh@gmail.com, kalle@hilsenbek.de.

### Tools:
##### Composition of a training corpus
We can compose a specific training corpus and separate test files with the joined corpus script in the training directory:

    usage: join_corpus.py [-h] [--dictionary] [--numerate] [--paraphrase]
                          ll [ll ...] min_ratio max_ratio min_length max_words

    Process the corpus with paraphrases and the dictionary

    positional arguments:
      ll            the lengths for dictionary lists
      min_ratio     We only use translations with this minimum, parallel ratio
      max_ratio     We only use translations with this maximum, parallel ratio
      min_length    We only use translations with this minimum length
      max_words     We only use translations with this maximum words

    optional arguments:
      --dictionary  We use the dictionary as translation source
      --numerate    The dictionary list has a numeration
      --paraphrase  We paraphrase the filtered corpus

For example `python3 join_corpus.py --dictionary --paraphrase 1 0.7 2.25 10 50` results in the commited `06-19-2020_corpus` with a minimum range of 10 letters, max 50 words, a min ratio of 0,7 and max ratio of 2.25. The paraphrases are based on the filtered, training copus and are joined with the plain dictionary.

#### Multilingual sources:
-	koran - the islamic holy book (Quran)
-	Braveheart - the Braveheart movie.
-	Declaration of Human Rights.
-	Novyi_Zavet - the new testament (Bible) Possible alignment with the russian, new testament in https://github.com/christos-c/bible-corpus ?
-	http://abaza.org/  - russian, abkhazian
-   http://apsnyteka.org/ 
-   http://apsnypress.info/
-   https://tatoeba.org/
-   https://wol.jw.org/

#### Current Multilingual Corpuses:
1. Abkhazian Russian Parallel corpus (173445 lines).

#### Further resources
- A Review of Past Work and Future Challenges https://arxiv.org/pdf/2006.07264.pdf
- Tools and resources for open translation services: https://github.com/Helsinki-NLP/Opus-MT
- https://paperswithcode.com/task/low-resource-neural-machine-translation
- https://www.masakhane.io/ https://github.com/masakhane-io/masakhane/blob/master/MT4LRL.md low resource, african NMT
- https://glosbe.com/ab/ru/ multilingual dictionary api
- https://babelnet.org/ multilingual semantic network
- https://iconictranslation.com/2020/02/sequence-to-sequence-pre-training-for-neural-mt/
- Research for paraphrasing in NMT:
  https://www.aclweb.org/anthology/W17-5703.pdf
  https://iconictranslation.com/2020/02/issue-69-using-paraphrases-in-multilingual-neural-mt/
