from influxdb import InfluxDBClient


INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'galaxy'
INFLUXDB_PASS = 'galaxy'
INFLUXDB_DB = 'galaxy'


client = InfluxDBClient(
    host=INFLUXDB_HOST,
    port=INFLUXDB_PORT,
    username=INFLUXDB_USER,
    password=INFLUXDB_PASS
)

client.create_database(INFLUXDB_DB)
client.switch_database(INFLUXDB_DB)

# Retention policies
#client.query(
#    "CREATE RETENTION POLICY a_month ON %s DURATION 30d REPLICATION 1"
#    % INFLUXDB_DB
#)
client.query(
    "CREATE RETENTION POLICY a_year ON %s DURATION 365d REPLICATION 1 DEFAULT"
    % INFLUXDB_DB
)

# Continuous queries
#client.query(
#    "DROP CONTINUOUS QUERY cq_search_criteria_per_day ON %s" % INFLUXDB_DB
#)
#
#client.query(
#    "CREATE CONTINUOUS QUERY cq_search_criteria_per_day ON %s "
#    "RESAMPLE EVERY 30m "
#    "BEGIN "
#    "SELECT count(value) AS value INTO search_criteria_per_day FROM a_month.search_criteria "
#    "GROUP BY time(1d), * "
#    "END"
#    % INFLUXDB_DB
#)
