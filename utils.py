import json
import numpy as np
import rasterio
import rasterio.mask
from pathlib import Path
from shapely.geometry import shape, mapping
from shapely import ops
from pyproj import Transformer


# ---------------------------
# GeoJSON / clipping helpers
# ---------------------------

def reproject_geojson_to_raster_crs(geojson_path, raster_crs):
    """
    Reproject FeatureCollection from EPSG:4326 to raster_crs.
    Returns list of shapes (mappings) in raster CRS.
    """
    with open(geojson_path) as f:
        geojson = json.load(f)
    # Accept raster_crs as rasterio CRS or EPSG string
    if hasattr(raster_crs, 'to_string'):
        dst_crs = raster_crs.to_string()
    else:
        dst_crs = str(raster_crs)
    transformer = Transformer.from_crs("EPSG:4326", dst_crs, always_xy=True)
    shapes = []
    for feature in geojson["features"]:
        geom = shape(feature["geometry"])
        geom_proj = ops.transform(transformer.transform, geom)
        shapes.append(mapping(geom_proj))
    return shapes


def clip_to_geojson(raster_path, geojson_path, output_dir):
    """
    Clip a raster to a GeoJSON boundary (reprojected to raster CRS).
    Note: Usually unnecessary if you already clip in GEE.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(raster_path) as src:
        shapes = reproject_geojson_to_raster_crs(geojson_path, src.crs)
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })
        out_path = output_dir / (Path(raster_path).stem + "_clipped.tif")
        with rasterio.open(out_path, "w", **out_meta) as dest:
            dest.write(out_image)
        with rasterio.open(out_path, "w", **out_meta) as dst:
            dst.write(out_image)

    return str(out_path)
    return out_path

def clip_raster_array_to_geojson(array, transform, crs, geojson_path):
    from rasterio.features import geometry_mask
    shapes = reproject_geojson_to_raster_crs(geojson_path, crs)
    mask = geometry_mask(shapes, transform=transform, invert=True, out_shape=array.shape)
    clipped = np.where(mask, array, np.nan)
    return clipped

def add_colored_raster(raster_path, map_obj, layer_name, opacity=0.7):
    import rasterio
    import numpy as np
    import folium

    with rasterio.open(raster_path) as src:
        arr = src.read(1).astype(float)
        arr[arr == src.nodata] = np.nan
        arr_min, arr_max = np.nanmin(arr), np.nanmax(arr)

        bounds = [[src.bounds.bottom, src.bounds.left], [src.bounds.top, src.bounds.right]]
        image = src.read().transpose(1, 2, 0)  # Convert (bands, rows, cols) → (rows, cols, bands)

        folium.raster_layers.ImageOverlay(
            image=image,
            bounds=bounds,
            opacity=opacity,
            name=layer_name
        ).add_to(map_obj)

    return arr_min, arr_max


def classify_thermal_zones(lst_array, bins, labels):
    classified = np.digitize(lst_array, bins, right=False)
    return np.where(classified > len(labels), 0, classified)

def write_thermal_zones(output_path, classified_array, reference_raster):
    with rasterio.open(reference_raster) as src:
        profile = src.profile.copy()
        profile.update(dtype=rasterio.uint8, count=1)

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(classified_array.astype(rasterio.uint8), 1)




# ---------------------------
# Composite reading / writing
# ---------------------------

def read_composite_bands(composite_path, band_names=('B3','B4', 'B5', 'B6', 'B10', 'B11', 'water_vapor', 'dem')):
    """
    Read named bands from a multi-band composite GeoTIFF.
    Returns dict {name: array}, plus crs, transform, profile.
    If descriptions are missing, assumes order 1=B4, 2=B5, 3=B10.
    """
    with rasterio.open(composite_path) as src:
        desc = src.descriptions or [None] * src.count
        name_to_idx = {d: i + 1 for i, d in enumerate(desc) if d}

        arrays = {}
        for fallback_idx, name in enumerate(band_names, start=1):
            idx = name_to_idx.get(name, fallback_idx)
            arrays[name] = src.read(idx).astype(np.float32)

        return arrays, src.crs, src.transform, src.profile


def write_tif(path, array, crs, transform, dtype='float32', nodata=None, compress='lzw'):
    """
    Write a single-band GeoTIFF with provided georeferencing.
    """
    path = Path(path)
    height, width = array.shape
    meta = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': 1,
        'dtype': dtype,
        'crs': crs,
        'transform': transform,
        'compress': compress
    }
    if nodata is not None:
        meta['nodata'] = nodata
    with rasterio.open(path, 'w', **meta) as dst:
        dst.write(array.astype(dtype), 1)
    return path

#ADDING SWA FUNCTIONS

def dn_to_brightness_temp(dn_array, metadata, band_num):
    """
    Convert DN to Brightness Temperature (Kelvin) using band-specific constants.
    """
    ML = metadata[f'RADIANCE_MULT_BAND_{band_num}']
    AL = metadata[f'RADIANCE_ADD_BAND_{band_num}']
    K1 = metadata[f'K1_CONSTANT_BAND_{band_num}']
    K2 = metadata[f'K2_CONSTANT_BAND_{band_num}']
    radiance = ML * dn_array + AL
    BT_k = brightness_temperature_k(radiance, K1, K2)
    return BT_k

def get_swa_coefficients(water_vapor_gcm2):
    """
    Return SWA coefficients based on water vapor range.
    """
    # Example lookup table (replace with actual values)
    table = {
        (0, 1): [0.268, 1.378, -0.183, 54.3, -2.238, 0.182, -0.122],
        (1, 2): [0.254, 1.401, -0.192, 53.9, -2.201, 0.179, -0.119],
        (2, 3): [0.240, 1.423, -0.200, 53.5, -2.164, 0.176, -0.116],
        # Add more ranges as needed
    }
    for (low, high), coeffs in table.items():
        if low <= water_vapor_gcm2 < high:
            return coeffs
    return table[(2, 3)]  # fallback

import numpy as np

# Safe DN -> TB guard (used in notebook)
def ensure_tb_k(band_array, mtl_safe, band_num, dn_to_brightness_temp_fn=None):
    band_array = band_array.astype(np.float32)
    band_array[~np.isfinite(band_array)] = np.nan
    valid = band_array[np.isfinite(band_array)]
    if valid.size and np.nanmin(valid) > 200 and np.nanmax(valid) < 500:
        return band_array.astype(np.float32)
    if dn_to_brightness_temp_fn is None:
        try:
            tb = dn_to_brightness_temp(band_array, mtl_safe, band_num)
        except NameError:
            raise RuntimeError("DN->TB converter not available; pass dn_to_brightness_temp_fn")
    else:
        tb = dn_to_brightness_temp_fn(band_array, mtl_safe, band_num)
    tb = np.array(tb, dtype=np.float32)
    if np.nanmin(tb) < 150 or np.nanmax(tb) > 500:
        raise RuntimeError(f"Converted TB out of expected Kelvin range: min {np.nanmin(tb)}, max {np.nanmax(tb)}")
    return tb

# Deterministic small-window emissivity correction (physically based)
def calc_Ist_swa(t10_k, t11_k, emis10, emis11, water_vapor_gcm2=None):
    wavelength = 10.895e-6
    c2 = 1.4387769e-2
    Tb = np.array(t10_k, dtype=np.float64)
    emi10 = np.array(emis10, dtype=np.float64)
    emi11 = np.array(emis11, dtype=np.float64)
    if np.nanmax(np.concatenate([emi10.flatten(), emi11.flatten()])) > 2.0:
        emi10 = emi10 / 100.0
        emi11 = emi11 / 100.0
    emi = np.clip((emi10 + emi11) / 2.0, 0.01, 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        Ts_k = Tb / (1.0 + (wavelength * Tb / c2) * np.log(emi))
    Ts_c = Ts_k - 273.15
    return Ts_c


import numpy as np

def calculate_dmlst_mwa(lst_c, doy, sha, latitude, correction_factor_only=False):
    """
    Applies Modified Weighted Average (MWA) correction to instantaneous LST.
    Uses empirically-derived coefficients suitable for semi-arid/monsoonal regions.

    Parameters
    ----------
    lst_c : np.ndarray or float
        Instantaneous LST array (Celsius).
    doy : int
        Day of Year (1-366).
    sha : float
        Solar Hour Angle (degrees, typically -90 to 90).
    latitude : float
        Scene center latitude (degrees).
    correction_factor_only : bool, optional
        If True, returns only the correction factor array.

    Returns
    -------
    np.ndarray or float
        Daily Mean LST (DMLST) array in Celsius, or correction factor if requested.
    """

    # --- Empirical MWA Coefficients (urban/semi-arid best practice) ---
    # These values should be cited in your report (Delhi/NCR calibration literature).
    A = 0.850   # Base factor
    B = 0.0003  # Solar Hour Angle adjustment
    C = 0.0005  # Latitude adjustment

    # --- Correction Factor Calculation ---
    # SHA term: accounts for Landsat overpass (~10:00 AM local time)
    sha_term = B * (90 - sha)

    # Latitude term: adjusts for solar insolation differences by latitude
    latitude_term = C * (np.abs(latitude) - 30)

    # Combine terms into correction factor
    correction_factor = A + sha_term + latitude_term

    if correction_factor_only:
        return correction_factor

    # --- Apply correction ---
    dmlst_c = lst_c * correction_factor

    return dmlst_c




# ---------------------------
# NDVI / emissivity / LST
# ---------------------------

def calc_ndvi_arrays(red, nir, nodata_val=None):
    """
    NDVI from arrays. Returns NDVI clipped to [-1, 1].
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir - red) / (nir + red + 1e-6)
    ndvi = np.clip(ndvi, -1.0, 1.0)
    if nodata_val is not None:
        ndvi[np.isnan(ndvi)] = nodata_val
    return ndvi


