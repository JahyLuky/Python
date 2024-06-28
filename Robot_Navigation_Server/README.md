# Robot Navigation Server

## Project Overview
The Robot Navigation Server project involves creating a server that can authenticate and navigate multiple remote robots to the center of a coordinate system. Each robot starts from a random position and attempts to reach the [0,0] coordinate to retrieve a secret message. The server communicates with robots using a specific text-based protocol, handles obstacles, and manages various error scenarios.

## What I Learned

### Socket Programming
- **Socket Creation**: Understanding the basics of creating a server-client architecture using sockets in Python.
- **Communication Protocols**: Implementing a custom text-based protocol for communication between the server and robots.

### Networking
- **Concurrent Connections**: Managing multiple robot connections simultaneously using threading or asynchronous programming.
- **Handling Network Delays**: Ensuring robust communication even with potential network delays or message segmentation issues.

### Algorithms
- **Authentication Algorithm**: Implementing a two-way authentication process using predefined key pairs and hashing techniques.
- **Navigation Algorithm**: Developing an algorithm to navigate the robots to the target position [0,0], including obstacle detection and avoidance.

### Error Handling
- **Syntactic and Logical Errors**: Detecting and handling various errors in the communication protocol, such as syntax errors, logical errors, and timeouts.
- **Robust Protocol Implementation**: Creating a resilient protocol that can handle incomplete or concatenated messages and maintain correct operation.

### Optimization
- **Protocol Optimization**: Implementing optimizations to react quickly to invalid messages and minimize unnecessary processing.

## Project Structure

- `robot_navigation_server/`: Main project folder.
  - `server.py`: Main server implementation.
  - `client_simulator.py`: Client simulator for testing.
  - `keys.py`: Contains key pairs used for authentication.
  - `utils.py`: Utility functions for hashing and protocol handling.
  - `README.md`: Project overview and learnings (this file).

## Running the Project

1. **Setup**: Ensure Python is installed on your system.
2. **Start Server**: Run the server using the command `python server.py`.
3. **Simulate Clients**: Use the provided client simulator or run the tester to simulate robot clients.

## Testing

Use the provided tester script to validate the server implementation:
```bash
chmod +x tester
./tester 3999 localhost {test_number}
