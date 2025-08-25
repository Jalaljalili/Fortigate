# FortiGate Memory Log Downloader & ELK Stack Visualizer

This project provides a complete solution for downloading user authentication logs from a FortiGate firewall's memory, parsing them, and visualizing the data using the Elastic (ELK) Stack. It's particularly useful for FortiGate devices that store logs only in memory and lack direct syslog VDOM support.

### 🌟 Features
* **Daily Log Retrieval**: A Python script (`download_logs.py`) automatically fetches yesterday's user authentication logs from the FortiGate API.
* **Log Parsing**: Logstash is configured to parse the key-value formatted logs into structured data.
* **ELK Stack**: A `docker-compose` file sets up a full ELK stack (Elasticsearch, Logstash, Kibana) for data processing, storage, and visualization.
* **Kibana Dashboards**: Visualize key metrics like daily logins, user activity, and geographical distribution of authentication attempts.
* **Persistent Storage**: Logs are saved to a local directory, ensuring a historical record is kept.

### 🛠️ Prerequisites
* Docker and Docker Compose
* A FortiGate firewall with API access enabled
* A FortiGate API token

### 🚀 Getting Started

#### 1. Configuration
1.  **FortiGate API**: Generate an API token on your FortiGate firewall.
2.  **`config.ini`**: In the `fortigate-log-downloader` directory, create a file named `config.ini` with your FortiGate details.

    ```ini
    [fortigate]
    url = https://<fortigate-ip-or-domain>
    token = <your-api-token>
    serial = <your-fortigate-serial-number>
    vdom = <vdom-name>
    ```

3.  **GeoIP Database**: Download the free GeoLite2 City database and place the `GeoLite2-City.mmdb` file in the project's root directory.

#### 2. Running the Stack
1.  **Build and Run**: From the project root, start the Docker containers.

    ```bash
    docker-compose up -d
    ```

2.  **Download Logs**: Run the Python script to fetch the logs. You can schedule this as a cron job to run daily.

    ```bash
    python3 fortigate-log-downloader/download_logs.py
    ```

3.  **Kibana**: Open Kibana at `http://localhost:5601`. Create an index pattern (`fortigate-logs-*`) and start building your visualizations!

### ⚙️ How It Works
* The `download_logs.py` script queries the FortiGate API to retrieve raw user event logs for the previous day.
* Filebeat monitors the `fortigate-log-downloader/logs` directory for new log files.
* Logstash ingests the logs from Filebeat, parses the key-value pairs using a `kv` filter, and enriches the data.
* Elasticsearch stores the structured log data in time-based indices.
* Kibana provides the visualization layer to create dashboards for monitoring and analysis.

## Excel Report ✅
 parses logs and writes a single Excel sheet with exactly:
* User
* Login_Count (number of auth-logon events)
* First_Login (earliest logon time)
* Last_Logout (latest logout time)



### 📄 License
This project is open-source and available under the MIT License.