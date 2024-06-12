from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
from sklearn.linear_model import LinearRegression
import os
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint


class CustomPipeline(FunctionCallingBlueprint):
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

        def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
            """
            Clean and preprocess the data.

            :param data: The data to clean and preprocess.
            :return: A Pandas DataFrame containing the cleaned and preprocessed data.
            """
            data = data.fillna(data.mean())
            data = data[data > 0]
            data['date'] = pd.to_datetime(data['date'])
            data = (data - data.min()) / (data.max() - data.min())
            return data

        def transform_data(self, data: pd.DataFrame):
            """
            Transform the data.

            :param data: The data to transform.
            :return: Aggregated, filtered, summarized, and pivoted data.
            """
            data_agg = data.groupby('category').mean()
            data_filtered = data[data['value'] > 10]
            data_summary = data.describe()
            data_pivot = data.pivot_table(index='category', columns='year', values='value')
            return data_agg, data_filtered, data_summary, data_pivot

        def visualize_data(self, data: pd.DataFrame):
            """
            Visualize the data.

            :param data: The data to visualize.
            """
            sns.barplot(x='category', y='value', data=data)
            plt.show()

            sns.lineplot(x='date', y='value', data=data)
            plt.show()

            sns.scatterplot(x='x', y='y', data=data)
            plt.show()

            sns.heatmap(data.corr(), annot=True)
            plt.show()

        def analyze_data(self, data: pd.DataFrame):
            """
            Analyze the data.

            :param data: The data to analyze.
            """
            t_stat, p_val = ttest_ind(data['value1'], data['value2'])
            print(f"T-statistic: {t_stat}, p-value: {p_val}")

            model = LinearRegression()
            model.fit(data[['x']], data['y'])
            print(model.coef_, model.intercept_)

    def __init__(self):
        super().__init__()
        self.name = "Custom Data Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
            },
        )
        self.tools = self.Tools(self)

    async def on_startup(self):
        print("Custom Data Pipeline started")

    async def on_shutdown(self):
        print("Custom Data Pipeline stopped")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print("Processing data pipeline")
        # Example usage: reading, cleaning, transforming, and visualizing data
        file_path = "data.csv"
        file_format = "csv"
        data = self.tools.read_data(file_path, file_format)
        clean_data = self.tools.clean_data(data)
        data_agg, data_filtered, data_summary, data_pivot = self.tools.transform_data(clean_data)
        self.tools.visualize_data(clean_data)
        self.tools.analyze_data(clean_data)
        return f"Data processing and analysis completed."


if __name__ == '__main__':
    import asyncio
    pipeline = CustomPipeline()
    asyncio.run(pipeline.on_startup())
    asyncio.run(pipeline.on_shutdown())
