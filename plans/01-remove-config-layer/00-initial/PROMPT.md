There appear to be many config items missing from the map, especially email channel support. The full config schema is documented in the Nanobot source code here: https://github.com/HKUDS/nanobot/blob/main/nanobot/config/schema.py

We should support all options and expose them as environment variables, handling any conversions like we already do.

We should also create a new skill called "config-schema-sync" which rechecks the above "schema.py" link and then add a new config items to our mapping, or remove any deprecated/removed properties. The skill should be run to sync the current latest Nanobot config schema with our own.
