"""Utilities module for playing with geographical data"""

from typing import Sequence
import geopandas as gpd


def filter_by_states(
    geodataframe: gpd.GeoDataFrame, state_names: Sequence[str] | str
) -> gpd.GeoDataFrame:
    """
    Filters the urban areas that intersect with the specified states.

    Parameters
    geodataframe (GeoDataFrame): GeoDataFrame containing urban areas.
    state_names (list): List of state names to filter urban areas by, or a geographical region

    Returns:
    GeoDataFrame: Filtered GeoDataFrame with urban areas intersecting the specified states.
    """
    if isinstance(state_names, str):
        state_names = [state_names]

    states_gdf: gpd.GeoDataFrame = gpd.read_file(
        "shapefiles/tl_2023_us_state/tl_2023_us_state.shp"
    )

    # Filter the states GeoDataFrame to include only the specified states
    selected_states_gdf = states_gdf[states_gdf["STUSPS"].isin(state_names)]

    # Ensure both GeoDataFrames use the same coordinate reference system (CRS)
    geodataframe = geodataframe.to_crs(selected_states_gdf.crs)

    # Perform spatial join to find urban areas that intersect with the selected states
    filtered_urban_areas_gdf = gpd.sjoin(
        geodataframe, selected_states_gdf, how="inner", predicate="intersects"
    )

    # Drop the additional state columns added during the spatial join
    filtered_urban_areas_gdf = filtered_urban_areas_gdf.drop(columns=["index_right"])

    return filtered_urban_areas_gdf
