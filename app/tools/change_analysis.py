import traceback
from pathlib import Path
from typing import Any

import numpy as np
import tifffile
from PIL import Image, ImageChops

from app.data_sources.sentinel_provider import SentinelProvider
from app.tools.base import BaseTool


class ChangeAnalysisTool(BaseTool):
    name = "change_analysis"

    description = (
        "Detect land, surface, and vegetation changes between "
        "two satellite images or two Sentinel-2 observations."
    )

    def __init__(self) -> None:
        self.sentinel_provider = SentinelProvider()

    # =========================================================
    # MAIN TOOL EXECUTION
    # =========================================================

    def run(
        self,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:

        try:
            threshold = int(
                float(
                    parameters.get(
                        "change_threshold",
                        30,
                    )
                )
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "change_threshold must be a valid number."
            ) from error

        try:
            min_change_pixels = int(
                float(
                    parameters.get(
                        "min_change_pixels",
                        20,
                    )
                )
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "min_change_pixels must be a valid number."
            ) from error

        image_urls = parameters.get(
            "image_urls",
            [],
        )

        if image_urls is None:
            image_urls = []

        if not isinstance(
            image_urls,
            list,
        ):
            raise ValueError(
                "image_urls must be a list."
            )

        before_metadata = None
        after_metadata = None

        before_ndvi_metadata = None
        after_ndvi_metadata = None

        before_ndvi_path = None
        after_ndvi_path = None

        # =====================================================
        # OPTION 1: COMPARE TWO EXISTING LOCAL IMAGES
        # =====================================================

        if len(image_urls) >= 2:

            before_path = image_urls[0]
            after_path = image_urls[1]

        # =====================================================
        # OPTION 2: DOWNLOAD REAL SENTINEL-2 DATA
        # =====================================================

        else:

            bbox = parameters.get(
                "bbox"
            )

            before_date = parameters.get(
                "before_date"
            )

            after_date = parameters.get(
                "after_date"
            )

            # -------------------------------------------------
            # IMPORTANT:
            # Pydantic may convert request dates into datetime.date
            # objects. SentinelProvider expects ISO date strings.
            # -------------------------------------------------

            if before_date is not None:
                before_date = str(
                    before_date
                )

            if after_date is not None:
                after_date = str(
                    after_date
                )

            if not bbox:
                raise ValueError(
                    "Change analysis requires either at least "
                    "two 'image_urls' or a 'bbox' with "
                    "'before_date' and 'after_date'."
                )

            if (
                not isinstance(
                    bbox,
                    list,
                )
                or len(bbox) != 4
            ):
                raise ValueError(
                    "bbox must contain exactly four values: "
                    "[min_lon, min_lat, max_lon, max_lat]."
                )

            try:
                bbox = [
                    float(value)
                    for value in bbox
                ]
            except (
                TypeError,
                ValueError,
            ) as error:
                raise ValueError(
                    "All bbox values must be valid numbers."
                ) from error

            if not before_date:
                raise ValueError(
                    "'before_date' is required for Sentinel-2 "
                    "change analysis."
                )

            if not after_date:
                raise ValueError(
                    "'after_date' is required for Sentinel-2 "
                    "change analysis."
                )

            print(
                "\n=== CHANGE ANALYSIS STARTED ==="
            )

            print(
                f"Before date: {before_date}"
            )

            print(
                f"After date: {after_date}"
            )

            print(
                f"BBox: {bbox}"
            )

            # ================================================
            # DOWNLOAD BEFORE TRUE COLOR IMAGE
            # ================================================

            print(
                "\nDownloading BEFORE Sentinel-2 image..."
            )

            before_result = (
                self.sentinel_provider
                .download_sentinel2_image_for_date(
                    bbox=bbox,
                    target_date=before_date,
                    output_path=(
                        "data/change_before.png"
                    ),
                    search_window_days=30,
                    max_cloud_coverage=80.0,
                )
            )

            # ================================================
            # DOWNLOAD AFTER TRUE COLOR IMAGE
            # ================================================

            print(
                "\nDownloading AFTER Sentinel-2 image..."
            )

            after_result = (
                self.sentinel_provider
                .download_sentinel2_image_for_date(
                    bbox=bbox,
                    target_date=after_date,
                    output_path=(
                        "data/change_after.png"
                    ),
                    search_window_days=30,
                    max_cloud_coverage=80.0,
                )
            )

            before_path = before_result[
                "image_path"
            ]

            after_path = after_result[
                "image_path"
            ]

            before_metadata = before_result
            after_metadata = after_result

            # ================================================
            # DOWNLOAD BEFORE NDVI
            # ================================================

            try:

                print(
                    "\nDownloading BEFORE NDVI data..."
                )

                before_ndvi_result = (
                    self.sentinel_provider
                    .download_ndvi_for_date(
                        bbox=bbox,
                        target_date=before_date,
                        output_path=(
                            "data/ndvi_before.tiff"
                        ),
                        search_window_days=30,
                        max_cloud_coverage=30.0,
                    )
                )

                before_ndvi_path = (
                    before_ndvi_result.get(
                        "ndvi_data_path"
                    )
                )

                before_ndvi_metadata = (
                    before_ndvi_result
                )

            except Exception as error:

                print(
                    "\nWARNING: Before NDVI download failed:"
                )

                print(
                    str(error)
                )

                traceback.print_exc()

            # ================================================
            # DOWNLOAD AFTER NDVI
            # ================================================

            try:

                print(
                    "\nDownloading AFTER NDVI data..."
                )

                after_ndvi_result = (
                    self.sentinel_provider
                    .download_ndvi_for_date(
                        bbox=bbox,
                        target_date=after_date,
                        output_path=(
                            "data/ndvi_after.tiff"
                        ),
                        search_window_days=30,
                        max_cloud_coverage=30.0,
                    )
                )

                after_ndvi_path = (
                    after_ndvi_result.get(
                        "ndvi_data_path"
                    )
                )

                after_ndvi_metadata = (
                    after_ndvi_result
                )

            except Exception as error:

                print(
                    "\nWARNING: After NDVI download failed:"
                )

                print(
                    str(error)
                )

                traceback.print_exc()

        # =====================================================
        # LOAD RGB IMAGES
        # =====================================================

        print(
            "\nLoading RGB images..."
        )

        before_image = self._load_image(
            before_path
        )

        after_image = self._load_image(
            after_path
        )

        original_before_size = (
            before_image.size
        )

        original_after_size = (
            after_image.size
        )

        before_image, after_image = (
            self._resize_to_match(
                before_image,
                after_image,
            )
        )

        # =====================================================
        # RGB PIXEL DIFFERENCE
        # =====================================================

        print(
            "Calculating RGB pixel difference..."
        )

        difference = ImageChops.difference(
            before_image,
            after_image,
        )

        difference_array = np.asarray(
            difference,
            dtype=np.uint8,
        )

        if difference_array.ndim == 3:

            max_difference = np.max(
                difference_array,
                axis=2,
            )

        else:

            max_difference = (
                difference_array
            )

        # =====================================================
        # CREATE CHANGE MASK
        # =====================================================

        change_mask = (
            max_difference > threshold
        )

        changed_pixels = int(
            np.sum(change_mask)
        )

        total_pixels = int(
            change_mask.size
        )

        if total_pixels == 0:
            raise RuntimeError(
                "Unable to calculate change statistics "
                "because the image contains no pixels."
            )

        change_percentage = round(
            (
                changed_pixels
                / total_pixels
            )
            * 100,
            4,
        )

        change_detected = (
            changed_pixels
            >= min_change_pixels
        )

        # =====================================================
        # SAVE RGB CHANGE MASK
        # =====================================================

        mask_array = (
            change_mask.astype(
                np.uint8
            )
            * 255
        )

        mask_image = Image.fromarray(
            mask_array,
            mode="L",
        )

        change_mask_path = (
            Path("data")
            / "change_mask.png"
        )

        change_mask_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        mask_image.save(
            change_mask_path
        )

        # =====================================================
        # NDVI ANALYSIS
        # =====================================================

        ndvi_result = None
        ndvi_error = None

        if (
            before_ndvi_path
            and after_ndvi_path
        ):

            try:

                print(
                    "Calculating NDVI change..."
                )

                ndvi_result = (
                    self._analyze_ndvi_change(
                        before_ndvi_path,
                        after_ndvi_path,
                    )
                )

            except Exception as error:

                ndvi_error = str(
                    error
                )

                print(
                    "\nWARNING: NDVI analysis failed:"
                )

                print(
                    ndvi_error
                )

                traceback.print_exc()

        # =====================================================
        # BUILD RESPONSE
        # =====================================================

        result = {
            "tool": self.name,
            "status": "success",
            "before_image": str(
                before_path
            ),
            "after_image": str(
                after_path
            ),
            "before_size": {
                "width": (
                    original_before_size[0]
                ),
                "height": (
                    original_before_size[1]
                ),
            },
            "after_size": {
                "width": (
                    original_after_size[0]
                ),
                "height": (
                    original_after_size[1]
                ),
            },
            "change_threshold": threshold,
            "min_change_pixels": (
                min_change_pixels
            ),
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "change_percentage": (
                change_percentage
            ),
            "change_detected": (
                change_detected
            ),
            "change_mask_path": str(
                change_mask_path
            ),
        }

        # =====================================================
        # SENTINEL BEFORE METADATA
        # =====================================================

        if before_metadata:

            result["before_sentinel"] = {
                "product_id": (
                    before_metadata.get(
                        "product_id"
                    )
                ),
                "datetime": (
                    before_metadata.get(
                        "datetime"
                    )
                ),
                "cloud_cover": (
                    before_metadata.get(
                        "cloud_cover"
                    )
                ),
            }

        # =====================================================
        # SENTINEL AFTER METADATA
        # =====================================================

        if after_metadata:

            result["after_sentinel"] = {
                "product_id": (
                    after_metadata.get(
                        "product_id"
                    )
                ),
                "datetime": (
                    after_metadata.get(
                        "datetime"
                    )
                ),
                "cloud_cover": (
                    after_metadata.get(
                        "cloud_cover"
                    )
                ),
            }

        # =====================================================
        # NDVI RESULT
        # =====================================================

        if ndvi_result:

            result["ndvi_analysis"] = (
                ndvi_result
            )

            result["mean_ndvi_before"] = (
                ndvi_result[
                    "mean_ndvi_before"
                ]
            )

            result["mean_ndvi_after"] = (
                ndvi_result[
                    "mean_ndvi_after"
                ]
            )

            result["ndvi_change"] = (
                ndvi_result[
                    "ndvi_change"
                ]
            )

            result[
                "vegetation_change_percentage"
            ] = (
                ndvi_result[
                    "vegetation_change_percentage"
                ]
            )

            result[
                "vegetation_loss_detected"
            ] = (
                ndvi_result[
                    "vegetation_loss_detected"
                ]
            )

            result[
                "vegetation_gain_detected"
            ] = (
                ndvi_result[
                    "vegetation_gain_detected"
                ]
            )

            result["vegetation_status"] = (
                ndvi_result[
                    "vegetation_status"
                ]
            )

        elif ndvi_error:

            result["ndvi_analysis"] = {
                "status": "unavailable",
                "error": ndvi_error,
            }

        # =====================================================
        # BEFORE NDVI METADATA
        # =====================================================

        if before_ndvi_metadata:

            result[
                "before_ndvi_sentinel"
            ] = {
                "product_id": (
                    before_ndvi_metadata.get(
                        "product_id"
                    )
                ),
                "datetime": (
                    before_ndvi_metadata.get(
                        "datetime"
                    )
                ),
                "cloud_cover": (
                    before_ndvi_metadata.get(
                        "cloud_cover"
                    )
                ),
                "ndvi_data_path": (
                    before_ndvi_path
                ),
            }

        # =====================================================
        # AFTER NDVI METADATA
        # =====================================================

        if after_ndvi_metadata:

            result[
                "after_ndvi_sentinel"
            ] = {
                "product_id": (
                    after_ndvi_metadata.get(
                        "product_id"
                    )
                ),
                "datetime": (
                    after_ndvi_metadata.get(
                        "datetime"
                    )
                ),
                "cloud_cover": (
                    after_ndvi_metadata.get(
                        "cloud_cover"
                    )
                ),
                "ndvi_data_path": (
                    after_ndvi_path
                ),
            }

        print(
            "\n=== CHANGE ANALYSIS COMPLETED ===\n"
        )

        return result

    # =====================================================
    # ANALYZE NDVI CHANGE
    # =====================================================

    def _analyze_ndvi_change(
        self,
        before_path: str,
        after_path: str,
    ) -> dict[str, Any]:

        before_ndvi = (
            self._load_ndvi_array(
                before_path
            )
        )

        after_ndvi = (
            self._load_ndvi_array(
                after_path
            )
        )

        before_ndvi, after_ndvi = (
            self._resize_ndvi_to_match(
                before_ndvi,
                after_ndvi,
            )
        )

        valid_mask = (
            np.isfinite(before_ndvi)
            & np.isfinite(after_ndvi)
            & (before_ndvi >= -1.0)
            & (before_ndvi <= 1.0)
            & (after_ndvi >= -1.0)
            & (after_ndvi <= 1.0)
        )

        if not np.any(
            valid_mask
        ):
            raise RuntimeError(
                "No valid NDVI pixels found "
                "for vegetation analysis."
            )

        valid_before = (
            before_ndvi[
                valid_mask
            ]
        )

        valid_after = (
            after_ndvi[
                valid_mask
            ]
        )

        mean_ndvi_before = float(
            np.mean(
                valid_before
            )
        )

        mean_ndvi_after = float(
            np.mean(
                valid_after
            )
        )

        ndvi_change = (
            mean_ndvi_after
            - mean_ndvi_before
        )

        if (
            abs(mean_ndvi_before)
            < 0.000001
        ):

            vegetation_change_percentage = 0.0

        else:

            vegetation_change_percentage = (
                ndvi_change
                / abs(mean_ndvi_before)
            ) * 100

        significant_change_threshold = (
            0.02
        )

        vegetation_loss_detected = (
            ndvi_change
            < -significant_change_threshold
        )

        vegetation_gain_detected = (
            ndvi_change
            > significant_change_threshold
        )

        if vegetation_loss_detected:

            vegetation_status = (
                "vegetation_loss"
            )

        elif vegetation_gain_detected:

            vegetation_status = (
                "vegetation_gain"
            )

        else:

            vegetation_status = (
                "stable"
            )

        return {
            "status": "success",
            "before_ndvi_path": str(
                before_path
            ),
            "after_ndvi_path": str(
                after_path
            ),
            "mean_ndvi_before": round(
                mean_ndvi_before,
                4,
            ),
            "mean_ndvi_after": round(
                mean_ndvi_after,
                4,
            ),
            "ndvi_change": round(
                ndvi_change,
                4,
            ),
            "vegetation_change_percentage": round(
                vegetation_change_percentage,
                2,
            ),
            "vegetation_loss_detected": (
                vegetation_loss_detected
            ),
            "vegetation_gain_detected": (
                vegetation_gain_detected
            ),
            "vegetation_status": (
                vegetation_status
            ),
            "valid_ndvi_pixels": int(
                np.sum(
                    valid_mask
                )
            ),
        }

    # =====================================================
    # LOAD NDVI TIFF / GEOTIFF
    # =====================================================

    def _load_ndvi_array(
        self,
        ndvi_path: str,
    ) -> np.ndarray:

        path = Path(
            ndvi_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"NDVI file not found: "
                f"{ndvi_path}"
            )

        if path.stat().st_size == 0:
            raise RuntimeError(
                f"NDVI file is empty: "
                f"{ndvi_path}"
            )

        try:

            array = tifffile.imread(
                str(path)
            )

        except Exception as error:

            raise RuntimeError(
                f"Unable to read NDVI TIFF "
                f"'{ndvi_path}': {error}"
            ) from error

        array = np.asarray(
            array,
            dtype=np.float32,
        )

        # Handle 3D arrays.
        if array.ndim == 3:

            # Band-first:
            # (bands, height, width)
            if (
                array.shape[0] <= 10
                and array.shape[1] > 10
                and array.shape[2] > 10
            ):

                array = array[
                    0
                ]

            # Band-last:
            # (height, width, bands)
            else:

                array = array[
                    :,
                    :,
                    0,
                ]

        array = np.squeeze(
            array
        )

        if array.ndim != 2:

            raise RuntimeError(
                f"Invalid NDVI array shape "
                f"{array.shape} in "
                f"'{ndvi_path}'"
            )

        finite_values = (
            array[
                np.isfinite(
                    array
                )
            ]
        )

        if finite_values.size == 0:

            raise RuntimeError(
                f"NDVI file contains no "
                f"finite values: "
                f"{ndvi_path}"
            )

        max_abs_value = float(
            np.max(
                np.abs(
                    finite_values
                )
            )
        )

        if max_abs_value > 2.0:

            array = (
                array / 10000.0
            )

        array[
            (array < -1.0)
            | (array > 1.0)
        ] = np.nan

        return array

    # =====================================================
    # RESIZE NDVI ARRAYS
    # =====================================================

    def _resize_ndvi_to_match(
        self,
        first: np.ndarray,
        second: np.ndarray,
    ) -> tuple[
        np.ndarray,
        np.ndarray,
    ]:

        if first.shape == second.shape:
            return first, second

        height = first.shape[0]
        width = first.shape[1]

        second_image = (
            Image.fromarray(
                second.astype(
                    np.float32
                ),
                mode="F",
            )
        )

        second_image = (
            second_image.resize(
                (
                    width,
                    height,
                ),
                Image.Resampling.BILINEAR,
            )
        )

        resized_second = (
            np.asarray(
                second_image,
                dtype=np.float32,
            )
        )

        return (
            first,
            resized_second,
        )

    # =====================================================
    # LOAD RGB IMAGE
    # =====================================================

    def _load_image(
        self,
        image_path: str,
    ) -> Image.Image:

        path = Path(
            image_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Image file not found: "
                f"{image_path}"
            )

        if path.stat().st_size == 0:
            raise RuntimeError(
                f"Image file is empty: "
                f"{image_path}"
            )

        try:

            with Image.open(
                path
            ) as image:

                return (
                    image
                    .convert("RGB")
                    .copy()
                )

        except Exception as error:

            raise RuntimeError(
                f"Unable to read image "
                f"'{image_path}': {error}"
            ) from error

    # =====================================================
    # RESIZE RGB IMAGES
    # =====================================================

    def _resize_to_match(
        self,
        first: Image.Image,
        second: Image.Image,
    ) -> tuple[
        Image.Image,
        Image.Image,
    ]:

        if first.size == second.size:
            return first, second

        second = second.resize(
            first.size,
            Image.Resampling.BILINEAR,
        )

        return (
            first,
            second,
        )