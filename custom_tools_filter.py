from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import pandas as pd
import spacy
from textblob import TextBlob
import os
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

# Load NLP models
nlp = spacy.load("en_core_web_sm")


class NLPipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def read_data(self, file_path: str, file_format: str) -> pd.DataFrame:
            """
            Read data from a file and return a Pandas DataFrame.

            :param file_path: The path to the file.
            :param file_format: The format of the file (e.g., 'csv', 'json', 'xml').
            :return: A Pandas DataFrame containing the data.
            """
            if file_format == 'csv':
                data = pd.read_csv(file_path)
            elif file_format == 'json':
                data = pd.read_json(file_path)
            elif file_format == 'xml':
                data = pd.read_xml(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")

            return data

        def clean_text(self, text: str) -> str:
            """
            Clean and preprocess the text data.

            :param text: The text to clean.
            :return: Cleaned text.
            """
            doc = nlp(text)
            tokens = [token.lemma_ for token in doc if not token.is_stop]
            return " ".join(tokens)

        def named_entity_recognition(self, text: str) -> List[str]:
            """
            Perform named entity recognition on the text.

            :param text: The text to analyze.
            :return: A list of named entities.
            """
            doc = nlp(text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            return entities

        def sentiment_analysis(self, text: str) -> str:
            """
            Perform sentiment analysis on the text.

            :param text: The text to analyze.
            :return: Sentiment polarity and subjectivity.
            """
            blob = TextBlob(text)
            return f"Polarity: {blob.sentiment.polarity}, Subjectivity: {blob.sentiment.subjectivity}"

        def summarize_text(self, text: str) -> str:
            """
            Summarize the text.

            :param text: The text to summarize.
            :return: Summarized text.
            """
            doc = nlp(text)
            summary = " ".join([sent.text for sent in doc.sents][:3])  # Simple summarization by taking the first 3 sentences
            return summary

    def __init__(self):
        super().__init__()
        self.name = "NLP Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
            },
        )
        self.tools = self.Tools(self)

    async def on_startup(self):
        print("NLP Pipeline started")

    async def on_shutdown(self):
        print("NLP Pipeline stopped")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print("Processing NLP pipeline")
        
        # Example usage of the NLP tools
        text = user_message
        
        cleaned_text = self.tools.clean_text(text)
        entities = self.tools.named_entity_recognition(cleaned_text)
        sentiment = self.tools.sentiment_analysis(cleaned_text)
        summary = self.tools.summarize_text(cleaned_text)
        
        response = {
            "cleaned_text": cleaned_text,
            "entities": entities,
            "sentiment": sentiment,
            "summary": summary
        }
        
        return response


if __name__ == '__main__':
    import asyncio
    pipeline = NLPipeline()
    asyncio.run(pipeline.on_startup())
    asyncio.run(pipeline.on_shutdown())