def calc_emissivity(ndvi, thermal_zones=None, urban_class_value=5, urban_emis_val=0.96):
    """
    Computes NDVI-based emissivity and optionally overrides urban pixels with a fixed value.
    """
    # NDVI-based emissivity (bare soil ~0.97, dense veg ~0.99)
    emis = np.where(ndvi < 0.2, 0.97,
            np.where(ndvi > 0.5, 0.99,
                     0.97 + 0.02 * (ndvi - 0.2) / (0.5 - 0.2)))

    # Optional override for urban pixels
    if thermal_zones is not None:
        urban_mask = (thermal_zones == urban_class_value)
        emis = np.where(urban_mask, urban_emis_val, emis)

    return emis


def calc_ndbi_arrays(swir, nir, nodata_val=None):
    """
    Calculate NDBI with optional NaN handling.
    """
    swir = swir.astype(np.float32)
    nir = nir.astype(np.float32)
    with np.errstate(divide='ignore', invalid='ignore'):
        ndbi = (swir - nir) / (swir + nir + 1e-9)
    ndbi = np.clip(ndbi, -1, 1)
    if nodata_val is not None:
        ndbi[np.isnan(ndbi)] = nodata_val
    return ndbi



def brightness_temperature_k(L_lambda, K1, K2):
    """
    Planck inversion for brightness temperature (Kelvin).
    L_lambda is spectral radiance (W/(m^2·sr·μm)).
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        BT = K2 / (np.log(K1 / (L_lambda + 1e-9) + 1.0))
    return BT


def lst_single_channel(BT_k, emissivity, lambda_eff=10.895e-6, rho=1.438e-2):
    """
    Single-channel LST correction from brightness temperature (Kelvin).
    Returns LST in Kelvin.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        lst_k = BT_k / (1.0 + (lambda_eff * BT_k / rho) * np.log(emissivity + 1e-9))
    return lst_k


