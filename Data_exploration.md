# Data Exploration

For the sake of privacy some information were edited

```
$ aws s3 ls not-boring-company-cogs
                            PRE 20220101_hurricane_Zac/
                            PRE 20230101_town1_tx_tornado/
                            PRE 20230102_town2_tx_tornado/
                            PRE 20230103_town3_tx_tornado/
                            PRE 20230201_vt_flood/
                            PRE 20240101_town1_nm_fires/
                            PRE 20240102_town1_nm_fires/
                            ...
```

- Looking at a particular COG

```
    $ aws s3 ls not-boring-company-cogs/20240101_town1_nm_fires/ --recursive --human
    2024-01-01 04:18:25    0 Bytes 20240101_town1_nm_fires/
    2024-01-01 05:49:58  138 Bytes 20240101_town1_nm_fires/cog.prj
    2024-01-01 05:49:58   67 Bytes 20240101_town1_nm_fires/cog.tfw
    2024-01-01 05:52:34   19.5 GiB 20240101_town1_nm_fires/cog.tif
```

🤔 rio-cogeo says it’s not a Valid COG

```
$ rio cogeo info s3://not-boring-company-cogs/20240101_town1_nm_fires/cog.tif
Driver: GTiff
File: s3://not-boring-company-cogs/20240101_town1_nm_fires/cog.tif
COG: False
Compression: LZW
ColorSpace: None

Profile
    Width:            104074
    Height:           108955
    Bands:            4
    Tiled:            True
    Dtype:            uint8
    NoData:           None
    Alpha Band:       True
    Internal Mask:    False
    Interleave:       PIXEL
    ColorMap:         False
    ColorInterp:      ('red', 'green', 'blue', 'alpha')
    Scales:           (1.0, 1.0, 1.0, 1.0)
    Offsets:          (0.0, 0.0, 0.0, 0.0)

Geo
    Crs:              EPSG:4326
    Origin:           (-97.141113, 7.762030)
    Resolution:       (8.476000000000599e-07, -8.476000000000302e-07)
    BoundingBox:      (-97.141113, 36.686041, -95.048218,3 7.762030)
    MinZoom:          12
    MaxZoom:          21

Image Metadata
    AREA_OR_POINT: Area
    TIFFTAG_SOFTWARE: SOME GIS SOFTWARE

Image Structure
    COMPRESSION: LZW
    INTERLEAVE: PIXEL
    PREDICTOR: 2

Band 1
    ColorInterp: red

Band 2
    ColorInterp: green

Band 3
    ColorInterp: blue

Band 4
    ColorInterp: alpha

IFD
    Id      Size           BlockSize     Decimation
    0       104074x108955  128x128       0
    1       52037x54478    128x128       2
    2       26019x27239    128x128       4
    3       13010x13620    128x128       8
    4       6505x6810      128x128       16
    5       3253x3405      128x128       32
    6       1627x1703      128x128       64
    7       814x852        128x128       128

COG Validation info
    - The offset of the main IFD should be < 300. It is 14265227280 instead (error)
    - The offset of the first block of overview of index 5 should be after the one of the overview of index 6 (error)
    - The offset of the first block of overview of index 4 should be after the one of the overview of index 5 (error)
    - The offset of the first block of overview of index 3 should be after the one of the overview of index 4 (error)
    - The offset of the first block of overview of index 2 should be after the one of the overview of index 3 (error)
    - The offset of the first block of overview of index 1 should be after the one of the overview of index 2 (error)
    - The offset of the first block of overview of index 0 should be after the one of the overview of index 1 (error)
    - The offset of the first block of the main resolution image should be after the one of the overview of index 6 (error)
```

⚠️ The “COG”  wasn’t created using rio-cogeo (we set a specific Tags).


    - They are using LZW compression for a RGBA dataset, **they should use JPEG/WEBP** if they are ok with loss (because those driver are not lossless…. but for visualization purpose this should be fine)

    - The CRS is set to EPSG:4326, I assume the original projection is `local` so maybe they will be ok with a WebOptimized COG (epsg:3857).  EDIT: not all the data is in epsg:4326

I think I know why they are not COG :

```
$ rio info s3://not-boring-company-cogs/20240101_town1_nm_fires/cog.tif
WARNING:rasterio._env:CPLE_AppDefined in cog.tif: This file used to have optimizations in its layout, but those have been, at least partly, invalidated by later changes
...
```

This tells us that the file was updated after creation. I’m guessing they added the overviews after the `COG` creation, which also explain the rio-cogeo error messages.

## TIF COMPRESSION

**from ~1.1G to 55Mb:**


    # Create a proper COG
    $ rio cogeo create bad_cog.tif true_cog.tif -p LZW
    $ ls -lah true_cog.tif
    -rw-r--r--  1 vincentsarago  staff   1.6G Sep  6 17:20 true_cog.tif

    # Create a COG using JPEG compression
    $ rio cogeo create bad_cog.tif true_cog_JPEG.tif -p JPEG --add-mask
    $ ls -lah true_cog_JPEG.tif
    -rw-r--r--    1 vincentsarago  staff    94M Sep  6 17:21 true_cog_JPEG.tif

    # Create a COG using JPEG compression + WebOptimized
    $ rio cogeo create bad_cog.tif true_cog_JPEG_Web.tif -p JPEG --add-mask -w
    $ ls -lah true_cog_JPEG_Web.tif
    -rw-r--r--  1 vincentsarago  staff    55M Sep  6 17:45 true_cog_JPEG_Web.tif

