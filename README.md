# Pemilu 2024 Data Scraper

This repository contains a Python program designed to scrape presidential election data for the Indonesian 2024 election. The program uses `aiohttp` and `asyncio` to perform asynchronous requests and organizes the data into a directory structure based on region (provinces, cities, districts, and TPS). Each TPS folder contains a CSV file with voter data for the presidential candidates.

## Features

- Fetches election data from the official KPU website.
- Creates a structured folder hierarchy for:
  - Provinces
  - Cities/Regencies
  - Districts
  - TPS (Polling Stations)
- Saves election data in CSV format for each TPS.
- Handles retries for failed requests.

## Prerequisites

Before running the program, ensure you have the following installed:

- Python 3.8+
- Required Python libraries:
  - `aiohttp`
  - `pandas`

You can install the required libraries using the command:

```bash
pip install aiohttp pandas
```

## How It Works

1. **Fetch Province Data:** The program retrieves the list of provinces.
2. **Fetch City Data:** For each province, it fetches the list of cities or regencies.
3. **Fetch District Data:** For each city, it fetches the list of districts.
4. **Fetch Village Data:** For each district, it fetches the list of villages.
5. **Fetch TPS Data:** For each village, it fetches polling station (TPS) data.
6. **Save Data:** TPS data is saved as a CSV file within its respective folder.

## Folder Structure

The program creates a timestamped directory structure as follows:

```
<timestamp>/
  <Province Name>/
    <City Name>/
      <District Name>/
        <Village Name>/
          TPS_<Number>.csv
```

Each CSV file contains the following information:
- Province, City, District, and Village names.
- TPS name and code.
- Candidate votes (`suara_01`, `suara_02`, `suara_03`).
- Additional administrative and polling data.

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pemilu-2024-data-scraper.git
   cd pemilu-2024-data-scraper
   ```

2. Run the program:
   ```bash
   python scraper.py
   ```

3. The data will be saved in a folder with the current timestamp.

## Configuration

The following constants can be adjusted in the code:

- `URL_PROV`: URL to fetch province data.
- `BASE_URL_WILAYAH`: Base URL for region data.
- `BASE_URL_TPS`: Base URL for TPS data.
- `WEB_URL`: URL for detailed TPS information.

## Error Handling

- The program retries up to 3 times for failed TPS data requests.
- In case of persistent failures, it logs an error and continues with the next TPS.

## Dependencies

- `aiohttp`: For asynchronous HTTP requests.
- `pandas`: For saving data in CSV format.

## Contribution

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.

