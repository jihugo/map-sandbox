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
        "northeast": {
            "new england": ["CT", "ME", "MA", "NH", "RI", "VT"],
            "mid-atlantic": ["NJ", "NY", "PA"],
        },
        "midwest": {
            "east north central": ["IL", "IN", "MI", "OH", "WI"],
            "west north central": ["IA", "KS", "MN", "MO", "NE", "ND", "SD"],
            "upper midwest": ["MN", "WI", "IA", "ND", "SD"],
        },
        "South": {
            "south atlantic": ["DE", "FL", "GA", "MD", "NC", "SC", "VA", "DC", "WV"],
            "east south central": ["AL", "KY", "MS", "TN"],
            "west south central": ["AR", "LA", "OK", "TX"],
            "deep south": ["AL", "GA", "LA", "MS", "SC"],
        },
        "west": {
            "mountain": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"],
            "pacific": ["AK", "CA", "HI", "OR", "WA"],
            "pacific northwest": ["OR", "WA", "ID"],
            "southwest": ["AZ", "NM", "OK", "TX"],
        },
    }

    result: Set[str] = set()

    for region_name in region_names:
        if region_name.lower() in regions:
            result = result.union(
                [
                    abbr
                    for subregion in regions[region_name.lower()]
                    for abbr in regions[region_name.lower()][subregion]
                ]
            )

        for main_region in regions.values():
            if region_name.lower() in main_region:
                result = result.union(main_region[region_name.lower()])

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

    return filter_by_regions_gdf(geodataframe, selected_states_gdf)


def filter_by_regions_gdf(
    geodataframe: gpd.GeoDataFrame, filter_regions_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Filters the geodataframe with filter regions. Regions touching the filter-regions are included.

    Parameters
    geodataframe (GeoDataFrame): GeoDataFrame to be filtered.
    filter_regions_gdf (GeoDataFrame): GeoDataFrame with regions as filters.
    """

    filter_regions_gdf = filter_regions_gdf.to_crs(geodataframe.crs)
    filtered_gdf = gpd.sjoin(
        geodataframe, filter_regions_gdf, how="inner", predicate="intersects"
    )
    return filtered_gdf.drop(columns=["index_right"])
