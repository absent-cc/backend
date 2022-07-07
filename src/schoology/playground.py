from .schoologyListener import *

from ..dataTypes import tools, structs

config_path = "config.ini"
south_key = tools.read_config(config_path, "NSHS", "key")
south_secret = tools.read_config(config_path, "NSHS", "secret")
north_key = tools.read_config(config_path, "NNHS", "key")
north_secret = tools.read_config(config_path, "NNHS", "secret")

# Define API variables.
SCHOOLOGYCREDS = structs.SchoologyCreds(
    {
        structs.SchoolName.NEWTON_NORTH: north_key,
        structs.SchoolName.NEWTON_SOUTH: south_key,
    },
    {
        structs.SchoolName.NEWTON_NORTH: north_secret,
        structs.SchoolName.NEWTON_SOUTH: south_secret,
    },
)

SchoologyListener(SCHOOLOGYCREDS).run()