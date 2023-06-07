
# Exploration
import os
if OVERVIEWER_CONFIG_DEBUG := os.environ.get('OVERVIEWER_CONFIG_DEBUG', None):
    # To run this section of code run overviewer as follows;
    #   $ docker-compose run --rm -e OVERVIEWER_CONFIG_DEBUG=yes overviewer-gen
    for name, param in globals().items():
        print(f'{name}: {param!r}')

    # To explore in mode detail, you can break here and get into python debug
    #   $ docker-compose run --rm -e OVERVIEWER_CONFIG_DEBUG=pdb overviewer-gen
    if OVERVIEWER_CONFIG_DEBUG == 'pdb':
        breakpoint()
    # > /tmp/config/config.py(15)<module>()
    #(Pdb) 
    
texturepath = "/tmp/overviewer/client.jar"

worlds.update({
    "My World": '/tmp/server/world',
})

# Render Modes:
#   normal:                     [Base, EdgeLines]
#   lighting:                   [Base, EdgeLines, Lighting]
#   smooth_lighting:            [Base, EdgeLines, SmoothLighting]
#   night:                      [Base, EdgeLines, Lighting]
#   smooth_night:               [Base, EdgeLines, SmoothLighting]
#   netherold:                  [Base, EdgeLines, NetherOld]
#   netherold_lighting:         [Base, EdgeLines, NetherOld, Lighting]
#   netherold_smooth_lighting:  [Base, EdgeLines, NetherOld, SmoothLighting]
#   nether:                     [Base, EdgeLines, Nether]
#   nether_lighting:            [Base, EdgeLines, Nether, Lighting]
#   nether_smooth_lighting:     [Base, EdgeLines, Nether, SmoothLighting]
#   cave:                       [Base, EdgeLines, Cave, DepthTinting]

# ----- Overworld
renders.update({
    "day": {
        "world": "My World",
        "title": "Day",
        "rendermode": smooth_lighting,
        "dimension": "overworld",
    },
})

# Slices
if os.environ.get('RENDER_SLICES', None):
    def slice_at(height):
        # Render up to a given level.
        # :param height: height above bedrock
        bedrock_level = -64
        return [Depth(
            min=bedrock_level,
            max=bedrock_level+height,
        )]

    renders.update({
        "slice-128": {
            "world": "My World",
            "title": "Slice: 0 -> 128",
            "rendermode": normal + slice_at(128),
            "dimension": "overworld",
        },
        "slice-96": {
            "world": "My World",
            "title": "Slice: 0 -> 96",
            "rendermode": normal + slice_at(96),
            "dimension": "overworld",
        },
        "slice-64": {
            "world": "My World",
            "title": "Slice: 0 -> 64",
            "rendermode": normal + slice_at(64),
            "dimension": "overworld",
        },
        "slice-32": {
            "world": "My World",
            "title": "Slice: 0 -> 32",
            "rendermode": normal + slice_at(32),
            "dimension": "overworld",
        },
    })

# Other
if os.environ.get('RENDER_NIGHT', None):
    renders.update({
        "night": {
            "world": "My World",
            "title": "Night",
            "rendermode": smooth_night,
            "dimension": "overworld",
        },
    })

if os.environ.get('RENDER_CAVES', None):
    renders.update({
        "cave": {
            "world": "My World",
            "title": "Caves",
            "rendermode": cave,
            "dimension": "overworld",
        },
    })

if os.environ.get('RENDER_HEATMAP', None):
    t_now = datetime.now()
    renders.update({
        "heatmap": {
            "world": "My World",
            "title": "Heatmap",
            "rendermode": normal + [HeatmapOverlay(
                t_invisible=int((t_now - timedelta(days=2)).timestamp()),
                t_full=int(t_now.timestamp()),
            )],
            "dimension": "overworld",
        },
    })

})

outputdir = "/tmp/export"
defaultzoom = 3
processes = 2  # slows generation down, but doesn't slow the server as much

