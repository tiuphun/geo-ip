#!/usr/bin/env python3
"""
Taiwan Router Geolocation using MaxMind GeoIP2
Quick start script for initial IP geolocation
"""

import geoip2.database
import socket
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class RouterGeolocator:
    def __init__(self, mmdb_path: str = 'GeoLite2-City.mmdb'):
        """
        Initialize with MaxMind database
        
        Args:
            mmdb_path: Path to the .mmdb database file
        """
        try:
            self.reader = geoip2.database.Reader(mmdb_path)
            print(f"✓ Successfully loaded database: {mmdb_path}")
        except FileNotFoundError:
            print(f"✗ Database file not found: {mmdb_path}")
            print("\nDownload it with:")
            print("wget https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb")
            raise
        
        # Taiwan city code mappings for DNS analysis
        self.taiwan_codes = {
            'tpe': 'Taipei',
            'tpq': 'Taipei',
            'ntc': 'New Taipei',
            'ntpc': 'New Taipei',
            'tyn': 'Taoyuan',
            'ty': 'Taoyuan',
            'tcn': 'Taichung',
            'tc': 'Taichung',
            'txg': 'Taichung',
            'tnn': 'Tainan',
            'tn': 'Tainan',
            'khh': 'Kaohsiung',
            'kh': 'Kaohsiung',
            'hsc': 'Hsinchu',
            'hc': 'Hsinchu',
            'hch': 'Hsinchu',
            'hl': 'Hualien',
            'il': 'Yilan',
            'tt': 'Taitung',
            'nt': 'Nantou',
            'cy': 'Chiayi',
            'ml': 'Miaoli',
            'cl': 'Changhua',
            'yl': 'Yunlin',
            'pt': 'Pingtung',
        }
    
    def lookup_ip(self, ip_address: str) -> Dict:
        """
        Lookup single IP address in MaxMind database
        
        Returns:
            Dictionary with location information
        """
        result = {
            'ip': ip_address,
            'country': None,
            'city': None,
            'latitude': None,
            'longitude': None,
            'accuracy_radius': None,
            'postal_code': None,
            'subdivision': None,
            'isp': None,
            'hostname': None,
            'dns_hints': None,
            'confidence': None
        }
        
        # MaxMind lookup
        try:
            response = self.reader.city(ip_address)
            result['country'] = response.country.name
            result['city'] = response.city.name
            result['latitude'] = response.location.latitude
            result['longitude'] = response.location.longitude
            result['accuracy_radius'] = response.location.accuracy_radius
            result['postal_code'] = response.postal.code
            
            # Get subdivision (state/province)
            if response.subdivisions:
                result['subdivision'] = response.subdivisions.most_specific.name
                
        except geoip2.errors.AddressNotFoundError:
            result['error'] = 'IP not found in database'
        except Exception as e:
            result['error'] = str(e)
        
        # DNS reverse lookup
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            result['hostname'] = hostname
            result['dns_hints'] = self.extract_location_from_hostname(hostname)
        except (socket.herror, socket.gaierror):
            pass
        
        # Calculate confidence score
        result['confidence'] = self.calculate_confidence(result)
        
        return result
    
    def extract_location_from_hostname(self, hostname: str) -> Optional[str]:
        """
        Extract location hints from hostname using Taiwan city codes
        
        Args:
            hostname: Domain name or hostname
            
        Returns:
            Detected city name or None
        """
        hostname_lower = hostname.lower()
        
        # Check for Taiwan city codes
        for code, city in self.taiwan_codes.items():
            # Look for code as whole word or with delimiters
            pattern = rf'\b{code}\b|[-_.]{code}[-_.]|{code}\d'
            if re.search(pattern, hostname_lower):
                return city
        
        return None
    
    def calculate_confidence(self, result: Dict) -> str:
        """
        Calculate confidence level based on available data
        
        Returns:
            Confidence level: 'high', 'medium', 'low', 'none'
        """
        score = 0
        
        # Has coordinates
        if result['latitude'] and result['longitude']:
            score += 2
        
        # Has city name
        if result['city']:
            score += 2
        
        # Has DNS hostname
        if result['hostname']:
            score += 1
        
        # Has DNS location hints
        if result['dns_hints']:
            score += 2
        
        # Small accuracy radius (< 50km)
        if result['accuracy_radius'] and result['accuracy_radius'] < 50:
            score += 1
        
        if score >= 6:
            return 'high'
        elif score >= 4:
            return 'medium'
        elif score >= 2:
            return 'low'
        else:
            return 'none'
    
    def process_ip_list(self, ip_list: List[str], output_csv: str = 'router_locations.csv'):
        """
        Process list of IPs and save results to CSV
        
        Args:
            ip_list: List of IP addresses
            output_csv: Output filename
        """
        results = []
        
        print(f"\nProcessing {len(ip_list)} IP addresses...")
        print("-" * 60)
        
        for i, ip in enumerate(ip_list, 1):
            result = self.lookup_ip(ip)
            results.append(result)
            
            # Print progress
            status = "✓" if result.get('city') else "✗"
            city = result.get('city') or 'Not found'
            dns_hint = f" (DNS: {result['dns_hints']})" if result.get('dns_hints') else ""
            
            print(f"{status} [{i}/{len(ip_list)}] {ip:15s} → {city}{dns_hint}")
        
        # Save to CSV
        self.save_to_csv(results, output_csv)
        print(f"\n✓ Results saved to: {output_csv}")
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def save_to_csv(self, results: List[Dict], filename: str):
        """Save results to CSV file"""
        if not results:
            return
        
        fieldnames = ['ip', 'country', 'city', 'subdivision', 'latitude', 'longitude',
                     'accuracy_radius', 'postal_code', 'hostname', 'dns_hints', 
                     'confidence', 'error']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Only write fields that exist in fieldnames
                row = {k: v for k, v in result.items() if k in fieldnames}
                writer.writerow(row)
    
    def print_summary(self, results: List[Dict]):
        """Print summary statistics"""
        total = len(results)
        found = sum(1 for r in results if r.get('city'))
        with_dns = sum(1 for r in results if r.get('hostname'))
        with_hints = sum(1 for r in results if r.get('dns_hints'))
        
        confidence_counts = {
            'high': sum(1 for r in results if r.get('confidence') == 'high'),
            'medium': sum(1 for r in results if r.get('confidence') == 'medium'),
            'low': sum(1 for r in results if r.get('confidence') == 'low'),
            'none': sum(1 for r in results if r.get('confidence') == 'none')
        }
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total IPs processed:     {total}")
        print(f"Found in database:       {found} ({found/total*100:.1f}%)")
        print(f"With DNS hostname:       {with_dns} ({with_dns/total*100:.1f}%)")
        print(f"With location hints:     {with_hints} ({with_hints/total*100:.1f}%)")
        print(f"\nConfidence levels:")
        print(f"  High:    {confidence_counts['high']} ({confidence_counts['high']/total*100:.1f}%)")
        print(f"  Medium:  {confidence_counts['medium']} ({confidence_counts['medium']/total*100:.1f}%)")
        print(f"  Low:     {confidence_counts['low']} ({confidence_counts['low']/total*100:.1f}%)")
        print(f"  None:    {confidence_counts['none']} ({confidence_counts['none']/total*100:.1f}%)")
        
        # City distribution for Taiwan
        taiwan_results = [r for r in results if r.get('country') == 'Taiwan']
        if taiwan_results:
            cities = {}
            for r in taiwan_results:
                city = r.get('city') or 'Unknown'
                cities[city] = cities.get(city, 0) + 1
            
            print(f"\nTaiwan city distribution:")
            for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
                print(f"  {city:20s}: {count}")
    
    def __del__(self):
        """Close database reader"""
        if hasattr(self, 'reader'):
            self.reader.close()


