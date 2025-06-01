CC        := gcc
CFLAGS    := -Wall -Wextra -O2
LDFLAGS   := -lrt

SERVER    := server_udp
CLIENT    := client_udp
CLIENT_RAMP := client_udp_ramp

SRC_SERVER       := server_udp.c
SRC_CLIENT       := client_udp.c
SRC_CLIENT_RAMP  := client_udp_ramp.c

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
	rm -f raw_data_cliente*.csv stats_cliente*.csv ramp_data_cliente*.csv rtt_vs_size_cliente*.png

