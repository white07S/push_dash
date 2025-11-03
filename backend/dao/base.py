"""Base DAO class for dataset access."""
import json
from typing import Dict, Any, List, Optional, Tuple
from db import get_db
from services.resolver import get_resolver

class BaseDAO:
    """Base Data Access Object for datasets."""

    def __init__(self, dataset_name: str, key_field: str):
        """Initialize base DAO.

        Args:
            dataset_name: Name of the dataset (controls, external_loss, etc.)
            key_field: Primary key field name
        """
        self.dataset_name = dataset_name
        self.key_field = key_field
        self.table_name = f"{dataset_name}_raw"
        self.db = get_db()
        self.resolver = get_resolver()

    def search_by_id(self, id: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Search for items by ID.

        Args:
            id: ID to search for
            limit: Maximum number of results

        Returns:
            List of matching items
        """
        query = f'''
            SELECT {self.key_field}, description, nfr_taxonomy, raw_data
            FROM {self.table_name}
            WHERE {self.key_field} = ?
            LIMIT ?
        '''

        rows = self.db.fetchall(query, (id, limit))
        results = []

        for row in rows:
            # Check if AI taxonomy exists
            ai_taxonomy_table = f"{self.dataset_name}_ai_taxonomy"
            ai_check_query = f"SELECT 1 FROM {ai_taxonomy_table} WHERE {self.key_field} = ?"
            ai_exists = self.db.fetchone(ai_check_query, (row[0],))

            item = {
                'id': row[0],
                'description': row[1],
                'nfr_taxonomy': row[2],
                'ai_taxonomy_present': bool(ai_exists)
            }
            results.append(item)

        return results

    def get_details(self, id: str) -> Optional[Dict[str, Any]]:
        """Get full details for an item including AI results.

        Args:
            id: Item ID

        Returns:
            Full item details or None if not found
        """
        # Get raw data
        query = f'''
            SELECT {self.key_field}, description, nfr_taxonomy, raw_data
            FROM {self.table_name}
            WHERE {self.key_field} = ?
        '''

        row = self.db.fetchone(query, (id,))
        if not row:
            return None

        # Parse raw data
        raw_data = json.loads(row[3]) if row[3] else {}

        # Get all AI results
        ai_results = self.resolver.get_all_results(self.dataset_name, id)

        # Format AI results - remove 'ai_' prefix for model compatibility
        ai_data = {}
        for func_name, result in ai_results.items():
            # Remove 'ai_' prefix if present, but keep special names like 'similar_controls'
            display_name = func_name
            if func_name.startswith('ai_'):
                display_name = func_name[3:]  # Remove 'ai_' prefix

            if result:
                ai_data[display_name] = result['payload']
            else:
                ai_data[display_name] = None

        return {
            'raw': {
                self.key_field: row[0],
                'description': row[1],
                'nfr_taxonomy': row[2],
                'raw_data': raw_data
            },
            'ai': ai_data
        }

    def list_all(self, offset: int = 0, limit: int = 100) -> Tuple[List[Dict[str, Any]], int]:
        """List all items with pagination.

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return

        Returns:
            Tuple of (items, total_count)
        """
        # Get total count
        count_query = f"SELECT COUNT(*) FROM {self.table_name}"
        total = self.db.fetchone(count_query)[0]

        # Get paginated results
        query = f'''
            SELECT {self.key_field}, description, nfr_taxonomy
            FROM {self.table_name}
            LIMIT ? OFFSET ?
        '''

        rows = self.db.fetchall(query, (limit, offset))
        items = []

        for row in rows:
            # Check if AI taxonomy exists
            ai_taxonomy_table = f"{self.dataset_name}_ai_taxonomy"
            ai_check_query = f"SELECT 1 FROM {ai_taxonomy_table} WHERE {self.key_field} = ?"
            ai_exists = self.db.fetchone(ai_check_query, (row[0],))

            item = {
                'id': row[0],
                'description': row[1],
                'nfr_taxonomy': row[2],
                'ai_taxonomy_present': bool(ai_exists)
            }
            items.append(item)

        return items, total

    def search_by_taxonomy(self, taxonomy_token: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search items by taxonomy token.

        Args:
            taxonomy_token: Taxonomy token to search for
            limit: Maximum number of results

        Returns:
            List of matching items
        """
        taxonomy_table = f"{self.dataset_name}_taxonomy_map"
        query = f'''
            SELECT DISTINCT r.{self.key_field}, r.description, r.nfr_taxonomy
            FROM {self.table_name} r
            INNER JOIN {taxonomy_table} t ON r.{self.key_field} = t.{self.key_field}
            WHERE t.taxonomy_token = ?
            LIMIT ?
        '''

        rows = self.db.fetchall(query, (taxonomy_token.title(), limit))
        results = []

        for row in rows:
            # Check if AI taxonomy exists
            ai_taxonomy_table = f"{self.dataset_name}_ai_taxonomy"
            ai_check_query = f"SELECT 1 FROM {ai_taxonomy_table} WHERE {self.key_field} = ?"
            ai_exists = self.db.fetchone(ai_check_query, (row[0],))

            item = {
                'id': row[0],
                'description': row[1],
                'nfr_taxonomy': row[2],
                'ai_taxonomy_present': bool(ai_exists)
            }
            results.append(item)

        return results

    def trigger_ai_function(
        self,
        id: str,
        function_name: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger an AI function for an item.

        Args:
            id: Item ID
            function_name: AI function name
            description: Optional description override
            refresh: Force recompute

        Returns:
            AI function result
        """
        return self.resolver.resolve(
            dataset=self.dataset_name,
            func=function_name,
            id=id,
            description=description,
            refresh=refresh
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics.

        Returns:
            Statistics dictionary
        """
        # Total count
        count_query = f"SELECT COUNT(*) FROM {self.table_name}"
        total = self.db.fetchone(count_query)[0]

        # Count by taxonomy
        taxonomy_query = f'''
            SELECT taxonomy_token, COUNT(DISTINCT {self.key_field}) as count
            FROM {self.dataset_name}_taxonomy_map
            GROUP BY taxonomy_token
            ORDER BY count DESC
            LIMIT 10
        '''
        taxonomy_rows = self.db.fetchall(taxonomy_query)
        top_taxonomies = [{'token': row[0], 'count': row[1]} for row in taxonomy_rows]

        # AI function coverage
        ai_functions = ['ai_taxonomy', 'ai_root_causes', 'ai_enrichment']
        if self.dataset_name == 'controls':
            ai_functions.append('similar_controls')
        else:
            ai_functions.append(f'similar_{self.dataset_name}')

        ai_coverage = {}
        for func in ai_functions:
            table = f"{self.dataset_name}_{func}"
            query = f"SELECT COUNT(*) FROM {table}"
            try:
                count = self.db.fetchone(query)[0]
                ai_coverage[func] = {
                    'computed': count,
                    'percentage': f"{(count / total * 100):.1f}%" if total > 0 else "0%"
                }
            except:
                ai_coverage[func] = {'computed': 0, 'percentage': "0%"}

        return {
            'total_items': total,
            'top_taxonomies': top_taxonomies,
            'ai_coverage': ai_coverage
        }