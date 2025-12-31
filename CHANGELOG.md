# Changelog

All notable changes to the Adobe Stock Generator project will be documented in this file.

## [v1.9] - 2025-12-31
### Changed
- **Critical Memory Optimization**: Enabled FP16 (half-precision) mode in `generation_pipeline.py`.
- **Stability**: Reduced default `TILE_SIZE` from 384 to 256 to prevent OOM errors on standard GPUs.

### Fixed
- Fixed `numpy._core._exceptions._ArrayMemoryError` crashing the upscaling pipeline during 4K image generation.

## [v1.85] - 2025-12-30
### Fixed
- **Category Mapping**: Corrected category ID mapping in `adobe_stock_guidelines.md`.
- **Select All Bug**: Fixed issue where hidden filtered images were being selected.

### Added
- **UI Guide**: Added category selection guidelines in helper text.

## [v1.84] - 2025-12-25
### Added
- **Strategy Guide**: Integrated Power Law strategy documentation.
- **Barbell Strategy**: Defined portfolio allocation (60% Evergreen / 30% Seasonal / 10% Trending).

## [v1.83] - 2025-12-20
### Changed
- **Workflow**: Enforced manual agent analysis `view_file` step before metadata creation.
- **Keywords**: Increased recommended keyword count to 25-35.

## [v1.82] - 2025-12-15
### Changed
- **CSV Generation**: Removed auto-generation; switched to manual button trigger.
- **JSON Handling**: Improved robustness for UTF-8 BOM files.

## [v1.81] - 2025-12-10
### Added
- **Filter**: Added dropdown filter for Drafts (All/Raw/Processed/Upscaled).

## [v1.8] - 2025-12-05
### Changed
- **CSV Output**: `submission.csv` is now generated directly in the `upscaled/` folder.
- **Metadata**: JSON metadata is auto-copied to `upscaled/` folder during processing.

## [v1.7] - 2025-12-01
### Added
- **Real-time Monitoring**: Dashboard logs now stream stdout from background processes.
- **Process Isolation**: Upscaling now runs in a separate subprocess to prevent server crashes.

## [v1.6] - 2025-11-20
### Changed
- **Memory Management**: Implemented aggressive `gc.collect()` and model unloading per image.
- **Logging**: Separated `error.log` for better debugging.

## [v1.5] - 2025-11-10
### Added
- **JSON Sidecars**: Adopted sidecar pattern for metadata storage.
- **Metadata Generator**: New module for Adobe Stock compliant metadata creation.

## [v1.0] - 2025-10-01
- Initial Release
