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
SRC_MIN_SERVER  := min_server.c
SRC_MIN_CLIENT  := min_client.c

.PHONY: all
all: $(SERVER) $(CLIENT) $(CLIENT_RAMP) $(MIN_SERVER) $(MIN_CLIENT)

$(SERVER): $(SRC_SERVER)
	$(CC) $(CFLAGS) -o $@ $(SRC_SERVER)

$(CLIENT): $(SRC_CLIENT)
	$(CC) $(CFLAGS) -o $@ $(SRC_CLIENT) $(LDFLAGS)

$(CLIENT_RAMP): $(SRC_CLIENT_RAMP)
	$(CC) $(CFLAGS) -o $@ $(SRC_CLIENT_RAMP) $(LDFLAGS)

$(MIN_SERVER): $(SRC_MIN_SERVER)
	$(CC) $(CFLAGS) -o $@ $(SRC_MIN_SERVER)

$(MIN_CLIENT): $(SRC_MIN_CLIENT)
	$(CC) $(CFLAGS) -o $@ $(SRC_MIN_CLIENT) $(LDFLAGS)

.PHONY: clean
clean:
	rm -f $(SERVER) $(CLIENT) $(CLIENT_RAMP) $(MIN_SERVER) $(MIN_CLIENT)

.PHONY: distclean
distclean: clean
	rm -f raw_data_cliente*.csv stats_cliente*.csv ramp_data_cliente*.csv rtt_vs_size_cliente*.png
