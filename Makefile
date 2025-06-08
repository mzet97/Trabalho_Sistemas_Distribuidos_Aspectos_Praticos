CC          := gcc
CFLAGS      := -Wall -Wextra -O2
LDFLAGS     := -lrt

SERVER      := server_udp
CLIENT      := client_udp
CLIENT_RAMP := client_udp_ramp
MIN_SERVER  := min_server
MIN_CLIENT  := min_client

SRC_SERVER      := server_udp.c
SRC_CLIENT      := client_udp.c
SRC_CLIENT_RAMP := client_udp_ramp.c

.PHONY: all
all: $(SERVER) $(CLIENT) $(CLIENT_RAMP)

$(SERVER): $(SRC_SERVER)
	$(CC) $(CFLAGS) -o $@ $(SRC_SERVER)

$(CLIENT): $(SRC_CLIENT)
	$(CC) $(CFLAGS) -o $@ $(SRC_CLIENT) $(LDFLAGS)

$(CLIENT_RAMP): $(SRC_CLIENT_RAMP)
	$(CC) $(CFLAGS) -o $@ $(SRC_CLIENT_RAMP) $(LDFLAGS)

.PHONY: clean
clean:
	rm -f $(SERVER) $(CLIENT) $(CLIENT_RAMP)

.PHONY: distclean
distclean: clean
	rm -f raw_data_cliente*.csv stats_cliente*.csv ramp_data_cliente*.csv stats_ramp_cliente*.csv stats_ramp_aggregated_cliente*.csv
	rm -f rtt_vs_size_cliente*.png loss_rate_vs_size.png jitter_vs_size.png loss_rate_ramp.png percentiles_comparison.png outliers_histogram.png rtt_ramp_vs_level_cliente*.png
	rm -f tcpdump_raw_*.log tcpdump_analysis_*.log tcpdump_capture_*.pcap