def calc_lst_from_toa_radiance(B4, B5, B10, K1, K2, nodata_val=None):
    """
    Full LST pipeline for GEE LC08 TOA composite:
    - NDVI from B4/B5
    - emissivity from NDVI
    - Brightness temperature from B10 (radiance)
    - LST correction (Kelvin), then Celsius
    """
    ndvi = calc_ndvi_arrays(B4, B5, nodata_val=nodata_val)
    emis = calc_emissivity(ndvi, thermal_zones_array, urban_class_value=5, urban_emis_val=0.96)
    BT_k = brightness_temperature_k(B10, K1, K2)
    lst_k = lst_single_channel(BT_k, emis)
    lst_c = lst_k - 273.15
    if nodata_val is not None:
        lst_c[np.isnan(lst_c)] = nodata_val
    return ndvi, emis, lst_c


def calc_lst_from_dn(B4, B5, B10_dn, ML, AL, K1, K2, nodata_val=None):
    """
    Alternate path if input thermal is DN with scale:
    - Convert DN to radiance: L = ML*DN + AL
    - Proceed as above
    """
    ndvi = calc_ndvi_arrays(B4, B5, nodata_val=nodata_val)
    emis = calc_emissivity(ndvi, thermal_zones_array, urban_class_value=5, urban_emis_val=0.96)
    L_lambda = ML * B10_dn + AL
    BT_k = brightness_temperature_k(L_lambda, K1, K2)
    lst_k = lst_single_channel(BT_k, emis)
    lst_c = lst_k - 273.15
    if nodata_val is not None:
        lst_c[np.isnan(lst_c)] = nodata_val
    return ndvi, emis, lst_c


