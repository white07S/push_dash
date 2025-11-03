"""CSV ingestion utilities for loading data into SQLite database."""
import csv
import json
import os
import logging
from typing import Dict, List, Any, Optional, Generator, Tuple
from datetime import datetime
import pandas as pd

from db import get_db

logger = logging.getLogger(__name__)

class CSVIngester:
    """Handle CSV data ingestion into SQLite database."""

    def __init__(self, csv_dir: str = "csv_data"):
        """Initialize CSV ingester."""
        self.csv_dir = csv_dir
        self.db = get_db()
        self.dataset_configs = {
            'controls': {
                'filename': 'controls.csv',
                'table': 'controls_raw',
                'key_field': 'control_id',
                'required_fields': ['control_id', 'description']
            },
            'external_loss': {
                'filename': 'external_losses.csv',
                'table': 'external_loss_raw',
                'key_field': 'ext_loss_id',
                'required_fields': ['ext_loss_id', 'description']
            },
            'internal_loss': {
                'filename': 'internal_losses.csv',
                'table': 'internal_loss_raw',
                'key_field': 'loss_id',
                'required_fields': ['loss_id', 'description']
            },
            'issues': {
                'filename': 'issues.csv',
                'table': 'issues_raw',
                'key_field': 'issue_id',
                'required_fields': ['issue_id', 'description']
            }
        }

    def normalize_taxonomy(self, taxonomy_str: Optional[str]) -> str:
        """Normalize NFR taxonomy string."""
        if not taxonomy_str:
            return ''

        # Split by pipe, trim whitespace, normalize case
        tokens = [token.strip().title() for token in taxonomy_str.split('|') if token.strip()]
        return '|'.join(tokens)

    def validate_row(self, row: Dict[str, Any], config: Dict) -> Tuple[bool, str]:
        """Validate a CSV row."""
        # Check required fields
        for field in config['required_fields']:
            if field not in row or not row[field]:
                return False, f"Missing required field: {field}"

        # Check for duplicate ID (this would be handled by DB constraint as well)
        key_field = config['key_field']
        key_value = row[key_field]

        if not key_value:
            return False, f"Empty {key_field}"

        return True, ""

    def stream_csv(self, filepath: str) -> Generator[Dict[str, Any], None, None]:
        """Stream CSV file row by row."""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Clean up field names (remove BOM, whitespace)
                    clean_row = {k.strip(): v.strip() if v else '' for k, v in row.items()}
                    yield clean_row
        except Exception as e:
            logger.error(f"Error reading CSV file {filepath}: {e}")
            raise

    def process_batch(self, rows: List[Dict[str, Any]], config: Dict) -> Tuple[int, int, List[str]]:
        """Process a batch of rows for insertion."""
        table = config['table']
        key_field = config['key_field']
        successful = 0
        failed = 0
        errors = []

        # Prepare batch data
        batch_data = []
        taxonomy_data = []

        for row in rows:
            is_valid, error_msg = self.validate_row(row, config)
            if not is_valid:
                failed += 1
                errors.append(f"{row.get(key_field, 'unknown')}: {error_msg}")
                continue

            key_value = row[key_field]
            description = row.get('description', '')
            nfr_taxonomy = self.normalize_taxonomy(row.get('nfr_taxonomy', ''))

            # Store entire row as JSON for raw_data column
            raw_data = json.dumps(row)

            batch_data.append((
                key_value,
                description,
                nfr_taxonomy,
                raw_data,
                datetime.utcnow().isoformat() + 'Z'
            ))

            # Prepare taxonomy mapping data
            if nfr_taxonomy:
                for token in nfr_taxonomy.split('|'):
                    if token:
                        taxonomy_data.append((key_value, token))

        # Insert batch into database
        if batch_data:
            try:
                # Use INSERT OR IGNORE to skip duplicates
                insert_query = f'''
                    INSERT OR IGNORE INTO {table}
                    ({key_field}, description, nfr_taxonomy, raw_data, created_at)
                    VALUES (?, ?, ?, ?, ?)
                '''
                self.db.executemany(insert_query, batch_data)

                # Insert taxonomy mappings
                if taxonomy_data:
                    dataset_name = table.replace('_raw', '')
                    taxonomy_query = f'''
                        INSERT OR IGNORE INTO {dataset_name}_taxonomy_map
                        ({key_field}, taxonomy_token)
                        VALUES (?, ?)
                    '''
                    self.db.executemany(taxonomy_query, taxonomy_data)

                # APSW is in autocommit mode by default, no commit needed
                successful = len(batch_data)
            except Exception as e:
                logger.error(f"Error inserting batch: {e}")
                failed += len(batch_data)
                errors.append(f"Batch insert error: {str(e)}")

        return successful, failed, errors

    def ingest_dataset(self, dataset_name: str, batch_size: int = 1000) -> Dict[str, Any]:
        """Ingest a single dataset from CSV."""
        if dataset_name not in self.dataset_configs:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        config = self.dataset_configs[dataset_name]
        filepath = os.path.join(self.csv_dir, config['filename'])

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        logger.info(f"Starting ingestion of {dataset_name} from {filepath}")

        total_successful = 0
        total_failed = 0
        all_errors = []
        batch = []

        # Process CSV in batches
        for row in self.stream_csv(filepath):
            batch.append(row)

            if len(batch) >= batch_size:
                successful, failed, errors = self.process_batch(batch, config)
                total_successful += successful
                total_failed += failed
                all_errors.extend(errors)
                batch = []

        # Process remaining batch
        if batch:
            successful, failed, errors = self.process_batch(batch, config)
            total_successful += successful
            total_failed += failed
            all_errors.extend(errors)

        result = {
            'dataset': dataset_name,
            'successful': total_successful,
            'failed': total_failed,
            'total': total_successful + total_failed,
            'errors': all_errors[:100]  # Limit errors to first 100
        }

        logger.info(f"Completed ingestion of {dataset_name}: {result}")
        return result

    def ingest_all(self, batch_size: int = 1000) -> Dict[str, Any]:
        """Ingest all datasets from CSV files."""
        results = {}

        for dataset_name in self.dataset_configs:
            try:
                result = self.ingest_dataset(dataset_name, batch_size)
                results[dataset_name] = result
            except Exception as e:
                logger.error(f"Error ingesting {dataset_name}: {e}")
                results[dataset_name] = {
                    'dataset': dataset_name,
                    'error': str(e),
                    'successful': 0,
                    'failed': 0
                }

        return results

    def get_ingestion_stats(self) -> Dict[str, int]:
        """Get current ingestion statistics."""
        stats = {}

        for dataset_name, config in self.dataset_configs.items():
            table = config['table']
            query = f"SELECT COUNT(*) FROM {table}"
            result = self.db.fetchone(query)
            stats[dataset_name] = result[0] if result else 0

        return stats