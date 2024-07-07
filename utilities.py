"""Utilities module for playing with geographical data"""

from typing import List, Sequence, Set
import geopandas as gpd


def get_state_abbreviations_from_region(region_names: str | List[str]) -> List[str]:
    """
    Get state name abbreviations given a region name

    Parameter
    region_name (str): Region name.
    """

    if isinstance(region_names, str):
        region_names = [region_names]

    regions: dict[str, dict[str, list[str]]] = {
        "Northeast": {
            "New England": ["CT", "ME", "MA", "NH", "RI", "VT"],
            "Mid-Atlantic": ["NJ", "NY", "PA"],
        },
        "Midwest": {
            "East North Central": ["IL", "IN", "MI", "OH", "WI"],
            "West North Central": ["IA", "KS", "MN", "MO", "NE", "ND", "SD"],
            "Upper Midwest": ["MN", "WI", "IA", "ND", "SD"],
        },
        "South": {
            "South Atlantic": ["DE", "FL", "GA", "MD", "NC", "SC", "VA", "DC", "WV"],
            "East South Central": ["AL", "KY", "MS", "TN"],
            "West South Central": ["AR", "LA", "OK", "TX"],
            "Deep South": ["AL", "GA", "LA", "MS", "SC"],
        },
        "West": {
            "Mountain": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"],
            "Pacific": ["AK", "CA", "HI", "OR", "WA"],
            "Pacific Northwest": ["OR", "WA", "ID"],
            "Southwest": ["AZ", "NM", "OK", "TX"],
        },
    }

    result: Set[str] = set()

    for region_name in region_names:
        if region_name in regions:
            result = result.union(
                [
                    abbr
                    for subregion in regions[region_name]
                    for abbr in regions[region_name][subregion]
                ]
            )

        for main_region in regions.values():
            if region_name in main_region:
                result = result.union(main_region[region_name])

    return list(result)


def filter_by_states(
    geodataframe: gpd.GeoDataFrame, state_names: Sequence[str] | str
) -> gpd.GeoDataFrame:
    """
    Filters the urban areas that intersect with the specified states.

    Parameters
    geodataframe (GeoDataFrame): GeoDataFrame containing urban areas.
    state_names (list): List of state names to filter urban areas by, or a geographical region.

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
