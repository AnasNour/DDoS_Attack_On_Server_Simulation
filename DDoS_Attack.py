import simpy
import random
import pygame
import matplotlib
import matplotlib.pyplot as plt

# Use Agg backend for Matplotlib to avoid Tkinter issues
matplotlib.use('Agg')

# Simulation Parameters
REQUEST_PROCESSING_TIME = 1  # Time to process one request (in seconds)
NORMAL_REQUEST_RATE = 2      # Increase time between normal client requests (lower load)
DDOS_REQUEST_RATE = 0.03     # Time between attacker requests
SERVER_CAPACITY = 10         # Maximum number of requests the server can process at once
SIMULATION_TIME = 300       # Total simulation time (seconds)
DDOS_ATTACK_START = 150      # Start the DDoS attack later in the simulation

# Tracking CPU load and dropped packets
cpu_load_over_time = []
dropped_packets_over_time = []

# Pygame visualization setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
FPS = 30

# Pygame Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)    # Normal clients
YELLOW = (255, 255, 0)  # Attackers
GREY = (128, 128, 128)  # Dropped clients

class Server:
    def __init__(self, env, capacity):
        self.env = env
        self.capacity = capacity
        self.queue = simpy.Resource(env, capacity=capacity)
        self.cpu_load = 0
        self.dropped_packets = 0

    def handle_request(self, request_type, sprite):
        with self.queue.request() as req:
            if not self.queue.count < self.capacity:  # Check if server is overloaded
                self.dropped_packets += 1
                sprite.image.fill(GREY)  # Change color to grey to indicate dropped request
                return
            yield req
            yield self.env.timeout(REQUEST_PROCESSING_TIME)  # Processing time for the request
            self.cpu_load = min(100, (self.queue.count / self.capacity) * 100)

    def get_stats(self):
        return self.cpu_load, self.dropped_packets

class ClientSprite(pygame.sprite.Sprite):
    """Represents a client or attacker in the 2D visualization."""
    def __init__(self, x, y, color, server):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.server = server

    def update(self):
        """Move towards the server and simulate sending a request."""
        target_x, target_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.rect.x += (target_x - self.rect.x) * 0.02
        self.rect.y += (target_y - self.rect.y) * 0.02

def normal_client(env, server, all_sprites):
    """A normal client that sends requests at a normal rate."""
    while True:
        yield env.timeout(random.expovariate(1.0 / NORMAL_REQUEST_RATE))
        # Add a new client sprite to the Pygame display
        client = ClientSprite(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), BLUE, server)
        all_sprites.add(client)
        env.process(server.handle_request('normal', client))

def ddos_attacker(env, server, all_sprites):
    """Simulates a DDoS attacker sending requests rapidly."""
    while True:
        yield env.timeout(random.expovariate(1.0 / DDOS_REQUEST_RATE))
        # Add a new attacker sprite to the Pygame display
        attacker = ClientSprite(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), YELLOW, server)
        all_sprites.add(attacker)
        env.process(server.handle_request('attack', attacker))

def monitor_server(env, server):
    """Monitor the CPU load and dropped packets."""
    while True:
        cpu_load, dropped_packets = server.get_stats()
        cpu_load_over_time.append((env.now, cpu_load))
        dropped_packets_over_time.append((env.now, dropped_packets))
        yield env.timeout(1)

def pygame_visualization(server, env):
    """Create a 2D visualization using Pygame."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    server_sprite = pygame.Rect(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30, 60, 60)

    # Create groups of sprites for clients and attackers
    all_sprites = pygame.sprite.Group()

    # Start normal clients in the visualization
    for i in range(3):  # Reduce number of normal clients
        env.process(normal_client(env, server, all_sprites))

    running = True
    while running and env.now < SIMULATION_TIME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update all sprites (clients/attackers moving towards the server)
        all_sprites.update()

        # Draw the background and server
        screen.fill(WHITE)

        # Draw the server (color depends on CPU load)
        cpu_load = server.cpu_load
        server_color = RED if cpu_load >= 80 else GREEN
        pygame.draw.rect(screen, server_color, server_sprite)

        # Draw all clients/attackers
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

        # Advance the simulation by 1 second
        env.run(until=env.now + 1)

        # Start DDoS attackers after attack time begins
        if env.now == DDOS_ATTACK_START:
            for _ in range(10):
                env.process(ddos_attacker(env, server, all_sprites))

    pygame.quit()

# Set up the simulation environment
env = simpy.Environment()
server = Server(env, SERVER_CAPACITY)

# Monitor server metrics
env.process(monitor_server(env, server))

# Run the SimPy simulation and Pygame visualization together
pygame_visualization(server, env)

# Plot the results after the simulation using the 'Agg' backend
times, cpu_loads = zip(*cpu_load_over_time)
plt.figure(figsize=(10, 5))
plt.plot(times, cpu_loads, label='CPU Load (%)')
plt.axvline(x=DDOS_ATTACK_START, color='red', linestyle='--', label='DDoS Attack Start')

# Set Times New Roman font and larger size for labels and title
plt.xlabel('Time (s)', fontsize=20, fontname='Times New Roman')
plt.ylabel('CPU Load (%)', fontsize=20, fontname='Times New Roman')
plt.title('Server CPU Load Over Time', fontsize=22, fontname='Times New Roman')
plt.legend(fontsize=16)
plt.grid(True)
plt.savefig('cpu_load_over_time.png')  # Save the plot as a PNG file

# Dropped Packets graph
times, dropped_packets = zip(*dropped_packets_over_time)
plt.figure(figsize=(10, 5))
plt.plot(times, dropped_packets, label='Dropped Packets')
plt.axvline(x=DDOS_ATTACK_START, color='red', linestyle='--', label='DDoS Attack Start')

# Set Times New Roman font and larger size for labels and title
plt.xlabel('Time (s)', fontsize=20, fontname='Times New Roman')
plt.ylabel('Dropped Packets', fontsize=20, fontname='Times New Roman')
plt.title('Dropped Packets Over Time', fontsize=22, fontname='Times New Roman')
plt.legend(fontsize=16)
plt.grid(True)
plt.savefig('dropped_packets_over_time.png')  # Save the plot as a PNG file
