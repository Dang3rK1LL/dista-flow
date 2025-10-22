import simpy, pandas as pd

def run_sim(line, trains, controller_map, dt=0.5, T=3600):
    """
    Run discrete-time simulation with improved finish detection
    """
    env = simpy.Environment()
    log = []
    finished_trains = set()  # Track which trains have finished

    def process(train, ctrl):
        while env.now < T:
            # Check if train has reached the end
            if train.pos_m >= line.total_m - 1.0:  # Within 1m of end
                if train.id not in finished_trains:
                    finished_trains.add(train.id)
                    print(f"Train {train.id} finished at t={env.now:.1f}s, pos={train.pos_m:.1f}m")
                # Log final position but don't continue simulation for this train
                log.append(dict(t=env.now, id=train.id, pos_m=train.pos_m, v=train.vel, finished=True))
                break
            
            # Find leader (trains ahead in position)
            potential_leaders = [t for t in trains if t.pos_m > train.pos_m and t.id != train.id]
            leader = min(potential_leaders, key=lambda x: x.pos_m) if potential_leaders else None
            
            # Get desired speed from controller
            v_des = ctrl.desired_speed(train, leader, line)
            
            # Update train state
            train.step(dt, v_des, line)
            
            # Log state
            log.append(dict(t=env.now, id=train.id, pos_m=train.pos_m, v=train.vel, finished=False))
            
            yield env.timeout(dt)

    # Start all train processes
    for tr in trains:
        env.process(process(tr, controller_map[tr.id]))
    
    env.run(until=T)
    
    print(f"Simulation completed. {len(finished_trains)} trains finished out of {len(trains)}")
    return pd.DataFrame(log)
