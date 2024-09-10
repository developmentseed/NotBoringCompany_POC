
import pystac
from pystac.utils import str_to_datetime
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
import json

if __name__ == "__main__":

    with open("data/items.json", "r") as f:
        bboxes = [json.loads(l.strip("\n"))["bbox"] for l in f.readlines()]
        minx, miny, maxx, maxy = zip(*bboxes)
        bboxes = [[min(minx), min(miny), max(maxx), max(maxy)], *bboxes]

    collection = pystac.Collection(
        id="not-boring-comp-vt-flood",
        title="Not Boring Company Imagery for the 2023 VT flood",
        description="Not Boring Company Imagery for the 2023 VT flood",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent(bboxes),
            temporal=pystac.TemporalExtent(
                intervals=[
                    [str_to_datetime("2023-02-01T00:00:00Z"), None],
                ]
            )
        )
    )

    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = {
        "cog": AssetDefinition.create(
            title="COG",
            description=None,
            media_type="image/tiff; application=geotiff; profile=cloud-optimized",
            roles=None,
        ),
    }

    assert collection.validate()
    print(json.dumps(collection.to_dict(), indent=2))
