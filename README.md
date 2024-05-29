 Overlay Analysys: vectors2raster
=======================


main function
------------------------------
 - Unify the coordinate system of vector layers
 - Rasterize Vector layers
 - Overlay analysis not affected by NODATA settings

how to use
------------------------------
 - Select up to 6 vector layers for analysis
 - Enter the field name for analysis
 - Set the pixel size of the final result
 - Select the analysis method among Sum, Mean, Max (maximum), and Min (minimum)
 - set the storage path if necessary (the analysis results will loaded on the current canvas, whether specified or not)

Cautuon
------------------------------
 - Field for analysis must be in all vector layers
 - The data format of the field for analysis must be set to Int
 - The extent of the final output is fixed to the minimum rectangle area containing the selected vector layers
 - The coordinate system of the final output is fixed as EPSG:3857
 - python 3.10 or higher is required to run this plugin