def parse_router_file(filename: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse router file in the format:
       1. 140.123.103.250    csgate103.cs.ccu.edu.tw
       
    Returns:
        List of tuples: [(ip, hostname), ...]
    """
    routers = []
    ip_pattern = re.compile(r'^\s*\d+\.\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(.*)')


def parse_router_file(filename: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parse router file in the format:
       1. 140.123.103.250    csgate103.cs.ccu.edu.tw
       
    Returns:
        List of tuples: [(ip, hostname), ...]
    """
    routers = []
    ip_pattern = re.compile(r'^\s*\d+\.\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(.*)')

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            match = ip_pattern.match(line)
            if match:
                ip = match.group(1)
                hostname = match.group(2).strip() if match.group(2).strip() else None
                routers.append((ip, hostname))
    
    return routers


def main():
    """Example usage"""
    
    print("=" * 60)
    print("TAIWAN ROUTER GEOLOCATION - MAXMIND SETUP")
    print("=" * 60)
    
    # Initialize geolocator
    try:
        geolocator = RouterGeolocator('GeoLite2-City.mmdb')
    except FileNotFoundError:
        print("\n⚠ Please download the database first!")
        return
    
    # Check if router_ips.txt exists
    router_file = 'router_ips.txt'
    if Path(router_file).exists():
        print(f"\n✓ Found {router_file}")
        routers = parse_router_file(router_file)
        print(f"✓ Parsed {len(routers)} routers from file")
        
        # Extract just the IPs
        ip_list = [ip for ip, _ in routers]
        
        # Process IPs
        results = geolocator.process_ip_list(ip_list, output_csv='router_locations.csv')
        
    else:
        print(f"\n⚠ {router_file} not found!")
        print("Using sample IPs for demonstration...")
        
        # Example Taiwan router IPs
        sample_ips = [
            '1.34.0.1',        # Chunghwa Telecom
            '168.95.1.1',      # HiNet DNS
            '203.133.1.1',     # Taiwan Academic Network
        ]
        
        results = geolocator.process_ip_list(sample_ips)
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Check 'router_locations.csv' for detailed results")
    print("2. IPs with 'low' or 'none' confidence need refinement")
    print("3. Note the DNS hostname patterns for location hints")
    print("4. Proceed to active measurement phase for precision")


if __name__ == '__main__':
    main()
