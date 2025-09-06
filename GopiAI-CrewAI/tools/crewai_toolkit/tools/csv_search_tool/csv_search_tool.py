from typing import Optional, Type

from embedchain.models.data_type import DataType
from pydantic import BaseModel, Field

# txtai agent module не доступен в текущей версии
try:
    from txtai.agent.tool.embeddings import EmbeddingsTool
except ImportError:
    # Fallback с базовой реализацией поиска
    import pandas as pd
    class EmbeddingsTool:
        def __init__(self, **kwargs):
            self.data = None
        def add(self, csv_file, data_type=None):
            try:
                self.data = pd.read_csv(csv_file)
            except Exception as e:
                self.data = None
                print(f"Error loading CSV: {e}")
        def _run(self, query=None, **kwargs):
            if self.data is None:
                return "No CSV data loaded"
            # Простой поиск по всем текстовым колонкам
            result_rows = []
            for idx, row in self.data.iterrows():
                for col in self.data.columns:
                    if str(row[col]).lower().find(query.lower()) != -1:
                        result_rows.append(row.to_dict())
                        break
            if result_rows:
                return f"Found {len(result_rows)} results:\n" + str(result_rows[:3])
            return f"No results found for '{query}'"


class FixedCSVSearchToolSchema(BaseModel):
    """Input for CSVSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the CSV's content",
    )


class CSVSearchToolSchema(FixedCSVSearchToolSchema):
    """Input for CSVSearchTool."""

    csv: str = Field(..., description="Mandatory csv path you want to search")


class CSVSearchTool(EmbeddingsTool):
    name: str = "Search a CSV's content"
    description: str = (
        "A tool that can be used to semantic search a query from a CSV's content."
    )
    args_schema: Type[BaseModel] = CSVSearchToolSchema

    def __init__(self, csv: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if csv is not None:
            self.add(csv)
            self.description = f"A tool that can be used to semantic search a query the {csv} CSV's content."
            self.args_schema = FixedCSVSearchToolSchema
            self._generate_description()

    def add(self, csv: str) -> None:
        super().add(csv, data_type=DataType.CSV)

    def _run(
        self,
        search_query: str,
        csv: Optional[str] = None,
    ) -> str:
        if csv is not None:
            self.add(csv)
        return super()._run(query=search_query)
