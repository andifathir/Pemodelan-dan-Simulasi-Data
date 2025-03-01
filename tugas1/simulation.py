import simpy
import random

# Parameters
NUM_AGENTS = 3 # Number of agents available to fulfill orders
ARRIVAL_RATE = 5  # Average time between customer arrivals (in time units)
SERVICE_TIME = 10  # Average time to fulfill an order (in time units)

# Environment setup
env = simpy.Environment()

# Resource: agents available to fulfill orders
agents = simpy.Resource(env, capacity=NUM_AGENTS)

# Metrics tracking
waiting_times = []  # Track the waiting times of customers
agent_busy_times = [0] * NUM_AGENTS  # Track how much each agent is busy

# Customer process
def customer(env, name, agents):
    arrival_time = env.now
    print(f'{name} arrived at {arrival_time:.2f}')
    
    # Request an agent to fulfill the order
    with agents.request() as req:
        yield req
        service_start_time = env.now
        service_time = random.expovariate(1 / SERVICE_TIME)
        yield env.timeout(service_time)
        
        # Track the waiting time (time spent in the queue)
        waiting_time = service_start_time - arrival_time
        waiting_times.append(waiting_time)
        
        # Track the agent's busy time
        agent_id = agents.count - 1  # Identify which agent is serving
        agent_busy_times[agent_id] += service_time
        
        print(f'{name} finished at {env.now:.2f} after {service_time:.2f} time units (waited {waiting_time:.2f} units)')

# Generate customers
def generate_customers(env, agents):
    i = 0
    while True:
        i += 1
        yield env.timeout(random.expovariate(1 / ARRIVAL_RATE))  # Time between customer arrivals
        env.process(customer(env, f'Customer {i}', agents))

# Set up and run simulation
env.process(generate_customers(env, agents))  # Start the customer generation process
env.run(until=1000)  # Run the simulation for 100 time units

# Calculate average waiting time
avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0

# Calculate system utilization (agent busy time / total time)
total_busy_time = sum(agent_busy_times)
system_utilization = total_busy_time / (NUM_AGENTS * env.now)  # Total time agents were busy / total available time

# Output results
print("\nSimulation Results:")
print(f"Average Waiting Time: {avg_waiting_time:.2f} time units")
print(f"System Utilization: {system_utilization * 100:.2f}%")
