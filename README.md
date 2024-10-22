# Caucasus focused Data Pipeline for Natural Language Processing(NLP)

How to use sparse checkout to exclude `data/` due to it's huge size, and selectively download folders later:
1. Initial clone: run `bash repo.sh clone https://github.com/Caucasus-Rosetta/Lingua-Corpus.git <target_dir>`
The repository is cloned to `<target_dir>`, excluding `data/`.
2. Selective download: To download a specific folder, run `bash repo.sh download <path/to/folder>`. i.e `data/raw/ab`
3. Cleanup: Run `bash repo.sh cleanup <path/to/folder>` to remove the folder.

To add a new folder to `data/`, you need to use the `--sparse`, i.e `git add -A --sparse`

## Lingua-Corpus Structure

```
Lingua-Corpus/
├── src/
│   ├── extraction/
│   ├── processing/
│   └── utils/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── stats/
├── README.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

1. `src/`: This directory contains all the source code for your project.
   - `extraction/`: Code for extracting text from PDFs and HTML files.
   - `processing/`: Scripts for cleaning and preprocessing the extracted text.
   - `utils/`: Utility functions used across different parts of the project.

   This separation allows for better organization and modularity of your code.

2. `data/`: This directory stores all your data files.
   - `raw/`: Original, unmodified PDF and HTML files.
   - `interim/`: Partially processed data, useful for debugging or checkpointing.
   - `processed/`: Fully processed, analysis-ready data.
   - `stats/`: Statistics of the processed data.
   
   This structure clearly separates data at different stages of your pipeline.

3. `README.md`: Provides an overview of the project, setup instructions, and other essential information.

4. `CODE_OF_CONDUCT.md`: Provides an overview of code of conduct for the project.

5. `LICENSE`: The license of the code of the project.

This structure follows several best practices:

- Separation of concerns: Code, data, and documentation are kept separate.
- Reproducibility: By including configs and requirements, others can recreate your environment.
- Scalability: As your project grows, this structure can accommodate more modules and data.
- Collaboration-friendly: Clear organization makes it easier for team members to navigate and contribute.

This structure is particularly well-suited for data pipeline projects because it accommodates the different stages of data processing (raw, interim, processed) and separates the code for each stage of the pipeline (extraction, processing).

## Description

This repository contains a data pipeline that processes text into monolingual and parallel corpora for Natural Language Processing (NLP) applications. 

| language | monolingual corpus | parallel corpus |
|----------|:----------:|:----------:|
| Abkhaz (ab) |  1,470,480 | 205,665 |
| West Circassian (ady) | - | - |
| East Circassian (kbd) | - | - |

The corpuses are located at `data/processed/<LANG_CODE>`

## Data Pipeline

The data pipeline consists of two stages, extraction and processing.

### Extraction

The data acquisition process involves extracting information from various sources, employing diverse techniques to ensure comprehensive coverage. 

- Dictionary parsing using the `parse_dictionary.py` script.
- For web content, a web scraping methodology is implemented, leveraging Scrapy spiders to simultaneously extract data from parallel web pages.
- Additionally, [`hunalign`](https://github.com/danielvarga/hunalign) is employed to perform heuristic text alignment across pages, optimizing the alignment process.
- The content from ebooks is directly extracted from PDF documents.

Extraction acquires data in it's raw form, then semi-processes and moves it to interim

The folders that matter in the extraction stage:
```
├── src/
│   └── extraction/    # code acquires data in it's raw form,
│                      # then semi-processes and moves it to interim
└── data/
    ├── raw/           # raw data
    └── interim/       # semi-processed data
```

### Processing

Data Refinement:
- Implement various heuristics to remove noise, identify outliers and filter interim data.
- Apply random sampling for inferential statistics and incorporate feedback from human evaluators.
- Repeat process iteratively until target accuracy of 95% (Error types considered: syntactical, grammatical, and semantic).

The folders that matter in the processing stage:
```
├── src/
│   └── processing/    # code for processing, cleaning and transforming
│                      # interim data into processed data along with analysis
└── data/
    ├── processed/     # processed data
    └── stats/         # statistics of the processed data
```
    
## Methodology (proposed)

I propose utilizing Bayesian with multifidelity Optimization methodology. The black box function involves the process of extraction, transformation, and processing to prepare the data for training neural network models, then validate accuracy by human evaluators (high fidelity). Inputs are derived from heuristics. The Gaussian processes and acquisition score policy are done manually, the desired global optimum is 95% accuracy.

I propose the following approach:

- Implement Gaussian processes and acquisition policy.
- Incorporate prompt engineering techniques alongside heuristics as inputs. 
- Utilize and balance between prompt engineering to evaluate output accuracy (low fidelity), and employ human evaluators for a thorough accuracy (high fidelity).

![bayesopt](https://github.com/user-attachments/assets/a95ce254-8a57-49cc-b302-f3e112581486)

Reference image from Bayesian Optimization in Action by Quan Nguyen