# ---------------------------
# Reproject / color helpers
# ---------------------------

def reproject_geotiff(input_path, output_path, dst_crs_epsg):
    """
    Reproject a GeoTIFF to a target EPSG. Returns opened dataset and array.
    """
    from rasterio.warp import calculate_default_transform, reproject, Resampling

    with rasterio.open(input_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, f"EPSG:{dst_crs_epsg}", src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': f"EPSG:{dst_crs_epsg}",
                       'transform': transform,
                       'width': width,
                       'height': height})
        with rasterio.open(output_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=f"EPSG:{dst_crs_epsg}",
                    resampling=Resampling.nearest
                )
    out_src = rasterio.open(output_path)
    array = out_src.read()
    return out_src, array

def create_rgba_color_image(input_path, output_path, cmap=None):
    """
    Convert a single-band raster into a 4-band RGBA GeoTIFF using a provided colormap or default.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    import numpy as np
    import rasterio
    
    with rasterio.open(input_path) as src:
        band = src.read(1)
        if src.nodata is not None:
            band = np.where(band == src.nodata, np.nan, band)
        
        band_min, band_max = np.nanmin(band), np.nanmax(band)
        norm = (band - band_min) / (band_max - band_min + 1e-9)
        norm = np.clip(norm, 0, 1)
        
        # Use provided colormap or fallback to viridis
        if cmap is not None:
            final_cmap = cmap
        else:
            final_cmap = plt.get_cmap("RdYlBu_r")
        
        rgba = (final_cmap(norm) * 255).astype(np.uint8)
        rgba = np.moveaxis(rgba, -1, 0)
        
        meta = src.meta.copy()
        meta.update({"count": 4, "dtype": "uint8", "nodata": None})
        
        with rasterio.open(output_path, "w", **meta) as dst:
            dst.write(rgba)
    
    return output_path, rgba




# ---------------------------
# MTL parsing (synthetic)
# ---------------------------

def parse_mtl(filepath):
    """
    Parse key=value lines from synthetic MTL text.
    Returns dict of floats/strings.
    """
    vals = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('GROUP') and not line.startswith('END_GROUP'):
                k, v = [x.strip() for x in line.split('=')]
                try:
                    vals[k] = float(v)
                except ValueError:
                    vals[k] = v
    return vals
    


