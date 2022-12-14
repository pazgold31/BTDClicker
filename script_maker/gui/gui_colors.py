import random

EXISTING_TOWERS_COLORS = [
    "#800000",  # maroon
    "#A52A2A",  # brown
    "#B22222",  # firebrick
    "#FF0000",  # red
    "#FF6347",  # tomato
    "#FF7F50",  # coral
    "#CD5C5C",  # indian red
    "#F08080",  # light coral
    "#E9967A",  # dark salmon
    "#FA8072",  # salmon
    "#FFA07A",  # light salmon
    "#FF4500",  # orange red
    "#FF8C00",  # dark orange
    "#FFA500",  # orange
    "#FFD700",  # gold
    "#B8860B",  # dark golden rod
    "#DAA520",  # golden rod
    "#EEE8AA",  # pale golden rod
    "#BDB76B",  # dark khaki
    "#F0E68C",  # khaki
    "#808000",  # olive
    "#FFFF00",  # yellow
    "#9ACD32",  # yellow green
    "#556B2F",  # dark olive green
    "#6B8E23",  # olive drab
    "#7CFC00",  # lawn green
    "#7FFF00",  # chartreuse
    "#ADFF2F",  # green yellow
    "#006400",  # dark green
    "#008000",  # green
    "#228B22",  # forest green
    "#00FF00",  # lime
    "#32CD32",  # lime green
    "#90EE90",  # light green
    "#98FB98",  # pale green
    "#8FBC8F",  # dark sea green
    "#00FA9A",  # medium spring green
    "#00FF7F",  # spring green
    "#2E8B57",  # sea green
    "#66CDAA",  # medium aqua marine
    "#3CB371",  # medium sea green
    "#20B2AA",  # light sea green
    "#008080",  # teal
    "#00FFFF",  # aqua
    "#00FFFF",  # cyan
    "#E0FFFF",  # light cyan
    "#00CED1",  # dark turquoise
    "#40E0D0",  # turquoise
    "#48D1CC",  # medium turquoise
    "#AFEEEE",  # pale turquoise
    "#7FFFD4",  # aqua marine
    "#B0E0E6",  # powder blue
    "#5F9EA0",  # cadet blue
    "#4682B4",  # steel blue
    "#6495ED",  # corn flower blue
    "#00BFFF",  # deep sky blue
    "#1E90FF",  # dodger blue
    "#ADD8E6",  # light blue
    "#87CEEB",  # sky blue
    "#87CEFA",  # light sky blue
    "#4169E1",  # royal blue
    "#8A2BE2",  # blue violet
    "#4B0082",  # indigo
    "#483D8B",  # dark slate blue
    "#6A5ACD",  # slate blue
    "#7B68EE",  # medium slate blue
    "#9370DB",  # medium purple
    "#8B008B",  # dark magenta
    "#9400D3",  # dark violet
    "#9932CC",  # dark orchid
    "#BA55D3",  # medium orchid
    "#D8BFD8",  # thistle
    "#DDA0DD",  # plum
    "#EE82EE",  # violet
    "#DA70D6",  # orchid
    "#C71585",  # medium violet red
    "#DB7093",  # pale violet red
    "#FF1493",  # deep pink
    "#FF69B4",  # hot pink
    "#FFB6C1",  # light pink
    "#FFC0CB",  # pink
    "#F5F5DC",  # beige
    "#FFE4C4",  # bisque
    "#FFEBCD",  # blanched almond
    "#F5DEB3",  # wheat
    "#FFF8DC",  # corn silk
    "#FAFAD2",  # light golden rod yellow
    "#FFFFE0",  # light yellow
    "#8B4513",  # saddle brown
    "#D2691E",  # chocolate
    "#CD853F",  # peru
    "#F4A460",  # sandy brown
    "#DEB887",  # burly wood
    "#D2B48C",  # tan
    "#BC8F8F",  # rosy brown
    "#FFE4B5",  # moccasin
    "#FFDAB9",  # peach puff
    "#FFE4E1",  # misty rose
    "#FFF0F5",  # lavender blush
    "#FAF0E6",  # linen
    "#FDF5E6",  # old lace
    "#FFEFD5",  # papaya whip
    "#FFF5EE",  # seashell
    "#708090",  # slate gray
    "#778899",  # light slate gray
    "#B0C4DE",  # light steel blue
    "#E6E6FA",  # lavender
    "#F0F8FF",  # alice blue
    "#F0FFF0",  # honeydew
    "#FFFFF0",  # ivory
    "#F0FFFF",  # azure
    "#FFFAFA",  # snow
    "#696969",  # dim gray / dim grey
    "#808080",  # gray / grey
    "#A9A9A9",  # dark gray / dark grey
    "#C0C0C0",  # silver
    "#D3D3D3",  # light gray / light grey
    "#DCDCDC",  # gainsboro
]
random.shuffle(EXISTING_TOWERS_COLORS)

ALTERNATING_DARK_COLOR = "#A9A9A9"
ALTERNATING_LIGHT_COLOR = "#D3D3D3"

GLOBAL_ENTRIES_COLOR = "#FF00FF"
