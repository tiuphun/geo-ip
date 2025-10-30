# Taiwan Router Geolocation Tool

A Python-based geolocation tool for analyzing and mapping Taiwan router IP addresses using the MaxMind GeoLite2 database. This project extracts geographic information from IP addresses, performs DNS-based location inference, and provides visualization of city distribution across Taiwan.

## Features

- **IP Geolocation**: Uses MaxMind GeoLite2-City database for precise location mapping
- **DNS Hostname Analysis**: Extracts location hints from router hostnames using Taiwan city codes
- **Confidence Scoring**: Rates geolocation accuracy based on multiple factors
- **Batch Processing**: Efficiently processes large lists of IP addresses
- **CSV Export**: Generates detailed reports with coordinates, accuracy metrics, and metadata
- **Visualization**: Creates distribution charts showing geographic patterns across Taiwan cities

## Project Structure

```
geo-ip/
├── geolocate_routers.py      # Main geolocation script with batch processing
├── visualize.py               # Data visualization for city distribution
├── GeoLite2-City.mmdb         # MaxMind GeoIP2 database (63MB)
├── router_ips-1a.txt          # Router IP list (334 entries)
├── router_ips-1b.txt          # Router IP list (562 entries)
├── router_locations-1a.csv    # Geolocation results for dataset 1a
├── router_locations-1b.csv    # Geolocation results for dataset 1b
├── Figure_1.png               # Distribution visualization output
├── 1b-log.txt                 # Processing log for dataset 1b
└── venv/                      # Python virtual environment
```

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. **Clone or download the repository:**
   ```bash
   cd /path/to/geo-ip
   ```

2. **Set up Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install required dependencies:**
   ```bash
   pip install geoip2 matplotlib numpy
   ```

4. **Download the GeoLite2 database** (if not included):
   ```bash
   wget https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb
   ```

## Usage

### Geolocate IP Addresses

Process a list of router IPs and generate geolocation results:

```bash
python3 geolocate_routers.py
```

The script will:
- Read IP addresses from `router_ips.txt` (or use sample IPs)
- Perform MaxMind database lookups
- Execute reverse DNS lookups for hostname analysis
- Extract location hints from Taiwan city codes in hostnames
- Calculate confidence scores for each result
- Export results to `router_locations.csv`
- Print summary statistics

### Visualize Results

Generate distribution charts from the CSV data:

```bash
python3 visualize.py
```

This creates a horizontal bar chart showing the city distribution of IP addresses across Taiwan.

### Custom IP List Format

Create a `router_ips.txt` file with the following format:

```
   1. 140.123.103.250    csgate103.cs.ccu.edu.tw
   2. 211.22.226.198     211-22-226-198.caw1-3332.hinet.net
   3. 210.69.250.126     210-69-250-126.hinet-ip.hinet.net
```

## Output Format

### CSV Columns

The generated CSV file includes:

| Column | Description |
|--------|-------------|
| `ip` | IP address |
| `country` | Country name |
| `city` | City name |
| `subdivision` | State/province/county |
| `latitude` | Latitude coordinate |
| `longitude` | Longitude coordinate |
| `accuracy_radius` | Accuracy radius in kilometers |
| `postal_code` | Postal/ZIP code |
| `hostname` | Reverse DNS hostname |
| `dns_hints` | City extracted from hostname |
| `confidence` | Confidence level (high/medium/low/none) |
| `error` | Error message if lookup failed |

### Confidence Levels

- **High (6+ points)**: Precise coordinates, city name, DNS hints, accuracy < 50km
- **Medium (4-5 points)**: Coordinates and city, or strong DNS hints
- **Low (2-3 points)**: Basic location data available
- **None (0-1 points)**: Minimal or no location information

## Taiwan City Codes

The tool recognizes the following city codes in hostnames:

| Code | City |
|------|------|
| `tpe`, `tpq` | Taipei |
| `ntc`, `ntpc` | New Taipei |
| `ty`, `tyn` | Taoyuan |
| `tc`, `tcn`, `txg` | Taichung |
| `tn`, `tnn` | Tainan |
| `kh`, `khh` | Kaohsiung |
| `hc`, `hsc`, `hch` | Hsinchu |
| `hl` | Hualien |
| `il` | Yilan |
| `tt` | Taitung |

## Example Results

Based on the included datasets:

- **Total routers processed**: 334 (dataset 1a), 562 (dataset 1b)
- **Success rate**: ~80-90% found in database
- **Top locations**: Taipei, Taichung, New Taipei City, Taoyuan
- **Network providers**: HiNet, Taiwan Academic Network (TWAREN), SEED.NET

## API Reference

### `RouterGeolocator` Class

```python
from geolocate_routers import RouterGeolocator

# Initialize
geolocator = RouterGeolocator('GeoLite2-City.mmdb')

# Lookup single IP
result = geolocator.lookup_ip('140.112.0.69')

# Process batch
ip_list = ['140.112.0.69', '168.95.1.1']
results = geolocator.process_ip_list(ip_list, output_csv='output.csv')
```

### Key Methods

- `lookup_ip(ip_address)`: Geolocate a single IP address
- `process_ip_list(ip_list, output_csv)`: Batch process multiple IPs
- `extract_location_from_hostname(hostname)`: Parse location from DNS name
- `calculate_confidence(result)`: Compute confidence score

## Dependencies

- **geoip2**: MaxMind GeoIP2 Python API
- **matplotlib**: Visualization library
- **numpy**: Numerical computing (for visualizations)

## Data Sources

- **MaxMind GeoLite2**: Free geolocation database (requires periodic updates)
- **Router data**: Taiwan academic and commercial network infrastructure

## Limitations

- Accuracy depends on MaxMind database precision (typically 50-200km radius)
- DNS hostnames may not always contain location information
- Some IPs may return generic coordinates (24.0, 121.0) for Taiwan
- Private/internal IPs will not be found in the database

## License

This project uses the GeoLite2 database created by MaxMind, available from [https://www.maxmind.com](https://www.maxmind.com). Please review MaxMind's licensing terms for database usage.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional city code mappings
- Integration with other geolocation services
- Enhanced confidence scoring algorithms
- Real-time traceroute integration
- Web-based visualization dashboard

## Author
Tieu-Phuong Nguyen, TEEP Intern @CISLab Fall 2025 

National Chung Cheng University, Taiwan R.O.C.

## Acknowledgments

- MaxMind for the GeoLite2 database
- Taiwan Academic Network (TWAREN) for network infrastructure data
- HiNet and other ISPs for publicly accessible router information