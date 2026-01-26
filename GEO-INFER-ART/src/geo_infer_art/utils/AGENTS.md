# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 0 classes and 10 functions. ## Classes
 and Functions ### validate_file_pat
h
 `validate_file_path(file_path: str, extensions: List[str]) -> None` Validate that a file path exists and has the correct extension. ### validate_geospatial_dat
a
 `validate_geospatial_data(data: Union[gpd.GeoDataFrame, np.ndarray]) -> None` Validate that the data is a valid GeoDataFrame or numpy array. ### validate_coordinate
s
 `validate_coordinates(lat: float, lon: float) -> None` Validate geographic coordinates. ### validate_bbo
x
 `validate_bbox(bbox: tuple) -> None` Validate a bounding box. ### validate_colo
r
 `validate_color(color: str) -> None` Validate a color string. ### validate_style_nam
e
 `validate_style_name(style_name: str, valid_styles: List[str]) -> None` Validate a style name against a list of valid styles. ### validate_numeric_rang
e
 `validate_numeric_range(value: float, min_val: float, max_val: float, name: str) -> None` Validate that a numeric value is within a specified range. ### validate_image_arra
y
 `validate_image_array(image_array: np.ndarray) -> None` Validate a numpy array representing an image. ### validate_resolutio
n
 `validate_resolution(resolution: Tuple[int, int]) -> None` Validate image resolution. ### validate_file_forma
t
 `validate_file_format(file_path: str, valid_formats: List[str]) -> None` Validate file format against a list of valid formats. ## Capabilities
 - **10 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-ART/src/geo_infer_art/utils` - **Type**: Directory Node 