# Not-Boring-Company - Case Study

## Preliminary work

[Exploring the available Datasets](Data_exploration.md)

## eoAPI - STAC + COGs

1. Create COGs

As mentioned in the Data exploration document, the "COGs" are not proper COGs so we need re-created them.

Note: we're using rio-cogeo but could use `gdal_translate -of COG` as well.

requirements: `rio-cogeo, aws-cli`

```
aws s3 ls s3://not-boring-company-cogs-cogs/20230201_vt_flood/ --recursive | awk '{print "s3://not-boring-company-cogs-cogs/"$NF}'| grep ".tif" | while read line; do name=$(echo $line | rev | cut -d"/" -f2 | rev); aws s3 cp $line data/cog.tif; rio cogeo create data/cog.tif data/NOTBORING_VT_flood_$name.tif -p JPEG -w --add-mask; rm data/cog.tif; done
```

2. Create STAC Items

Note: The data doesn't have metadata, so we are using the directory name to extract the datetime metadata (`2023-02-01T00:00:00`).

requirements: `rio-stac, pystac`

```
# Create STAC Items
$ ls -1 data/*tif | while read line; do rio stac $line -c "not-boring-comp-vt-flood" --asset-mediatype COG -n cog --asset-href $line --without-proj -d "2023-02-01T00:00:00" --collection-url data/collection.json ; done > data/items.json

# Create STAC Collection
$ python scripts/create_collection.py > data/collection.json
```

3. Ingest data

requirements: `pypgstac==0.8.5` (same version as PgSTAC defined in docker-compose.yml)

- Launch PgSTAC database and other services

```
docker compose up database  -d
```

- Ingest STAC items/collection

```
pypgstac load collections data/collection.json --dsn postgresql://username:password@127.0.0.1:5439/postgis

pypgstac load items data/items.json --dsn postgresql://username:password@127.0.0.1:5439/postgis
```


4. See the data

```
http://0.0.0.0:8082/collections/not-boring-comp-vt-flood/map?assets=cog
```

![](img/map.png)
