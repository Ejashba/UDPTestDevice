/**
 * @file device.hpp
 * @author Emerson Shoichet-Bartus (e.shoichet-bartus@berkeley.edu)
 * @brief header for device
 * @version 1.0
 * @date 2023-04-21
 * 
 * @copyright Copyright (c) 2023
 * 
 */

#define MAXBUFFER 100
#include <thread>

using namespace std;

class Device {
	public:
		Device(int, string, string);
	private:
		void listen();
		void send(string);
		void run_test(int, int);
		//void *start_test(int, int);
		int sockfd;
		char buffer[MAXBUFFER];
		struct sockaddr_in device_addr, window_addr;
		socklen_t len;
		bool test_running;
		bool continue_test;
		int PORT;
		string MODEL;
		string SERIAL;
		int ms;
		float mV, mA;
		thread test;
};