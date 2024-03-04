/**
 * @file device.cpp
 * @author Emerson Shoichet-Bartus (e.shoichet-bartus@berkeley.edu)
 * @brief 
 * @version 1.0
 * @date 2023-04-21
 * 
 * @copyright Copyright (c) 2023
 * 
 */

#include <iostream>
#include <netinet/in.h>
#include <vector>
#include <sstream>
#include <math.h>
#include <thread>
#include "device.hpp"
#include <future>
#include <unistd.h>

#define MAXBUFFER 100
#define ADDR "50.50.50.50"

using namespace std;

Device::Device(const int port, const string model, const string serial) {
	
	PORT = port;
	MODEL = model;
	SERIAL = serial;

	// Creating socket file descriptor
	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		std::cout << "socket creation failed" << endl;
		exit(EXIT_FAILURE);
	}
	
	memset(&device_addr, 0, sizeof(device_addr));
	memset(&window_addr, 0, sizeof(window_addr));
	
	// Filling server information
	device_addr.sin_family = AF_INET; // IPv4
	device_addr.sin_addr.s_addr = INADDR_ANY;//inet_addr(ADDR);
	device_addr.sin_port = htons(PORT);
	
	bind(sockfd, (const struct sockaddr *)&device_addr, sizeof(device_addr));

	len = sizeof(window_addr); //len is value/result
	test_running = false;

	cout << "Started device at port " << PORT << endl;
	cout << "Listening closely..." << endl;
	listen();
}

void Device::listen() {
	while (true) {
		ssize_t msg_len = recvfrom(sockfd, (char *) buffer, MAXBUFFER, 0, (struct sockaddr *) &window_addr, &len);
		buffer[msg_len] = '\0';

		string message(buffer, msg_len);
		cout << "Received: " << message << endl;
		string cmd;
		int duration, rate;
		stringstream ss(message);
		vector<string> commands;
		while (getline(ss, cmd, ';')) {
			commands.push_back(cmd);
		}
		if (commands[0] == "ID") {
			send("ID;MODEL=" + MODEL + ";SERIAL=" + SERIAL + ";");
		} else if (commands[0] == "TEST") {
			if (commands[1] == "CMD=START") {
				if (!test_running) {
					send("TEST;RESULT=STARTED");
					continue_test = true;
					duration = stoi(commands[2].substr(9)); //starting after DURATION=
					rate = stoi(commands[3].substr(5)); //starting after RATE=

					//thread test(start_test, (duration, rate));
					//test.detach();
					run_test(duration, rate);
					test_running = true;
				} else if (test_running) {
					send("TEST;RESULT=error;MSG='Test already in progress';");
				}
			} else if (commands[1] == "CMD=STOP") {
				if (!test_running) {
					send("TEST;RESULT=error;MSG='No test to stop!';");
				} else if (test_running) {
					send("TEST;RESULT=STOPPED;");
					send("STATUS;STATE=IDLE;");
					test_running = false;
				}
			}
		}
	}
}

void Device::send(string response) {
	char* response_array = new char[response.length()+1];
	strcpy(response_array, response.c_str());
	sendto(sockfd, (const char *)response_array, strlen(response_array), 0, (const struct sockaddr *) &window_addr, len);
}

void Device::run_test(int duration, int rate) {
	int length = floor((duration*1000)/rate);
	for (int i = 0; i < length; i++) {
		if (!continue_test) {
			break;
		}
		ms = i*rate;
		mV = rand()%105 + 95;
		mA = rand()%205 + 195;
		send("STATUS;TIME=" + to_string(ms) + ";MV=" + to_string(mV) + ";MA=" + to_string(mA) + ";");
		sleep(rate/1000);
	}
	send("STATUS;STATE=IDLE;");
	test_running = false;
}

int main(int argc, char* argv[]) {
	if (argc != 2) {
		cout << "Usage: ./device [port]" << endl;
		return 0;
	}

	const string TEST_MODEL = "1.0";
	const string TEST_SERIAL = "7324XX";
	const int port = stoi(argv[1]);
	Device device(port, TEST_MODEL, TEST_SERIAL);

	return 0;
}