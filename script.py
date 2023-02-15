import CloudFlare
import yaml

# Load API Key from key.yml
with open('key.yml') as file:
    api_data = yaml.safe_load(file)
    api_key = api_data['api_key']
    zone_id = api_data['zone_id']

# Load CNAME DB Yaml file
with open('db\cnamedb.yml') as file:
    cname_db_data = yaml.safe_load(file)

# Load NS DB Yaml file
with open('db\dbns.yml') as file:
    ns_db_data = yaml.safe_load(file)

# Load Subdomain YAML file
with open('subdomain.yml') as file:
    yaml_data = yaml.safe_load(file)

# Get CNAME and NS records from YAML
cname_records = yaml_data.get('CNAME records', [])
ns_records = yaml_data.get('NS records', [])

# Set up Cloudflare API client
cf = CloudFlare.CloudFlare(email='', token=api_key)

# Loop through CNAME records and update or create them
for record in cname_records:
    record_type = record.get('type', 'CNAME')
    name = record['name']
    value = record['value']
    proxy = record.get('proxy', False)

    # Check if the record is reserved
    is_reserved = False
    for reserved_record in yaml_data['Reserved records']:
        if name == reserved_record['name']:
            print(f"{name} is a reserved name and cannot be modified")
            is_reserved = True
            break

    if is_reserved:
        continue

    # Check if the record already exists in the DB
    existing_record = None
    for record in cname_db_data.get(record_type + ' records', []):
        if name == record['name'] and value == record['value']:
            existing_record = record
            break

    # If the record already exists, skip it
    if existing_record:
        print(f"{name} already exists in the DNS records")
        continue

    # Otherwise, create the new record
    cf.zones.dns_records.post(zone_id, data={
        'type': record_type, 'name': name, 'content': value, 'proxied': proxy})

    # Add the new record to the DB
    cname_db_data.setdefault(record_type + ' records', []
                             ).append({'name': name, 'value': value})

    with open('db\cnamedb.yml', 'w') as file:
        yaml.dump(cname_db_data, file)

    print(f"record {name} created successfully")


# Loop through NS records and update or create them
for record in ns_records:
    record_type = record.get('type', 'NS')
    name = record['name']
    value = record['value']
    ttl = record.get('ttl', 14400)
    data = {'type': record_type, 'name': name, 'content': value, 'ttl': ttl}

    # Check if the record is reserved
    is_reserved = False
    for reserved_record in yaml_data['Reserved records']:
        if name == reserved_record['name']:
            print(f"{name} is a reserved name and cannot be modified")
            is_reserved = True
            break

    if is_reserved:
        continue

    # Check if the record already exists in the DB
    existing_record = None
    for record in ns_db_data.get(record_type + ' records', []):
        if name == record['name'] and value == record['value']:
            existing_record = record
            break

    # If the record already exists, skip it
    if existing_record:
        print(f"{name} already exists in the DNS records")
        continue

    # Otherwise, create the new record
    cf.zones.dns_records.post(zone_id, data=data)

    # Add the new record to the DB
    ns_db_data.setdefault(record_type + ' records', []
                          ).append({'name': name, 'value': value})

    with open('db\dbns.yml', 'w') as file:
        yaml.dump(ns_db_data, file)

    print(f"Record {name} created successfully")
