import os
from typing import Dict, Any, List
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

class SchemaExtractor:
    """Auto-extracts PostgreSQL schema metadata and categorical samples using SQLAlchemy introspection."""

    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ecommerce")
        self.engine: Engine = create_engine(self.db_url)

    def _get_categorical_samples(self, table_name: str, column_name: str, limit: int = 5) -> List[Any]:
        """Fetches distinct non-null sample values for text/string columns to guide LLM value filtering."""
        query = text(f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL LIMIT :limit')
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                return [row[0] for row in result.fetchall()]
        except Exception:
            return []

    def extract_schema(self) -> Dict[str, Any]:
        """Extracts tables, columns, constraints, foreign keys, and sample values into a structured dict."""
        inspector = inspect(self.engine)
        schema_data = {}

        for table_name in inspector.get_table_names():
            pk_constraint = inspector.get_pk_constraint(table_name)
            pks = set(pk_constraint.get('constrained_columns', []))
            
            fks = inspector.get_foreign_keys(table_name)
            fk_map = {}
            for fk in fks:
                for c_col, r_col in zip(fk['constrained_columns'], fk['referred_columns']):
                    fk_map[c_col] = f"{fk['referred_table']}.{r_col}"

            columns_info = []
            for col in inspector.get_columns(table_name):
                col_name = col['name']
                col_type = str(col['type'])
                is_pk = col_name in pks
                fk_target = fk_map.get(col_name)

                col_meta = {
                    "name": col_name,
                    "type": col_type,
                    "primary_key": is_pk,
                    "foreign_key": fk_target,
                    "sample_values": []
                }

                # Extract sample values for string/text columns to help the LLM match exact categories
                if any(t in col_type.lower() for t in ["varchar", "text", "char", "string", "nvarchar"]):
                    col_meta["sample_values"] = self._get_categorical_samples(table_name, col_name)

                columns_info.append(col_meta)

            schema_data[table_name] = columns_info

        return schema_data

    def get_formatted_schema(self) -> str:
        """Renders the extracted schema dictionary into a clean text block for LLM prompt context."""
        schema_dict = self.extract_schema()
        output_lines = []

        for table_name, columns in schema_dict.items():
            output_lines.append(f"Table: {table_name}")
            for col in columns:
                details = [f"type: {col['type']}"]
                if col['primary_key']:
                    details.append("PRIMARY KEY")
                if col['foreign_key']:
                    details.append(f"FK -> {col['foreign_key']}")
                if col['sample_values']:
                    samples_formatted = ", ".join([f"'{v}'" for v in col['sample_values']])
                    details.append(f"samples: [{samples_formatted}]")

                output_lines.append(f"  - {col['name']} ({', '.join(details)})")
            output_lines.append("")

        return "\n".join(output_lines).strip()

if __name__ == "__main__":
    # Quick visual test
    extractor = SchemaExtractor()
    print(extractor.get_formatted_schema())