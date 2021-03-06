# Author: echel0n <echel0n@sickrage.ca>
# URL: http://github.com/SiCKRAGETV/SickRage/
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from sickrage.core.databases import Connection, SchemaUpgrade


class CacheDB(Connection):
    def __init__(self, filename='cache.db', suffix=None, row_type=None):
        super(CacheDB, self).__init__(filename, suffix, row_type)

    # Add new migrations at the bottom of the list; subclass the previous migration.
    class InitialSchema(SchemaUpgrade):

        def __init__(self, filename='cache.db', suffix=None, row_type=None):
            super(CacheDB.InitialSchema, self).__init__(filename, suffix, row_type)

        def test(self):
            return self.checkDBVersion() >= 1

        def execute(self, **kwargs):
            queries = [
                ("CREATE TABLE lastUpdate (provider TEXT, time NUMERIC);",),
                ("CREATE TABLE lastSearch (provider TEXT, time NUMERIC);",),
                (
                    "CREATE TABLE scene_exceptions (exception_id INTEGER PRIMARY KEY, indexer_id INTEGER KEY, show_name TEXT, season NUMERIC DEFAULT -1, custom NUMERIC DEFAULT 0);",),
                ("CREATE TABLE scene_names (indexer_id INTEGER, name TEXT);",),
                ("CREATE TABLE network_timezones (network_name TEXT PRIMARY KEY, timezone TEXT);",),
                ("CREATE TABLE scene_exceptions_refresh (list TEXT PRIMARY KEY, last_refreshed INTEGER);",),
                ("PRAGMA user_version = 1;",),
            ]

            for query in queries:
                if len(query) == 1:
                    self.action(query[0])
                else:
                    self.action(query[0], query[1:])

    class AddSceneExceptions(InitialSchema):
        def test(self):
            return self.hasTable("scene_exceptions")

        def execute(self, **kwargs):
            self.action(
                    "CREATE TABLE scene_exceptions (exception_id INTEGER PRIMARY KEY, indexer_id INTEGER KEY, show_name TEXT);")

    class AddSceneNameCache(AddSceneExceptions):
        def test(self):
            return self.hasTable("scene_names")

        def execute(self, **kwargs):
            self.action("CREATE TABLE scene_names (indexer_id INTEGER, name TEXT);")

    class AddNetworkTimezones(AddSceneNameCache):
        def test(self):
            return self.hasTable("network_timezones")

        def execute(self, **kwargs):
            self.action("CREATE TABLE network_timezones (network_name TEXT PRIMARY KEY, timezone TEXT);")

    class AddLastSearch(AddNetworkTimezones):
        def test(self):
            return self.hasTable("lastSearch")

        def execute(self, **kwargs):
            self.action("CREATE TABLE lastSearch (provider TEXT, time NUMERIC);")

    class AddSceneExceptionsSeasons(AddLastSearch):
        def test(self):
            return self.hasColumn("scene_exceptions", "season")

        def execute(self, **kwargs):
            self.addColumn("scene_exceptions", "season", "NUMERIC", -1)

    class AddSceneExceptionsCustom(AddSceneExceptionsSeasons):
        def test(self):
            return self.hasColumn("scene_exceptions", "custom")

        def execute(self, **kwargs):
            self.addColumn("scene_exceptions", "custom", "NUMERIC", 0)

    class AddSceneExceptionsRefresh(AddSceneExceptionsCustom):
        def test(self):
            return self.hasTable("scene_exceptions_refresh")

        def execute(self, **kwargs):
            self.action(
                    "CREATE TABLE scene_exceptions_refresh (list TEXT PRIMARY KEY, last_refreshed INTEGER);")
