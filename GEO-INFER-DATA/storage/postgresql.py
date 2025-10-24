"""
PostgreSQL/PostGIS storage implementation for GEO-INFER-DATA.

This module provides comprehensive PostgreSQL and PostGIS storage capabilities
including table creation, indexing, querying, and performance optimization.
"""

import logging
from typing import Dict, List, Optional, Union, Any
import asyncio
from datetime import datetime

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from ..models.schemas import DatasetMetadata, SpatialExtent, TemporalExtent, DataLineage


logger = logging.getLogger(__name__)


class PostgreSQLStorage:
    """
    PostgreSQL/PostGIS storage implementation.

    This class provides comprehensive PostgreSQL storage with PostGIS
    spatial capabilities including automatic table creation, indexing,
    and query optimization.

    Args:
        connection_string: PostgreSQL connection string
        schema: Database schema name
        enable_postgis: Whether to enable PostGIS features

    Examples:
        >>> storage = PostgreSQLStorage(
        ...     connection_string='postgresql://user:pass@localhost/geodata',
        ...     schema='public',
        ...     enable_postgis=True
        ... )
        >>>
        >>> # Create table for sensor data
        >>> await storage.create_table(table_schema, 'sensor_data')
        >>>
        >>> # Insert geospatial data
        >>> await storage.insert_geodataframe(gdf, 'sensor_data', metadata)
        >>>
        >>> # Query with spatial filter
        >>> results = await storage.query_spatial('sensor_data', bbox=[-122.5, 37.7, -122.3, 37.9])
    """

    def __init__(
        self,
        connection_string: str,
        schema: str = 'public',
        enable_postgis: bool = True
    ):
        self.connection_string = connection_string
        self.schema = schema
        self.enable_postgis = enable_postgis

        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None

        self._initialize_connection()

        logger.info(f"Initialized PostgreSQLStorage with schema={schema}")

    def _initialize_connection(self):
        """Initialize PostgreSQL connection."""
        try:
            # Create synchronous engine
            self.engine = create_engine(
                self.connection_string,
                echo=False,
                pool_pre_ping=True
            )

            # Create session factory
            from sqlalchemy.orm import sessionmaker
            self.SessionLocal = sessionmaker(bind=self.engine)

            # Create async engine
            async_url = self.connection_string.replace('postgresql://', 'postgresql+asyncpg://')
            self.async_engine = create_async_engine(async_url)

            from sqlalchemy.ext.asyncio import AsyncSession
            self.AsyncSessionLocal = sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Create PostGIS extension if enabled
            if self.enable_postgis:
                self._create_postgis_extension()

            logger.info("PostgreSQL connection established")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection: {e}")
            raise

    def _create_postgis_extension(self):
        """Create PostGIS extension if not exists."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))
                conn.commit()
            logger.info("PostGIS extensions created")
        except Exception as e:
            logger.warning(f"Failed to create PostGIS extensions: {e}")

    async def create_table(
        self,
        table_schema: Dict[str, Any],
        table_name: str,
        if_exists: str = 'replace'
    ) -> bool:
        """
        Create database table with schema.

        Args:
            table_schema: Table schema definition
            table_name: Table name
            if_exists: Behavior if table exists ('replace', 'append', 'fail')

        Returns:
            True if successful
        """
        logger.info(f"Creating table {table_name} in schema {self.schema}")

        try:
            # Build CREATE TABLE statement
            columns = []
            for col_name, col_def in table_schema.items():
                col_type = self._map_pandas_to_sql_type(col_def.get('type', 'object'))
                nullable = col_def.get('nullable', True)

                if col_name == 'geometry' or col_name == 'geom':
                    col_sql = f"{col_name} GEOMETRY({col_def.get('geometry_type', 'POINT')}, {col_def.get('srid', 4326)})"
                else:
                    col_sql = f"{col_name} {col_type}"
                    if not nullable:
                        col_sql += " NOT NULL"

                columns.append(col_sql)

            # Add metadata columns
            metadata_columns = [
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "data_source VARCHAR(255)",
                "quality_score FLOAT",
                "metadata JSONB"
            ]

            all_columns = columns + metadata_columns
            columns_sql = ",\n    ".join(all_columns)

            # Build complete CREATE TABLE statement
            if if_exists == 'replace':
                drop_statement = f"DROP TABLE IF EXISTS {self.schema}.{table_name};"
                create_statement = f"""
                CREATE TABLE {self.schema}.{table_name} (
                    {columns_sql}
                );
                """
            else:
                create_statement = f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.{table_name} (
                    {columns_sql}
                );
                """

            # Execute table creation
            async with self.AsyncSessionLocal() as session:
                if if_exists == 'replace':
                    await session.execute(text(drop_statement))
                await session.execute(text(create_statement))
                await session.commit()

            # Create spatial indexes if geometry columns exist
            await self._create_spatial_indexes(table_name, table_schema)

            logger.info(f"Table {table_name} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise

    def _map_pandas_to_sql_type(self, pandas_type: str) -> str:
        """Map pandas data types to SQL types."""
        type_mapping = {
            'object': 'VARCHAR(255)',
            'string': 'VARCHAR(255)',
            'int64': 'BIGINT',
            'int32': 'INTEGER',
            'int16': 'SMALLINT',
            'float64': 'DOUBLE PRECISION',
            'float32': 'REAL',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TIMESTAMP',
            'datetime64[ns, UTC]': 'TIMESTAMP WITH TIME ZONE'
        }

        return type_mapping.get(pandas_type, 'VARCHAR(255)')

    async def _create_spatial_indexes(self, table_name: str, table_schema: Dict[str, Any]):
        """Create spatial indexes for geometry columns."""
        geometry_columns = [col for col in table_schema.keys()
                          if col in ['geometry', 'geom', 'the_geom']]

        for geom_col in geometry_columns:
            index_name = f"idx_{table_name}_{geom_col}"

            try:
                async with self.AsyncSessionLocal() as session:
                    await session.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS {index_name}
                        ON {self.schema}.{table_name}
                        USING GIST ({geom_col});
                    """))
                    await session.commit()

                logger.info(f"Created spatial index {index_name}")

            except Exception as e:
                logger.warning(f"Failed to create spatial index {index_name}: {e}")

    async def insert_geodataframe(
        self,
        gdf: gpd.GeoDataFrame,
        table_name: str,
        metadata: Optional[DatasetMetadata] = None,
        batch_size: int = 1000
    ) -> int:
        """
        Insert GeoDataFrame into PostgreSQL table.

        Args:
            gdf: GeoDataFrame to insert
            table_name: Target table name
            metadata: Dataset metadata
            batch_size: Batch size for insertion

        Returns:
            Number of rows inserted
        """
        logger.info(f"Inserting {len(gdf)} records into {table_name}")

        try:
            # Prepare data for insertion
            insert_data = []

            for idx, row in gdf.iterrows():
                record = row.to_dict()

                # Handle geometry column
                if 'geometry' in record:
                    geom = record['geometry']
                    if geom and hasattr(geom, 'wkt'):
                        record['geom'] = geom.wkt
                    del record['geometry']

                # Add metadata
                record.update({
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow(),
                    'data_source': metadata.title if metadata else 'unknown',
                    'quality_score': getattr(metadata, 'quality_score', None) if metadata else None,
                    'metadata': metadata.dict() if metadata else {}
                })

                insert_data.append(record)

            # Insert in batches
            total_inserted = 0

            for i in range(0, len(insert_data), batch_size):
                batch = insert_data[i:i + batch_size]

                async with self.AsyncSessionLocal() as session:
                    # Build INSERT statement
                    columns = list(batch[0].keys())
                    columns_sql = ', '.join(columns)
                    placeholders = ', '.join([f':{col}' for col in columns])
                    values_sql = ', '.join([f'({placeholders})' for _ in batch])

                    insert_sql = f"""
                    INSERT INTO {self.schema}.{table_name} ({columns_sql})
                    VALUES {values_sql}
                    """

                    await session.execute(text(insert_sql), batch)
                    await session.commit()

                total_inserted += len(batch)
                logger.debug(f"Inserted batch {i//batch_size + 1}, total: {total_inserted}")

            logger.info(f"Successfully inserted {total_inserted} records")
            return total_inserted

        except Exception as e:
            logger.error(f"Failed to insert GeoDataFrame: {e}")
            raise

    async def query_spatial(
        self,
        table_name: str,
        bbox: List[float],
        columns: Optional[List[str]] = None,
        temporal_filter: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        **kwargs
    ) -> gpd.GeoDataFrame:
        """
        Query table with spatial and temporal filters.

        Args:
            table_name: Table name to query
            bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
            columns: Columns to select
            temporal_filter: Temporal filtering options
            limit: Maximum number of records
            **kwargs: Additional query parameters

        Returns:
            Query results as GeoDataFrame
        """
        logger.info(f"Querying {table_name} with spatial filter")

        # Build query
        select_columns = columns or ['*']
        columns_sql = ', '.join(select_columns)

        # Spatial filter
        min_lon, min_lat, max_lon, max_lat = bbox
        spatial_condition = """
        ST_Intersects(
            geom,
            ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
        )
        """

        # Temporal filter
        temporal_conditions = []
        if temporal_filter:
            if 'start_date' in temporal_filter:
                temporal_conditions.append("created_at >= :start_date")
            if 'end_date' in temporal_filter:
                temporal_conditions.append("created_at <= :end_date")

        # Combine conditions
        conditions = [spatial_condition]
        conditions.extend(temporal_conditions)
        where_clause = " WHERE " + " AND ".join(conditions)

        # Add limit
        limit_clause = f" LIMIT {limit}" if limit else ""

        query = f"""
        SELECT {columns_sql}
        FROM {self.schema}.{table_name}
        {where_clause}
        {limit_clause}
        """

        try:
            # Execute query
            params = {
                'min_lon': min_lon,
                'min_lat': min_lat,
                'max_lon': max_lon,
                'max_lat': max_lat
            }

            if temporal_filter:
                if 'start_date' in temporal_filter:
                    params['start_date'] = temporal_filter['start_date']
                if 'end_date' in temporal_filter:
                    params['end_date'] = temporal_filter['end_date']

            async with self.AsyncSessionLocal() as session:
                result = await session.execute(text(query), params)
                rows = result.fetchall()

                if not rows:
                    return gpd.GeoDataFrame()

                # Convert to DataFrame
                df = pd.DataFrame(rows, columns=result.keys() if hasattr(result, 'keys') else None)

                # Convert to GeoDataFrame
                if 'geom' in df.columns:
                    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geom']), crs="EPSG:4326")
                    gdf.drop('geom', axis=1, inplace=True)
                    return gdf
                else:
                    return gpd.GeoDataFrame(df)

        except Exception as e:
            logger.error(f"Spatial query failed: {e}")
            raise

    async def create_table_from_geodataframe(
        self,
        gdf: gpd.GeoDataFrame,
        table_name: str,
        metadata: Optional[DatasetMetadata] = None,
        if_exists: str = 'replace'
    ) -> bool:
        """
        Create table from GeoDataFrame structure.

        Args:
            gdf: Source GeoDataFrame
            table_name: Table name
            metadata: Dataset metadata
            if_exists: Behavior if table exists

        Returns:
            True if successful
        """
        logger.info(f"Creating table from GeoDataFrame: {table_name}")

        # Analyze GeoDataFrame structure
        table_schema = {}

        for col_name, dtype in gdf.dtypes.items():
            if col_name == 'geometry':
                # Geometry column
                table_schema[col_name] = {
                    'type': 'geometry',
                    'geometry_type': gdf.geom_type.iloc[0] if hasattr(gdf, 'geom_type') else 'GEOMETRY',
                    'srid': gdf.crs.to_epsg() if gdf.crs else 4326,
                    'nullable': True
                }
            else:
                # Regular column
                table_schema[col_name] = {
                    'type': str(dtype),
                    'nullable': gdf[col_name].isnull().any()
                }

        # Create table
        await self.create_table(table_schema, table_name, if_exists)

        # Insert data
        await self.insert_geodataframe(gdf, table_name, metadata)

        logger.info(f"Table {table_name} created and populated successfully")
        return True

    async def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """
        Get table statistics and metadata.

        Args:
            table_name: Table name

        Returns:
            Table statistics
        """
        try:
            async with self.AsyncSessionLocal() as session:
                # Get row count
                count_result = await session.execute(text(f"""
                    SELECT COUNT(*) as row_count
                    FROM {self.schema}.{table_name}
                """))
                row_count = count_result.scalar()

                # Get column information
                columns_result = await session.execute(text(f"""
                    SELECT
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns
                    WHERE table_schema = :schema
                    AND table_name = :table_name
                    ORDER BY ordinal_position
                """), {'schema': self.schema, 'table_name': table_name})

                columns = columns_result.fetchall()

                # Get spatial information
                spatial_info = {}
                if self.enable_postgis:
                    try:
                        geom_result = await session.execute(text(f"""
                            SELECT
                                f_geometry_column as geom_column,
                                srid,
                                type as geometry_type
                            FROM geometry_columns
                            WHERE f_table_schema = :schema
                            AND f_table_name = :table_name
                        """), {'schema': self.schema, 'table_name': table_name})

                        spatial_info = geom_result.fetchone()
                    except Exception:
                        pass  # No spatial columns

                # Get table size
                size_result = await session.execute(text(f"""
                    SELECT
                        pg_total_relation_size('{self.schema}.{table_name}') as total_size,
                        pg_relation_size('{self.schema}.{table_name}') as data_size
                """))

                size_info = size_result.fetchone()

                return {
                    'table_name': table_name,
                    'schema': self.schema,
                    'row_count': row_count,
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1],
                            'nullable': col[2] == 'YES',
                            'default': col[3]
                        } for col in columns
                    ],
                    'spatial_info': {
                        'geometry_column': spatial_info[0] if spatial_info else None,
                        'srid': spatial_info[1] if spatial_info else None,
                        'geometry_type': spatial_info[2] if spatial_info else None
                    } if spatial_info else {},
                    'size_info': {
                        'total_size_bytes': size_info[0] if size_info else 0,
                        'data_size_bytes': size_info[1] if size_info else 0
                    }
                }

        except Exception as e:
            logger.error(f"Failed to get table statistics: {e}")
            return {'error': str(e)}

    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """
        Optimize table performance.

        Args:
            table_name: Table name to optimize

        Returns:
            Optimization results
        """
        logger.info(f"Optimizing table: {table_name}")

        optimizations = []

        try:
            async with self.AsyncSessionLocal() as session:
                # Analyze table
                await session.execute(text(f"ANALYZE {self.schema}.{table_name}"))
                optimizations.append("Table analyzed")

                # Vacuum table
                await session.execute(text(f"VACUUM {self.schema}.{table_name}"))
                optimizations.append("Table vacuumed")

                # Reindex if needed
                await session.execute(text(f"REINDEX TABLE {self.schema}.{table_name}"))
                optimizations.append("Table reindexed")

                await session.commit()

            logger.info(f"Table optimization completed: {len(optimizations)} optimizations applied")
            return {
                'table_name': table_name,
                'optimizations_applied': optimizations,
                'timestamp': datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Table optimization failed: {e}")
            return {
                'table_name': table_name,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }

    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("PostgreSQL connections closed")
