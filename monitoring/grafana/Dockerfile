FROM grafana/grafana:9.3.0

# Create configuration directories
RUN mkdir -p /etc/grafana/provisioning/datasources && \
    mkdir -p /etc/grafana/provisioning/dashboards && \
    mkdir -p /var/lib/grafana/dashboards

# Extract the provisioning configuration from the ConfigMap in grafana-k8s.yaml
COPY grafana-k8s.yaml /tmp/grafana-k8s.yaml

# Use sed to extract datasources.yaml and dashboards.yaml from the ConfigMap
RUN sed -n '/datasources.yaml:/,/dashboards.yaml:/p' /tmp/grafana-k8s.yaml | \
    grep -v "datasources.yaml:" | \
    grep -v "dashboards.yaml:" | \
    sed 's/^    //' > /etc/grafana/provisioning/datasources/datasources.yaml && \
    sed -n '/dashboards.yaml:/,/---/p' /tmp/grafana-k8s.yaml | \
    grep -v "dashboards.yaml:" | \
    grep -v "---" | \
    sed 's/^    //' > /etc/grafana/provisioning/dashboards/dashboards.yaml

# Extract the dashboard JSON from the ConfigMap
RUN mkdir -p /etc/grafana/dashboards && \
    sed -n '/ml-metrics-dashboard.json:/,/EOF/p' /tmp/grafana-k8s.yaml | \
    grep -v "ml-metrics-dashboard.json:" | \
    grep -v "EOF" | \
    sed 's/^    //' > /etc/grafana/dashboards/ml-metrics-dashboard.json && \
    # Clean up temporary file
    rm /tmp/grafana-k8s.yaml

# Configure Grafana environment variables
ENV GF_SECURITY_ADMIN_USER=admin
ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_USERS_ALLOW_SIGN_UP=false
ENV GF_INSTALL_PLUGINS=grafana-piechart-panel

# Expose the Grafana port
EXPOSE 3000

# No need to specify entrypoint or CMD as they're already set in the base image 